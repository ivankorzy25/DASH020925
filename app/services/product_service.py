from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Product, ProductStatus
from app.services.audit_service import audit_log
import datetime

class ProductService:
    """Service for managing products"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(
        self,
        sku: str,
        name: str,
        price: float,
        currency: str = "USD",
        description: Optional[str] = None,
        status: ProductStatus = ProductStatus.ACTIVE,
        created_by: str = "system"
    ) -> Product:
        """Create a new product"""
        # Check if SKU already exists
        existing_product = self.db.query(Product).filter(Product.sku == sku).first()
        if existing_product:
            raise ValueError(f"Product with SKU {sku} already exists")
        
        # Create product
        product = Product(
            sku=sku,
            name=name,
            description=description,
            price=price,
            currency=currency,
            status=status,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        self.db.add(product)
        self.db.commit()
        
        # Audit log
        audit_log(
            self.db,
            entity="product",
            entity_id=product.id,
            action="create",
            payload={
                "sku": sku,
                "name": name,
                "price": price,
                "currency": currency
            },
            actor=created_by
        )
        
        return product
    
    def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        currency: Optional[str] = None,
        status: Optional[str] = None,
        updated_by: str = "system"
    ) -> Product:
        """Update a product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Track changes for audit log
        changes = {}
        
        if name is not None and product.name != name:
            changes["name"] = {"old": product.name, "new": name}
            product.name = name
        
        if description is not None and product.description != description:
            changes["description"] = {"old": product.description, "new": description}
            product.description = description
        
        if price is not None and product.price != price:
            changes["price"] = {"old": product.price, "new": price}
            product.price = price
        
        if currency is not None and product.currency != currency:
            changes["currency"] = {"old": product.currency, "new": currency}
            product.currency = currency
        
        if status is not None and product.status.value != status:
            changes["status"] = {"old": product.status.value, "new": status}
            product.status = ProductStatus(status)
        
        if changes:
            product.updated_at = datetime.datetime.now()
            self.db.commit()
            
            # Audit log
            audit_log(
                self.db,
                entity="product",
                entity_id=product_id,
                action="update",
                payload={"changes": changes},
                actor=updated_by
            )
        
        return product
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU"""
        return self.db.query(Product).filter(Product.sku == sku).first()
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        return self.db.query(Product).order_by(Product.created_at.desc()).all()
    
    def delete_product(self, product_id: int, deleted_by: str = "system") -> bool:
        """Delete a product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        # Audit log before deletion
        audit_log(
            self.db,
            entity="product",
            entity_id=product_id,
            action="delete",
            payload={
                "sku": product.sku,
                "name": product.name
            },
            actor=deleted_by
        )
        
        self.db.delete(product)
        self.db.commit()
        
        return True
