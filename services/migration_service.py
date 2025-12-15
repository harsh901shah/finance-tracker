"""
Database migration service for schema changes
"""
import sqlite3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MigrationService:
    """Handles database schema migrations"""
    
    DB_FILE = 'finance_tracker.db'
    
    @classmethod
    def get_connection(cls):
        """Get database connection"""
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    
    @classmethod
    def initialize_migrations_table(cls):
        """Create migrations tracking table"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def is_migration_applied(cls, version: str) -> bool:
        """Check if migration version is already applied"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM schema_migrations WHERE version = ?', (version,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    @classmethod
    def apply_migration(cls, version: str, migration_sql: str):
        """Apply a migration and record it"""
        if cls.is_migration_applied(version):
            logger.info(f"Migration {version} already applied, skipping")
            return
        
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            # Execute migration
            cursor.executescript(migration_sql)
            
            # Record migration
            cursor.execute(
                'INSERT INTO schema_migrations (version) VALUES (?)', 
                (version,)
            )
            
            conn.commit()
            logger.info(f"Applied migration {version}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to apply migration {version}: {e}")
            raise
        finally:
            conn.close()
    
    @classmethod
    def run_all_migrations(cls):
        """Run all pending migrations"""
        cls.initialize_migrations_table()
        
        migrations = [
            {
                'version': '001_add_user_id_columns',
                'sql': '''
                -- Add user_id to transactions if not exists
                ALTER TABLE transactions ADD COLUMN user_id TEXT DEFAULT 'default_user';
                
                -- Add user_id to budget if not exists  
                ALTER TABLE budget ADD COLUMN user_id TEXT DEFAULT 'default_user';
                
                -- Add user_id to assets if not exists
                ALTER TABLE assets ADD COLUMN user_id TEXT DEFAULT 'default_user';
                
                -- Add user_id to liabilities if not exists
                ALTER TABLE liabilities ADD COLUMN user_id TEXT DEFAULT 'default_user';
                
                -- Add user_id to real_estate if not exists
                ALTER TABLE real_estate ADD COLUMN user_id TEXT DEFAULT 'default_user';
                '''
            },
            {
                'version': '002_normalize_payment_methods',
                'sql': '''
                -- Normalize payment methods for consistency
                UPDATE transactions SET payment_method = 'Check' WHERE payment_method = 'Cheque';
                UPDATE transactions SET payment_method = 'Credit Card' WHERE payment_method = 'Debit Card';
                '''
            }
        ]
        
        for migration in migrations:
            try:
                cls.apply_migration(migration['version'], migration['sql'])
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    # Column already exists, mark as applied
                    if not cls.is_migration_applied(migration['version']):
                        conn = cls.get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            'INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)', 
                            (migration['version'],)
                        )
                        conn.commit()
                        conn.close()
                else:
                    raise