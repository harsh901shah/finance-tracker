#!/usr/bin/env python3
"""
Database Migration Script

This script migrates data from JSON files to the SQLite database.
"""

import os
import json
from services.database_service import DatabaseService

def migrate_data():
    """Migrate data from JSON files to the database"""
    print("Starting migration to database...")
    
    # Initialize database
    DatabaseService.initialize_database()
    print("Database initialized.")
    
    # Import data from JSON files
    DatabaseService.import_json_data()
    print("Data imported to database.")
    
    # Backup original JSON files
    backup_json_files()
    print("Original JSON files backed up.")
    
    print("Migration completed successfully!")

def backup_json_files():
    """Backup original JSON files"""
    json_files = ['transactions.json', 'networth.json', 'budget.json']
    
    for file in json_files:
        if os.path.exists(file):
            backup_file = f"{file}.bak"
            try:
                with open(file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                print(f"Backed up {file} to {backup_file}")
            except Exception as e:
                print(f"Error backing up {file}: {e}")

if __name__ == "__main__":
    migrate_data()