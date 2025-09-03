#!/usr/bin/env python3
from app.database import Base, engine
from app.models import *  # Importar todos los modelos

def upgrade_database():
    """
    Crea todas las tablas definidas en los modelos de la aplicación.
    Este método es idempotente y seguro de ejecutar múltiples veces.
    """
    print("Creando/actualizando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas de la base de datos listas.")

if __name__ == "__main__":
    # Este script se puede ejecutar directamente para inicializar la DB,
    # pero está pensado para ser llamado desde otros scripts de inicialización.
    upgrade_database()
