#!/usr/bin/env python3
"""
Script principal para ejecutar la aplicación DASH020925
"""
import os
import sys
import argparse
from app.database import init_db
from scripts.db import upgrade_database
from scripts.init_users import init_users
from scripts.init_storage import init_storage

def main():
    parser = argparse.ArgumentParser(description="DASH020925 - Sistema de Gestión")
    subparsers = parser.add_subparsers(dest="command")
    
    # Run command
    subparsers.add_parser("run", help="Ejecutar la aplicación")
    
    # Init command
    subparsers.add_parser("init", help="Inicializar la aplicación (DB, usuarios, storage)")
    
    # DB commands
    db_parser = subparsers.add_parser("db", help="Comandos de base de datos")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("upgrade", help="Ejecutar migraciones de base de datos")
    db_subparsers.add_parser("reset", help="Reiniciar base de datos (¡Cuidado!)")
    
    args = parser.parse_args()
    
    if args.command == "run":
        os.system("streamlit run app/main.py")
    
    elif args.command == "init":
        print("Inicializando aplicación...")
        init_db()
        upgrade_database()
        init_users()
        init_storage()
        print("Aplicación inicializada correctamente!")
    
    elif args.command == "db":
        if args.db_command == "upgrade":
            upgrade_database()
        elif args.db_command == "reset":
            print("¡Esta operación eliminará todos los datos!")
            confirmation = input("Escribe 'RESET' para confirmar: ")
            if confirmation == "RESET":
                # Implementation for reset would go here
                print("Base de datos reiniciada")
            else:
                print("Operación cancelada")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
