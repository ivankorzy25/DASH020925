import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models import User, UserRole
import jwt

class AuthService:
    """Service for handling authentication and authorization"""
    
    def __init__(self, db: Session):
        self.db = db
        self.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
        self.token_expiry_minutes = int(os.getenv("TOKEN_EXPIRY_MINUTES", "1440"))  # 24 hours default
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with a salt"""
        salt = os.getenv("PASSWORD_SALT", "fallback-salt-change-in-production")
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.hash_password(password) == hashed_password
    
    def create_user(self, username: str, password: str, role: UserRole, email: Optional[str] = None) -> User:
        """Create a new user"""
        # Check if username already exists
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError("Username already exists")
        
        # Create user
        user = User(
            username=username,
            password_hash=self.hash_password(password),
            role=role,
            email=email,
            is_active=True,
            created_at=datetime.now()
        )
        
        self.db.add(user)
        self.db.commit()
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user and return the user object if successful"""
        user = self.db.query(User).filter(User.username == username, User.is_active == True).first()
        if not user:
            # Return None instead of raising exception for easier handling
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def generate_token(self, user: User) -> str:
        """Generate a JWT token for a user"""
        payload = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(minutes=self.token_expiry_minutes)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a JWT token and return the payload if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        return self.db.query(User).filter(User.username == username, User.is_active == True).first()
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change a user's password"""
        if not self.verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = self.hash_password(new_password)
        user.updated_at = datetime.now()
        self.db.commit()
        
        return True
