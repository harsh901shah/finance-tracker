import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging to file and stdout for diagnostics and auditing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for handling database operations"""
    
    DB_FILE = 'finance_tracker.db'
    
    @classmethod
    def get_connection(cls):
        """Get a database connection"""
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.OperationalError as e:
            # Catch OperationalError for database file permission issues
            logger.error(f"Database file access error: {str(e)}")
            raise IOError(f"Cannot access database file. Check permissions: {str(e)}")
        except sqlite3.DatabaseError as e:
            # Handle database corruption or format errors separately for better diagnostics
            logger.error(f"Database corruption or format error: {str(e)}")
            raise IOError(f"Database file may be corrupted: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected database connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    @classmethod
    def initialize_database(cls):
        """Create database tables if they don't exist"""
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            # Create transactions table with additional_data JSON field
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                category TEXT,
                payment_method TEXT,
                additional_data TEXT,  -- JSON field for dynamic attributes
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create assets table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                owner TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create liabilities table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS liabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                owner TEXT NOT NULL,
                liability_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create real_estate table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_estate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                current_value REAL NOT NULL,
                purchase_value REAL NOT NULL,
                owner TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create budget table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month TEXT NOT NULL,
                year INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, month, year)
            )
            ''')
            
            # Create statements table to track processed statements
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                account_type TEXT NOT NULL,
                statement_month INTEGER NOT NULL,
                statement_year INTEGER NOT NULL,
                processed_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(bank_name, account_number, account_type, statement_month, statement_year)
            )
            ''')
            
            # Create indexes for performance optimization (user_id columns added dynamically)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)')
            
            # Create audit log table for sensitive actions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                old_data TEXT,
                new_data TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp ON audit_log(user_id, timestamp DESC)')
            
            # Create undo snapshots table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS undo_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL
            )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_undo_user_created ON undo_snapshots(user_id, created_at DESC)')
            
            conn.commit()
        except sqlite3.OperationalError as e:
            if conn:
                conn.rollback()
            logger.error(f"Database schema creation failed: {str(e)}")
            raise IOError(f"Failed to create database tables. Check disk space and permissions: {str(e)}")
        except sqlite3.DatabaseError as e:
            if conn:
                conn.rollback()
            logger.error(f"Database integrity error during initialization: {str(e)}")
            raise IOError(f"Database integrity error: {str(e)}")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error during database initialization: {str(e)}")
            raise RuntimeError(f"Database initialization failed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def import_json_data(cls):
        """Import data from existing JSON files into the database"""
        # This method is intentionally left empty to avoid importing sample data
        # You can add your own data import logic here if needed
        pass

    # Transaction methods
    @classmethod
    def add_transaction(cls, transaction: Dict[str, Any], user_id: str) -> int:
        """Add a transaction to the database with user isolation"""
        conn = None
        try:
            # Validate required fields
            if 'date' not in transaction:
                raise ValueError("Transaction date is required")
            if 'amount' not in transaction:
                raise ValueError("Transaction amount is required")
            if 'type' not in transaction:
                raise ValueError("Transaction type is required")
            if not user_id:
                raise ValueError("User ID is required")
                
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            # Add user_id column if it doesn't exist
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute('ALTER TABLE transactions ADD COLUMN user_id TEXT')
            
            # Extract standard fields
            date = transaction.get('date')
            amount = transaction.get('amount')
            type_ = transaction.get('type')
            description = transaction.get('description', '')
            category = transaction.get('category', 'Other')
            payment_method = transaction.get('payment_method', 'Other')
            
            # Extract additional data (anything that's not a standard field)
            standard_fields = {'date', 'amount', 'type', 'description', 'category', 'payment_method'}
            additional_data = {k: v for k, v in transaction.items() if k not in standard_fields}
            
            # Convert additional data to JSON string
            additional_data_json = json.dumps(additional_data) if additional_data else None
            
            cursor.execute('''
            INSERT INTO transactions (date, amount, type, description, category, payment_method, additional_data, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date,
                amount,
                type_,
                description,
                category,
                payment_method,
                additional_data_json,
                user_id
            ))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            return transaction_id
        except sqlite3.IntegrityError as e:
            # Handle constraint violations (duplicate keys, foreign key errors)
            if conn:
                conn.rollback()
            logger.warning(f"Transaction data integrity violation: {str(e)}")
            raise ValueError(f"Invalid transaction data: {str(e)}")
        except sqlite3.OperationalError as e:
            # Catch OperationalError for database file permission issues
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed for transaction: {str(e)}")
            raise IOError(f"Database operation failed. Try again: {str(e)}")
        except ValueError as e:
            logger.warning(f"Transaction validation failed: {str(e)}")
            raise
        except json.JSONEncodeError as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to serialize transaction data: {str(e)}")
            raise ValueError(f"Invalid transaction data format: {str(e)}")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error adding transaction: {str(e)}")
            raise RuntimeError(f"Failed to save transaction: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_transactions(cls, user_id: str = None) -> List[Dict[str, Any]]:
        """Get transactions from the database, filtered by user if provided"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN user_id TEXT')
            # Set existing transactions to default user for migration
            cursor.execute('UPDATE transactions SET user_id = ? WHERE user_id IS NULL', ('default_user',))
            conn.commit()
        
        if user_id:
            # Handle both string and integer user_id
            cursor.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC', (str(user_id),))
        else:
            # Don't return any transactions if no user_id provided
            return []
            
        transactions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return transactions
    
    @classmethod
    def delete_transaction(cls, transaction_id: int, user_id: str) -> bool:
        """Delete a transaction from the database with audit logging"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Debug logging
        logger.info(f"Attempting to delete transaction {transaction_id} for user_id: {user_id} (type: {type(user_id)})")
        
        # Get transaction data before deletion for audit log
        cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, str(user_id)))
        transaction_data = cursor.fetchone()
        
        # Debug: Check if transaction was found
        if not transaction_data:
            logger.warning(f"Transaction {transaction_id} not found for user {user_id}")
            # Try to find the transaction without user filter to see if it exists
            cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
            any_transaction = cursor.fetchone()
            if any_transaction:
                logger.warning(f"Transaction {transaction_id} exists but belongs to user_id: {any_transaction['user_id']} (type: {type(any_transaction['user_id'])})")
            else:
                logger.warning(f"Transaction {transaction_id} does not exist at all")
        
        if transaction_data:
            # Log the deletion
            cls._log_audit_action(user_id, 'DELETE', 'transactions', transaction_id, dict(transaction_data), None)
            
            cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, str(user_id)))
            deleted = cursor.rowcount > 0
            logger.info(f"Delete operation result: {deleted}")
        else:
            deleted = False
        
        conn.commit()
        conn.close()
        
        return deleted
    
    @classmethod
    def bulk_delete_transactions(cls, transaction_ids: List[int], user_id: str) -> int:
        """Delete multiple transactions with audit logging"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        deleted_count = 0
        
        try:
            for transaction_id in transaction_ids:
                # Get transaction data before deletion
                cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, str(user_id)))
                transaction_data = cursor.fetchone()
                
                if transaction_data:
                    # Log the deletion
                    cls._log_audit_action(user_id, 'DELETE', 'transactions', transaction_id, dict(transaction_data), None)
                    
                    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, str(user_id)))
                    if cursor.rowcount > 0:
                        deleted_count += 1
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return deleted_count
    
    # Asset methods
    @classmethod
    def add_asset(cls, asset: Dict[str, Any], user_id: str) -> int:
        """Add an asset to the database with user isolation"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(assets)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE assets ADD COLUMN user_id TEXT')
        
        cursor.execute('''
        INSERT INTO assets (name, value, owner, asset_type, user_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            asset.get('name'),
            asset.get('value'),
            asset.get('owner', 'Joint'),
            asset.get('asset_type', 'Other'),
            str(user_id)
        ))
        
        asset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return asset_id
    
    @classmethod
    def get_assets(cls, user_id: str, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get assets from the database for a specific user, optionally filtered by type"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(assets)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE assets ADD COLUMN user_id TEXT')
            cursor.execute('UPDATE assets SET user_id = ? WHERE user_id IS NULL', ('default_user',))
            conn.commit()
        
        if asset_type:
            cursor.execute('SELECT * FROM assets WHERE user_id = ? AND asset_type = ?', (str(user_id), asset_type))
        else:
            cursor.execute('SELECT * FROM assets WHERE user_id = ?', (str(user_id),))
            
        assets = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return assets
    
    @classmethod
    def update_asset(cls, asset_id: int, value: float, updated_at: str) -> bool:
        """Update an asset's value in the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE assets 
            SET value = ?, updated_at = ? 
            WHERE id = ?
            ''', (value, updated_at, asset_id))
            
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except sqlite3.IntegrityError as e:
            conn.rollback()
            logger.warning(f"Asset update integrity violation: {str(e)}")
            return False
        except sqlite3.OperationalError as e:
            conn.rollback()
            logger.error(f"Asset update operation failed: {str(e)}")
            return False
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error updating asset: {str(e)}")
            return False
        finally:
            conn.close()
    
    # Liability methods
    @classmethod
    def add_liability(cls, liability: Dict[str, Any], user_id: str) -> int:
        """Add a liability to the database with user isolation"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(liabilities)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE liabilities ADD COLUMN user_id TEXT')
        
        cursor.execute('''
        INSERT INTO liabilities (name, value, owner, liability_type, user_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            liability.get('name'),
            liability.get('value'),
            liability.get('owner', 'Joint'),
            liability.get('liability_type', 'Other'),
            str(user_id)
        ))
        
        liability_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return liability_id
    
    @classmethod
    def get_liabilities(cls, user_id: str, liability_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get liabilities from the database for a specific user, optionally filtered by type"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(liabilities)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE liabilities ADD COLUMN user_id TEXT')
            cursor.execute('UPDATE liabilities SET user_id = ? WHERE user_id IS NULL', ('default_user',))
            conn.commit()
        
        if liability_type:
            cursor.execute('SELECT * FROM liabilities WHERE user_id = ? AND liability_type = ?', (str(user_id), liability_type))
        else:
            cursor.execute('SELECT * FROM liabilities WHERE user_id = ?', (str(user_id),))
            
        liabilities = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return liabilities
    
    # Real estate methods
    @classmethod
    def add_real_estate(cls, property: Dict[str, Any], user_id: str) -> int:
        """Add a real estate property to the database with user isolation"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(real_estate)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE real_estate ADD COLUMN user_id TEXT')
        
        cursor.execute('''
        INSERT INTO real_estate (name, current_value, purchase_value, owner, user_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            property.get('name'),
            property.get('current_value'),
            property.get('purchase_value', 0),
            property.get('owner', 'Joint'),
            str(user_id)
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return property_id
    
    @classmethod
    def get_real_estate(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get all real estate properties from the database for a specific user"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Add user_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(real_estate)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE real_estate ADD COLUMN user_id TEXT')
            cursor.execute('UPDATE real_estate SET user_id = ? WHERE user_id IS NULL', ('default_user',))
            conn.commit()
        
        cursor.execute('SELECT * FROM real_estate WHERE user_id = ?', (str(user_id),))
        properties = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return properties
    
    # Budget methods
    @classmethod
    def add_budget(cls, budget_item: Dict[str, Any]) -> int:
        """Add or update a budget item in the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO budget (category, amount, month, year)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category, month, year) 
            DO UPDATE SET amount = ?, updated_at = CURRENT_TIMESTAMP
            ''', (
                budget_item.get('category'),
                budget_item.get('amount'),
                budget_item.get('month'),
                budget_item.get('year'),
                budget_item.get('amount')
            ))
            
            budget_id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError as e:
            logger.warning(f"Budget constraint violation: {str(e)}")
            conn.rollback()
            budget_id = 0
        except sqlite3.OperationalError as e:
            logger.error(f"Budget operation failed: {str(e)}")
            conn.rollback()
            budget_id = 0
        except Exception as e:
            logger.error(f"Unexpected error adding budget: {str(e)}")
            conn.rollback()
            budget_id = 0
        finally:
            conn.close()
        
        return budget_id
    
    @classmethod
    def get_budget(cls, month: Optional[str] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get budget items from the database, optionally filtered by month and year"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        if month and year:
            cursor.execute('SELECT * FROM budget WHERE month = ? AND year = ?', (month, year))
        elif year:
            cursor.execute('SELECT * FROM budget WHERE year = ?', (year,))
        else:
            # Default to current month and year
            current_month = datetime.now().strftime('%Y-%m')
            year, month = current_month.split('-')
            cursor.execute('SELECT * FROM budget WHERE month = ? AND year = ?', (month, int(year)))
            
        budget_items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return budget_items
    
    # Statement tracking methods
    @classmethod
    def add_statement(cls, statement: Dict[str, Any]) -> int:
        """Add a processed statement record to the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO statements 
            (bank_name, account_number, account_type, statement_month, statement_year, processed_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                statement.get('bank_name'),
                statement.get('account_number'),
                statement.get('account_type'),
                statement.get('statement_month'),
                statement.get('statement_year'),
                statement.get('processed_date')
            ))
            
            statement_id = cursor.lastrowid
            conn.commit()
            return statement_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            logger.info(f"Statement already processed: {str(e)}")
            return 0
        except sqlite3.OperationalError as e:
            conn.rollback()
            logger.error(f"Statement operation failed: {str(e)}")
            return 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error adding statement: {str(e)}")
            return 0
        finally:
            conn.close()
    
    @classmethod
    def get_statements(cls) -> List[Dict[str, Any]]:
        """Get all processed statement records"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM statements')
        statements = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return statements
    
    # User preferences methods
    @classmethod
    def save_user_preference(cls, key: str, value: Any, user_id: str) -> bool:
        """Save user preference to database with user isolation"""
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            # Create preferences table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (key, user_id)
            )
            ''')
            
            # Save preference as JSON
            import json
            value_json = json.dumps(value)
            
            cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (key, user_id, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, str(user_id), value_json))
            
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if conn:
                conn.rollback()
            logger.error(f"User preference operation failed: {str(e)}")
            return False
        except json.JSONEncodeError as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to serialize preference data: {str(e)}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error saving user preference: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_user_preference(cls, key: str, user_id: str, default_value: Any = None) -> Any:
        """Get user preference from database for specific user"""
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT NOT NULL,
                user_id TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (key, user_id)
            )
            ''')
            
            cursor.execute('SELECT value FROM user_preferences WHERE key = ? AND user_id = ?', (key, str(user_id)))
            result = cursor.fetchone()
            
            if result:
                import json
                return json.loads(result[0])
            else:
                return default_value
        except sqlite3.OperationalError as e:
            logger.error(f"User preference retrieval failed: {str(e)}")
            return default_value
        except json.JSONDecodeError as e:
            logger.warning(f"Corrupted preference data for key {key}: {str(e)}")
            return default_value
        except Exception as e:
            logger.error(f"Unexpected error getting user preference: {str(e)}")
            return default_value
        finally:
            if conn:
                conn.close()
    @classmethod
    def _log_audit_action(cls, user_id: str, action: str, table_name: str, record_id: int, old_data: Dict = None, new_data: Dict = None):
        """Log audit action for sensitive operations"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO audit_log (user_id, action, table_name, record_id, old_data, new_data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                action,
                table_name,
                record_id,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None
            ))
            conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"Audit logging failed: {str(e)}")
        except json.JSONEncodeError as e:
            logger.error(f"Failed to serialize audit data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in audit logging: {str(e)}")
        finally:
            conn.close()
    
    @classmethod
    def get_audit_log(cls, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries for a user"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM audit_log 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        ''', (user_id, limit))
        
        audit_entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return audit_entries
    
    @classmethod
    def create_undo_snapshot(cls, user_id: str, action: str, data: Dict) -> int:
        """Create undo snapshot for destructive actions"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Table already created in initialize_database
        
        # Set expiration to 24 hours from now
        from datetime import datetime, timedelta
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        cursor.execute('''
        INSERT INTO undo_snapshots (user_id, action, data, expires_at)
        VALUES (?, ?, ?, ?)
        ''', (user_id, action, json.dumps(data), expires_at))
        
        snapshot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return snapshot_id
    
    @classmethod
    def get_undo_snapshots(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get available undo snapshots for user"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # Clean up expired snapshots first
        cursor.execute('DELETE FROM undo_snapshots WHERE expires_at < datetime("now")')
        
        cursor.execute('''
        SELECT * FROM undo_snapshots 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        ''', (user_id,))
        
        snapshots = [dict(row) for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        
        return snapshots
    
    @classmethod
    def restore_from_undo(cls, snapshot_id: int, user_id: str) -> bool:
        """Restore data from undo snapshot"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get snapshot data
            cursor.execute('SELECT * FROM undo_snapshots WHERE id = ? AND user_id = ?', (snapshot_id, user_id))
            snapshot = cursor.fetchone()
            
            if not snapshot:
                return False
            
            data = json.loads(snapshot['data'])
            action = snapshot['action']
            
            if action == 'DELETE_TRANSACTION':
                # Restore deleted transaction
                cls.add_transaction(data, user_id)
            elif action == 'BULK_DELETE_TRANSACTIONS':
                # Restore multiple deleted transactions
                for transaction in data['transactions']:
                    cls.add_transaction(transaction, user_id)
            
            # Remove the used snapshot
            cursor.execute('DELETE FROM undo_snapshots WHERE id = ?', (snapshot_id,))
            conn.commit()
            return True
            
        except sqlite3.OperationalError as e:
            conn.rollback()
            logger.error(f"Undo operation failed: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            conn.rollback()
            logger.error(f"Corrupted undo data: {str(e)}")
            return False
        except Exception as e:
            conn.rollback()
            logger.error(f"Unexpected error during undo: {str(e)}")
            return False
        finally:
            conn.close()