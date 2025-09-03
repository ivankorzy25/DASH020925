from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import datetime

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class ProductStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    HTML = "html"
    OTHER = "other"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    media_items = relationship("Media", back_populates="product")
    price_items = relationship("PriceItem", back_populates="product")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    type = Column(Enum(MediaType), nullable=False)
    title = Column(String(200), nullable=False)
    file_name = Column(String(500), nullable=False)
    storage_bucket = Column(String(200), nullable=False)
    storage_path = Column(String(500), nullable=False)
    public_url = Column(String(1000), nullable=True)
    size_bytes = Column(Integer, nullable=False)
    checksum = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    current_version_id = Column(Integer, ForeignKey("media_versions.id"), nullable=True)

    product = relationship("Product", back_populates="media_items")
    versions = relationship("MediaVersion", back_populates="media")

class MediaVersion(Base):
    __tablename__ = "media_versions"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    version = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    public_url = Column(String(1000), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    media = relationship("Media", back_populates="versions")

class PriceList(Base):
    __tablename__ = "price_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    source = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    price_items = relationship("PriceItem", back_populates="price_list")

class PriceItem(Base):
    __tablename__ = "price_items"

    id = Column(Integer, primary_key=True, index=True)
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    sku = Column(String(50), ForeignKey("products.sku"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text)

    price_list = relationship("PriceList", back_populates="price_items")
    product = relationship("Product", back_populates="price_items")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    payload_json = Column(Text, nullable=False)
    actor = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
