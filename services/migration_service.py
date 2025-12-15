"""
Database migration service for schema changes
"""
import sqlite3
import logging
import re
from typing import List, Dict
from config.constants import DatabaseConstants

logger = logging.getLogger(__name__)

# Allowed tables for migration operations (security whitelist)
ALLOWED_MIGRATION_TABLES = {'transactions', 'budget', 'assets', 'liabilities', 'real_estate'}

# Strict identifier validation (letters, digits, underscore, not starting with digit)
IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Dangerous SQL keywords that must be blocked
DANGEROUS_KEYWORDS = re.compile(r'\b(DROP|ATTACH|DETACH|PRAGMA|BEGIN|COMMIT|ALTER\s+TABLE|DELETE|INSERT|UPDATE|CREATE|EXEC)\b', re.IGNORECASE)

class MigrationService:
    """Handles database schema migrations"""
    
    DB_FILE = DatabaseConstants.DB_FILE
    
    @classmethod
    def get_connection(cls):
        """Get database connection"""
        conn = sqlite3.connect(cls.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    
    @classmethod
    def _ensure_table_allowed(cls, table_name: str):
        """Validate table name against whitelist and identifier rules"""
        if not table_name:
            logger.warning(f"Migration security: Empty table name rejected")
            raise ValueError("table_name is required")
        if not IDENT_RE.match(table_name):
            logger.warning(f"Migration security: Invalid table identifier '{table_name}' rejected (invalid characters)")
            raise ValueError(f"Invalid table name '{table_name}'. Must contain only letters, digits, underscore and not start with digit")
        if table_name.lower() not in ALLOWED_MIGRATION_TABLES:
            logger.warning(f"Migration security: Table '{table_name}' rejected (not in whitelist). Allowed: {sorted(ALLOWED_MIGRATION_TABLES)}")
            raise ValueError(f"Table '{table_name}' not allowed. Allowed: {sorted(ALLOWED_MIGRATION_TABLES)}")
    
    @classmethod
    def _validate_column_name(cls, column_name: str):
        """Validate column name follows SQL identifier rules"""
        if not column_name:
            logger.warning(f"Migration security: Empty column name rejected")
            raise ValueError("column_name is required")
        if not IDENT_RE.match(column_name):
            logger.warning(f"Migration security: Invalid column identifier '{column_name}' rejected (invalid characters)")
            raise ValueError(f"Invalid column name '{column_name}'. Must contain only letters, digits, underscore and not start with digit")
    
    @classmethod
    def _validate_column_definition(cls, column_name: str, column_definition: str):
        """Validate column definition with strict SQL injection protection"""
        if not column_definition:
            logger.warning(f"Migration security: Empty column definition rejected for column '{column_name}'")
            raise ValueError("column_definition is required")
        
        # Block dangerous characters that enable SQL injection
        if ';' in column_definition:
            logger.warning(f"Migration security: Column definition rejected for '{column_name}' (contains semicolon): {column_definition!r}")
            raise ValueError("Semicolons not allowed in column definition")
        if '--' in column_definition:
            logger.warning(f"Migration security: Column definition rejected for '{column_name}' (contains SQL comment): {column_definition!r}")
            raise ValueError("SQL comments not allowed in column definition")
        if '/*' in column_definition or '*/' in column_definition:
            logger.warning(f"Migration security: Column definition rejected for '{column_name}' (contains block comment): {column_definition!r}")
            raise ValueError("SQL block comments not allowed in column definition")
        
        # Block dangerous SQL keywords
        if DANGEROUS_KEYWORDS.search(column_definition):
            logger.warning(f"Migration security: Column definition rejected for '{column_name}' (contains dangerous keywords): {column_definition!r}")
            raise ValueError("Dangerous SQL keywords not allowed in column definition")
        
        # Ensure definition starts with the column name
        col_pattern = re.compile(r'^\s*[`"\[]?' + re.escape(column_name) + r'[`"\]]?\b', re.IGNORECASE)
        if not col_pattern.match(column_definition):
            logger.warning(f"Migration security: Column definition rejected for '{column_name}' (wrong column name): {column_definition!r}")
            raise ValueError(f"Column definition must start with column name '{column_name}'. Got: {column_definition!r}")
    
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
    def column_exists(cls, table_name: str, column_name: str) -> bool:
        """Check if column exists in table"""
        cls._ensure_table_allowed(table_name)
        cls._validate_column_name(column_name)
        
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Use quoted identifier for safety
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        
        return column_name in columns
    
    @classmethod
    def add_column_if_not_exists(cls, table_name: str, column_name: str, column_definition: str):
        """Add column only if it doesn't exist"""
        cls._ensure_table_allowed(table_name)
        cls._validate_column_name(column_name)
        cls._validate_column_definition(column_name, column_definition)
        
        if not cls.column_exists(table_name, column_name):
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            try:
                # Use quoted identifiers for safety
                cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN {column_definition}')
                conn.commit()
                logger.info(f"Added column {column_name} to {table_name}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to add column {column_name} to {table_name}: {e}")
                raise
            finally:
                conn.close()
        else:
            logger.info(f"Column {column_name} already exists in {table_name}")
    
    @classmethod
    def run_all_migrations(cls):
        """Run all pending migrations"""
        cls.initialize_migrations_table()
        
        # Migration 001: Add user_id columns
        if not cls.is_migration_applied('001_add_user_id_columns'):
            cls.add_column_if_not_exists('transactions', 'user_id', 'user_id TEXT DEFAULT "default_user"')
            cls.add_column_if_not_exists('budget', 'user_id', 'user_id TEXT DEFAULT "default_user"')
            cls.add_column_if_not_exists('assets', 'user_id', 'user_id TEXT DEFAULT "default_user"')
            cls.add_column_if_not_exists('liabilities', 'user_id', 'user_id TEXT DEFAULT "default_user"')
            cls.add_column_if_not_exists('real_estate', 'user_id', 'user_id TEXT DEFAULT "default_user"')
            
            # Mark migration as applied
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)', ('001_add_user_id_columns',))
            conn.commit()
            conn.close()
        
        # Migration 002: Normalize payment methods
        if not cls.is_migration_applied('002_normalize_payment_methods'):
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("UPDATE transactions SET payment_method = 'Check' WHERE payment_method = 'Cheque'")
                cursor.execute("UPDATE transactions SET payment_method = 'Credit Card' WHERE payment_method = 'Debit Card'")
                cursor.execute('INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)', ('002_normalize_payment_methods',))
                conn.commit()
                logger.info("Applied migration 002_normalize_payment_methods")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to apply migration 002_normalize_payment_methods: {e}")
                raise
            finally:
                conn.close()