from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import Product, PriceList, PriceItem
from app.services.audit_service import audit_log
import datetime
import csv
import io

class PriceService:
    """Service for managing prices and price imports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def import_prices_from_csv(
        self,
        csv_data: str,
        price_list_name: str,
        source: str,
        imported_by: str
    ) -> Dict:
        """Import prices from CSV data and return diff report"""
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_data))
        imported_prices = {}
        
        for row in reader:
            sku = row.get('sku', '').strip()
            price_str = row.get('price', '').strip()
            
            if not sku or not price_str:
                continue
            
            try:
                price = float(price_str)
                imported_prices[sku] = price
            except ValueError:
                continue
        
        # Get current prices for comparison
        current_products = self.db.query(Product).filter(
            Product.sku.in_(list(imported_prices.keys()))
        ).all()
        
        current_prices = {p.sku: p.price for p in current_products}
        
        # Prepare diff report
        diff_report = {
            'new_skus': [],
            'updated_prices': [],
            'unchanged': [],
            'invalid_skus': []
        }
        
        for sku, new_price in imported_prices.items():
            current_price = current_prices.get(sku)
            
            if current_price is None:
                diff_report['new_skus'].append({
                    'sku': sku,
                    'new_price': new_price
                })
            elif current_price != new_price:
                diff_report['updated_prices'].append({
                    'sku': sku,
                    'current_price': current_price,
                    'new_price': new_price,
                    'difference': new_price - current_price
                })
            else:
                diff_report['unchanged'].append({
                    'sku': sku,
                    'price': new_price
                })
        
        # Check for invalid SKUs (in CSV but not in database)
        all_skus = {p.sku for p in current_products}
        invalid_skus = set(imported_prices.keys()) - all_skus
        diff_report['invalid_skus'] = list(invalid_skus)
        
        return diff_report
    
    def apply_price_changes(
        self,
        price_changes: List[Dict],
        price_list_name: str,
        source: str,
        applied_by: str
    ) -> PriceList:
        """Apply price changes and create price list"""
        
        # Create price list
        price_list = PriceList(
            name=price_list_name,
            source=source,
            created_at=datetime.datetime.now()
        )
        
        self.db.add(price_list)
        self.db.flush()
        
        # Apply changes and create price items
        for change in price_changes:
            sku = change['sku']
            new_price = change['new_price']
            
            # Update product price
            product = self.db.query(Product).filter(Product.sku == sku).first()
            if product:
                old_price = product.price
                product.price = new_price
                product.updated_at = datetime.datetime.now()
                
                # Create price item
                price_item = PriceItem(
                    price_list_id=price_list.id,
                    sku=sku,
                    price=new_price,
                    currency=product.currency,
                    effective_from=datetime.datetime.now(),
                    notes=f"Price change from {old_price} to {new_price}"
                )
                
                self.db.add(price_item)
                
                # Audit log
                audit_log(
                    self.db,
                    entity="product",
                    entity_id=product.id,
                    action="price_update",
                    payload={
                        "sku": sku,
                        "old_price": old_price,
                        "new_price": new_price
                    },
                    actor=applied_by
                )
        
        self.db.commit()
        
        # Audit log for price list
        audit_log(
            self.db,
            entity="price_list",
            entity_id=price_list.id,
            action="create",
            payload={
                "name": price_list_name,
                "source": source,
                "changes_count": len(price_changes)
            },
            actor=applied_by
        )
        
        return price_list
    
    def get_price_history(self, sku: str, limit: int = 50) -> List[PriceItem]:
        """Get price history for a product"""
        return self.db.query(PriceItem).join(PriceList).filter(
            PriceItem.sku == sku
        ).order_by(PriceItem.effective_from.desc()).limit(limit).all()
