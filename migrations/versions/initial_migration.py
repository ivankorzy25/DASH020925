"""Initial migration

Revision ID: initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Bind the Alembic op object to a connection
    connection = op.get_bind()

    # --- Idempotent ENUM creation for 'productstatus' ---
    result = connection.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'productstatus')")).scalar()
    if not result:
        product_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'DRAFT', name='productstatus')
        product_status_enum.create(connection)
    product_status = sa.Enum('ACTIVE', 'INACTIVE', 'DRAFT', name='productstatus', create_type=False)

    # --- Idempotent ENUM creation for 'mediatype' ---
    result = connection.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mediatype')")).scalar()
    if not result:
        media_type_enum = sa.Enum('IMAGE', 'VIDEO', 'AUDIO', 'PDF', 'HTML', 'OTHER', name='mediatype')
        media_type_enum.create(connection)
    media_type = sa.Enum('IMAGE', 'VIDEO', 'AUDIO', 'PDF', 'HTML', 'OTHER', name='mediatype', create_type=False)

    # --- Idempotent ENUM creation for 'userrole' ---
    result = connection.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')")).scalar()
    if not result:
        user_role_enum = sa.Enum('ADMIN', 'EDITOR', 'VIEWER', name='userrole')
        user_role_enum.create(connection)
    user_role = sa.Enum('ADMIN', 'EDITOR', 'VIEWER', name='userrole', create_type=False)

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('status', product_status, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)

    # Create media table
    op.create_table('media_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('public_url', sa.String(length=1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_media_versions_id'), 'media_versions', ['id'], unique=False)

    op.create_table('media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('type', media_type, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('storage_bucket', sa.String(length=200), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('public_url', sa.String(length=1000), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=100), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_by', sa.String(length=100), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], )
    )
    op.create_index(op.f('ix_media_id'), 'media', ['id'], unique=False)

    # Add foreign keys separately to avoid circular dependency
    op.create_foreign_key(
        "fk_media_versions_media_id", "media_versions",
        "media", ["media_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_media_current_version_id", "media",
        "media_versions", ["current_version_id"], ["id"]
    )

    # Create price_lists table
    op.create_table('price_lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('source', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_price_lists_id'), 'price_lists', ['id'], unique=False)

    # Create price_items table
    op.create_table('price_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('price_list_id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('effective_from', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['price_list_id'], ['price_lists.id'], ),
        sa.ForeignKeyConstraint(['sku'], ['products.sku'], )
    )
    op.create_index(op.f('ix_price_items_id'), 'price_items', ['id'], unique=False)

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_id'), 'audit_log', ['id'], unique=False)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('role', user_role, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade():
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE userrole')
    
    op.drop_index('ix_audit_log_id', table_name='audit_log')
    op.drop_table('audit_log')
    
    op.drop_index('ix_price_items_id', table_name='price_items')
    op.drop_table('price_items')
    
    op.drop_index('ix_price_lists_id', table_name='price_lists')
    op.drop_table('price_lists')
    
    op.drop_index('ix_media_versions_id', table_name='media_versions')
    op.drop_table('media_versions')
    
    op.drop_index('ix_media_id', table_name='media')
    op.drop_table('media')
    
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')
    
    op.execute('DROP TYPE productstatus')
    op.execute('DROP TYPE mediatype')
