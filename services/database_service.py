import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

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
        except sqlite3.Error as e:
            raise IOError(f"Database connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error connecting to database: {str(e)}")
    
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
            
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise IOError(f"Database initialization error: {str(e)}")
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Unexpected error initializing database: {str(e)}")
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
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise IOError(f"Database error adding transaction: {str(e)}")
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error adding transaction: {str(e)}")
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
            cursor.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC', (user_id,))
        else:
            # Don't return any transactions if no user_id provided
            return []
            
        transactions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return transactions
    
    @classmethod
    def delete_transaction(cls, transaction_id: int) -> bool:
        """Delete a transaction from the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    # Asset methods
    @classmethod
    def add_asset(cls, asset: Dict[str, Any]) -> int:
        """Add an asset to the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO assets (name, value, owner, asset_type)
        VALUES (?, ?, ?, ?)
        ''', (
            asset.get('name'),
            asset.get('value'),
            asset.get('owner', 'Joint'),
            asset.get('asset_type', 'Other')
        ))
        
        asset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return asset_id
    
    @classmethod
    def get_assets(cls, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get assets from the database, optionally filtered by type"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        if asset_type:
            cursor.execute('SELECT * FROM assets WHERE asset_type = ?', (asset_type,))
        else:
            cursor.execute('SELECT * FROM assets')
            
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
        except Exception as e:
            conn.rollback()
            print(f"Error updating asset: {e}")
            return False
        finally:
            conn.close()
    
    # Liability methods
    @classmethod
    def add_liability(cls, liability: Dict[str, Any]) -> int:
        """Add a liability to the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO liabilities (name, value, owner, liability_type)
        VALUES (?, ?, ?, ?)
        ''', (
            liability.get('name'),
            liability.get('value'),
            liability.get('owner', 'Joint'),
            liability.get('liability_type', 'Other')
        ))
        
        liability_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return liability_id
    
    @classmethod
    def get_liabilities(cls, liability_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get liabilities from the database, optionally filtered by type"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        if liability_type:
            cursor.execute('SELECT * FROM liabilities WHERE liability_type = ?', (liability_type,))
        else:
            cursor.execute('SELECT * FROM liabilities')
            
        liabilities = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return liabilities
    
    # Real estate methods
    @classmethod
    def add_real_estate(cls, property: Dict[str, Any]) -> int:
        """Add a real estate property to the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO real_estate (name, current_value, purchase_value, owner)
        VALUES (?, ?, ?, ?)
        ''', (
            property.get('name'),
            property.get('current_value'),
            property.get('purchase_value', 0),
            property.get('owner', 'Joint')
        ))
        
        property_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return property_id
    
    @classmethod
    def get_real_estate(cls) -> List[Dict[str, Any]]:
        """Get all real estate properties from the database"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM real_estate')
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
        except Exception as e:
            print(f"Error adding budget: {e}")
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
        except Exception as e:
            conn.rollback()
            print(f"Error adding statement record: {e}")
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
            ''', (key, user_id, value_json))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error saving user preference: {e}")
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
            
            cursor.execute('SELECT value FROM user_preferences WHERE key = ? AND user_id = ?', (key, user_id))
            result = cursor.fetchone()
            
            if result:
                import json
                return json.loads(result[0])
            else:
                return default_value
        except Exception as e:
            print(f"Error getting user preference: {e}")
            return default_value
        finally:
            if conn:
                conn.close()