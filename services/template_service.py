import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for managing transaction templates"""
    
    @classmethod
    def initialize_templates_table(cls):
        """Create transaction_templates table and add custom_fields column to transactions"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create templates table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                icon TEXT NOT NULL DEFAULT '💰',
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                default_amount REAL DEFAULT 0.0,
                default_payment_method TEXT DEFAULT 'Bank Transfer',
                fields_schema TEXT,
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, template_name)
            )
            ''')
            
            # Add custom_fields column to transactions if not exists
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'custom_fields' not in columns:
                cursor.execute('ALTER TABLE transactions ADD COLUMN custom_fields TEXT')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize templates table: {e}")
            raise
        finally:
            conn.close()
    
    @classmethod
    def create_template(cls, user_id: str, template_data: Dict[str, Any]) -> int:
        """Create a new transaction template"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO transaction_templates 
            (user_id, template_name, icon, transaction_type, category, default_amount, 
             default_payment_method, fields_schema, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(user_id),
                template_data['template_name'],
                template_data.get('icon', '💰'),
                template_data['transaction_type'],
                template_data['category'],
                template_data.get('default_amount', 0.0),
                template_data.get('default_payment_method', 'Bank Transfer'),
                json.dumps(template_data.get('fields_schema', {})),
                template_data.get('sort_order', 0)
            ))
            
            template_id = cursor.lastrowid
            conn.commit()
            return template_id
        except sqlite3.IntegrityError:
            conn.rollback()
            logger.warning(f"Template '{template_data['template_name']}' already exists for user {user_id}")
            return 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create template: {e}")
            return 0
        finally:
            conn.close()
    
    @classmethod
    def get_user_templates(cls, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all templates for a user"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            if active_only:
                cursor.execute('''
                SELECT * FROM transaction_templates 
                WHERE user_id = ? AND is_active = 1 
                ORDER BY sort_order, template_name
                ''', (str(user_id),))
            else:
                cursor.execute('''
                SELECT * FROM transaction_templates 
                WHERE user_id = ? 
                ORDER BY sort_order, template_name
                ''', (str(user_id),))
            
            templates = []
            for row in cursor.fetchall():
                template = dict(row)
                if template.get('fields_schema'):
                    template['fields_schema'] = json.loads(template['fields_schema'])
                templates.append(template)
            
            return templates
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
        finally:
            conn.close()
    
    @classmethod
    def update_template(cls, template_id: int, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update a template"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['template_name', 'icon', 'transaction_type', 'category', 
                          'default_amount', 'default_payment_method', 'is_active', 'sort_order']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                elif key == 'fields_schema':
                    set_clauses.append("fields_schema = ?")
                    values.append(json.dumps(value))
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.extend([template_id, str(user_id)])
            
            cursor.execute(f'''
            UPDATE transaction_templates 
            SET {', '.join(set_clauses)}
            WHERE id = ? AND user_id = ?
            ''', values)
            
            updated = cursor.rowcount > 0
            conn.commit()
            return updated
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update template: {e}")
            return False
        finally:
            conn.close()
    
    @classmethod
    def delete_template(cls, template_id: int, user_id: str) -> bool:
        """Delete a template (soft delete by setting is_active = 0)"""
        return cls.update_template(template_id, user_id, {'is_active': 0})
    
    @classmethod
    def seed_default_templates(cls, user_id: str):
        """Seed default templates from existing hardcoded categories"""
        default_templates = [
            # Income
            {'template_name': 'Monthly Salary', 'icon': '💰', 'transaction_type': 'Income', 'category': 'Salary', 'default_amount': 5000.0, 'sort_order': 1},
            {'template_name': 'Interest Income', 'icon': '🏦', 'transaction_type': 'Income', 'category': 'Investment', 'default_amount': 50.0, 'sort_order': 2},
            {'template_name': 'BOX STOCKS ESPP', 'icon': '📈', 'transaction_type': 'Income', 'category': 'Investment', 'default_amount': 0.0, 'sort_order': 3},
            {'template_name': 'Tax Refund', 'icon': '💸', 'transaction_type': 'Income', 'category': 'Tax', 'default_amount': 800.0, 'sort_order': 4},
            {'template_name': 'BOX RSU', 'icon': '📊', 'transaction_type': 'Income', 'category': 'Investment', 'default_amount': 2000.0, 'sort_order': 5},
            {'template_name': 'BOX ESPP PROFIT', 'icon': '💹', 'transaction_type': 'Income', 'category': 'Investment', 'default_amount': 500.0, 'sort_order': 6},
            
            # Taxes
            {'template_name': 'TAXES PAID', 'icon': '🏛️', 'transaction_type': 'Tax', 'category': 'Tax', 'default_amount': 1200.0, 'sort_order': 10},
            
            # Housing
            {'template_name': 'Mortgage', 'icon': '🏠', 'transaction_type': 'Expense', 'category': 'Housing', 'default_amount': 2500.0, 'sort_order': 20},
            {'template_name': 'HOA', 'icon': '🏢', 'transaction_type': 'Expense', 'category': 'Housing', 'default_amount': 100.0, 'sort_order': 21},
            {'template_name': 'Property Tax', 'icon': '🏘️', 'transaction_type': 'Expense', 'category': 'Housing', 'default_amount': 0.0, 'sort_order': 22},
            {'template_name': 'Furniture', 'icon': '🛋️', 'transaction_type': 'Expense', 'category': 'Shopping', 'default_amount': 800.0, 'sort_order': 23},
            {'template_name': 'Utilities', 'icon': '⚡', 'transaction_type': 'Expense', 'category': 'Bills & Utilities', 'default_amount': 0.0, 'sort_order': 24},
            {'template_name': 'Jewelry', 'icon': '💎', 'transaction_type': 'Expense', 'category': 'Shopping', 'default_amount': 500.0, 'sort_order': 25},
            
            # Transportation
            {'template_name': 'Car Loan', 'icon': '🚗', 'transaction_type': 'Expense', 'category': 'Transportation', 'default_amount': 450.0, 'sort_order': 30},
            {'template_name': 'Car Insurance', 'icon': '🚙', 'transaction_type': 'Expense', 'category': 'Transportation', 'default_amount': 150.0, 'sort_order': 31},
            {'template_name': 'Gas', 'icon': '⛽', 'transaction_type': 'Expense', 'category': 'Transportation', 'default_amount': 60.0, 'sort_order': 32},
            
            # Retirement
            {'template_name': '401K Pretax', 'icon': '🏦', 'transaction_type': 'Income', 'category': 'Retirement', 'default_amount': 800.0, 'sort_order': 40},
            {'template_name': '401k Roth', 'icon': '🏦', 'transaction_type': 'Investment', 'category': 'Retirement', 'default_amount': 500.0, 'sort_order': 41},
            {'template_name': 'HSA', 'icon': '🏥', 'transaction_type': 'Income', 'category': 'Healthcare', 'default_amount': 300.0, 'sort_order': 42},
            
            # Debt & Credit
            {'template_name': 'Credit Card', 'icon': '💳', 'transaction_type': 'Expense', 'category': 'Credit Card', 'default_amount': 200.0, 'sort_order': 50},
            {'template_name': 'Extra Principal', 'icon': '🏠', 'transaction_type': 'Expense', 'category': 'Housing', 'default_amount': 300.0, 'sort_order': 51},
            
            # Investments & Transfers
            {'template_name': 'Savings Transfer', 'icon': '💰', 'transaction_type': 'Transfer', 'category': 'Savings', 'default_amount': 0.0, 'sort_order': 60},
            {'template_name': 'ROBINHOOD', 'icon': '📈', 'transaction_type': 'Investment', 'category': 'Investment', 'default_amount': 500.0, 'sort_order': 61},
            {'template_name': 'Savings Withdraw', 'icon': '💸', 'transaction_type': 'Transfer', 'category': 'Savings', 'default_amount': 500.0, 'sort_order': 62},
            {'template_name': 'GOLD Investment', 'icon': '🥇', 'transaction_type': 'Investment', 'category': 'Investment', 'default_amount': 200.0, 'sort_order': 63},
            {'template_name': 'Money to India', 'icon': '🌏', 'transaction_type': 'Transfer', 'category': 'Transfer', 'default_amount': 0.0, 'sort_order': 64},
        ]
        
        for template in default_templates:
            cls.create_template(user_id, template)
