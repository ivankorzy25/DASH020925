#!/usr/bin/env python3
import os
import sys
from alembic.config import Config
from alembic import command
from app.database import init_db, SessionLocal
from app.models import Product, Media, PriceList
import argparse

def run_alembic_command(command_name, *args):
    """Run alembic command with proper configuration"""
    alembic_cfg = Config("alembic.ini")
    getattr(command, command_name)(alembic_cfg, *args)

def init_database():
    """Initialize database tables"""
    init_db()
    print("Database tables created successfully")

def create_migration(message):
    """Create new migration"""
    run_alembic_command("revision", "--autogenerate", "-m", message)
    print(f"Migration created: {message}")

def upgrade_database(revision="head"):
    """Upgrade database to specified revision"""
    run_alembic_command("upgrade", revision)
    print(f"Database upgraded to revision: {revision}")

def downgrade_database(revision):
    """Downgrade database to specified revision"""
    run_alembic_command("downgrade", revision)
    print(f"Database downgraded to revision: {revision}")

def seed_database():
    """Seed database with sample data"""
    db = SessionLocal()
    try:
        # Create sample products
        sample_products = [
            Product(sku="PROD001", name="Sample Product 1", price=19.99),
            Product(sku="PROD002", name="Sample Product 2", price=29.99),
        ]
        
        db.add_all(sample_products)
        db.commit()
        print("Sample data seeded successfully")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init command
    subparsers.add_parser("init", help="Initialize database tables")
    
    # Create migration command
    migrate_parser = subparsers.add_parser("migrate", help="Create new migration")
    migrate_parser.add_argument("message", help="Migration message")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    
    # Seed command
    subparsers.add_parser("seed", help="Seed database with sample data")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_database()
    elif args.command == "migrate":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_database(args.revision)
    elif args.command == "downgrade":
        downgrade_database(args.revision)
    elif args.command == "seed":
        seed_database()
    else:
        parser.print_help()
