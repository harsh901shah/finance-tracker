"""Data integrity utilities to fix common data issues"""

from services.database_service import DatabaseService

class DataIntegrityFixer:
    """Fix common data integrity issues in the database"""
    
    @staticmethod
    def fix_transaction_types():
        """Fix transactions with wrong type based on category"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            expense_categories = ('Travel', 'Food', 'Groceries', 'Shopping', 'Entertainment', 
                                'Transportation', 'Housing', 'Bills & Utilities', 'Healthcare',
                                'Education', 'Personal Care', 'Dining', 'Credit Card')
            
            cursor.execute(f"""
                UPDATE transactions 
                SET type = 'Expense' 
                WHERE category IN ({','.join(['?']*len(expense_categories))}) 
                AND type != 'Expense'
            """, expense_categories)
            
            fixed_count = cursor.rowcount
            conn.commit()
            return fixed_count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def fix_template_types():
        """Fix templates with wrong type based on category"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        
        try:
            expense_categories = ('Travel', 'Food', 'Groceries', 'Shopping', 'Entertainment', 
                                'Transportation', 'Housing', 'Bills & Utilities', 'Healthcare',
                                'Education', 'Personal Care', 'Dining', 'Credit Card')
            
            cursor.execute(f"""
                UPDATE transaction_templates 
                SET transaction_type = 'Expense' 
                WHERE category IN ({','.join(['?']*len(expense_categories))}) 
                AND transaction_type != 'Expense'
            """, expense_categories)
            
            fixed_count = cursor.rowcount
            conn.commit()
            return fixed_count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
