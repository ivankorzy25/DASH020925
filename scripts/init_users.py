#!/usr/bin/env python3
import os
import sys
from app.database import SessionLocal
from app.services.auth_service import AuthService

def init_users():
    """Initialize default users"""
    db = SessionLocal()
    auth_service = AuthService(db)
    
    # Create default users if they don't exist
    default_users = [
        {"username": "admin", "password": "admin123", "role": "admin", "email": "admin@example.com"},
        {"username": "editor", "password": "editor123", "role": "editor", "email": "editor@example.com"},
        {"username": "viewer", "password": "viewer123", "role": "viewer", "email": "viewer@example.com"},
    ]
    
    for user_data in default_users:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            try:
                auth_service.create_user(
                    user_data["username"],
                    user_data["password"],
                    UserRole[user_data["role"].upper()],
                    user_data["email"]
                )
                print(f"Created user: {user_data['username']}")
            except Exception as e:
                print(f"Error creating user {user_data['username']}: {e}")
        else:
            print(f"User already exists: {user_data['username']}")
    
    db.close()
    print("User initialization completed")

if __name__ == "__main__":
    from app.models import User, UserRole
    init_users()
