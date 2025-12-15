    @classmethod
    def add_budget(cls, budget_item: Dict[str, Any], user_id: str) -> int:
        """Add or update a budget item in the database with user isolation"""
        # Validate required fields
        if not budget_item.get('category'):
            logger.warning("Budget category is required")
            return 0
        if budget_item.get('amount') is None or budget_item.get('amount') < 0:
            logger.warning(f"Invalid budget amount: {budget_item.get('amount')}")
            return 0
        if not budget_item.get('month') or not budget_item.get('year'):
            logger.warning("Budget month and year are required")
            return 0
        
        budget_id = 0
        conn = None
        
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            
            # Check if budget item already exists
            cursor.execute('''
            SELECT id FROM budget 
            WHERE category = ? AND month = ? AND year = ? AND user_id = ?
            ''', (
                budget_item.get('category'),
                budget_item.get('month'),
                budget_item.get('year'),
                str(user_id)
            ))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing budget item
                cursor.execute('''
                UPDATE budget 
                SET amount = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                ''', (budget_item.get('amount'), existing[0]))
                budget_id = existing[0]
            else:
                # Insert new budget item
                cursor.execute('''
                INSERT INTO budget (category, amount, month, year, user_id)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    budget_item.get('category'),
                    budget_item.get('amount'),
                    budget_item.get('month'),
                    budget_item.get('year'),
                    str(user_id)
                ))
                budget_id = cursor.lastrowid
            
            conn.commit()
            return budget_id if budget_id else 0
            
        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            logger.warning(f"Budget constraint violation for {budget_item.get('category', 'unknown')}: {str(e)}")
            return 0
        except sqlite3.OperationalError as e:
            if conn:
                conn.rollback()
            logger.error(f"Budget operation failed for {budget_item.get('category', 'unknown')}: {str(e)}")
            return 0
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error adding budget for {budget_item.get('category', 'unknown')}: {str(e)}")
            return 0
        finally:
            if conn:
                conn.close()