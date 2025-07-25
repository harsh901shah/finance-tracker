"""
Transaction filtering utility to eliminate code duplication
"""
import streamlit as st
from datetime import datetime
from services.database_service import DatabaseService
from utils.logger import AppLogger
from utils.auth_middleware import AuthMiddleware

class TransactionFilter:
    """Centralized transaction filtering utility"""
    
    @staticmethod
    def get_filtered_transactions(date_filter=None, filters=None):
        """Get transactions with applied filters"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                # Check if user is authenticated with 'user' key
                if st.session_state.get('authenticated') and 'user' in st.session_state:
                    user_id = st.session_state.user
                    AppLogger.log_info(f"Using session user as user_id: {user_id}")
                else:
                    AppLogger.log_error("No authenticated user found", show_user=False)
                    return []
            transactions = DatabaseService.get_transactions(str(user_id))
            AppLogger.log_info(f"Loaded {len(transactions)} transactions for user: {user_id}")
            # Filter out transactions without user_id (legacy data)
            transactions = [t for t in transactions if t.get('user_id') == str(user_id)]
            
            if not transactions:
                return []
            
            # Apply date filter
            if date_filter:
                start_date, end_date = date_filter
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                transactions = [t for t in transactions if start_str <= t.get('date', '') <= end_str]
            else:
                # Default to current month
                current_month = datetime.now().strftime('%Y-%m')
                transactions = [t for t in transactions if t.get('date', '').startswith(current_month)]
            
            # Apply other filters
            if filters:
                if filters.get('transaction_types'):
                    transactions = [t for t in transactions if t.get('type', '') in filters['transaction_types']]
                
                if filters.get('categories'):
                    transactions = [t for t in transactions if t.get('category', '') in filters['categories']]
                
                if filters.get('payment_methods'):
                    transactions = [t for t in transactions if t.get('payment_method', '') in filters['payment_methods']]
            
            return transactions
            
        except Exception as e:
            AppLogger.log_error("Error filtering transactions", e, show_user=False)
            return []
    
    @staticmethod
    def calculate_financial_summary(transactions):
        """Calculate income and expenses from filtered transactions"""
        income = 0
        expenses = 0
        
        for transaction in transactions:
            try:
                amount = float(transaction.get('amount', 0))
                transaction_type = transaction.get('type', '').lower().strip()
                
                if transaction_type == 'income':
                    income += abs(amount)
                elif transaction_type == 'expense':
                    expenses += abs(amount)
            except (ValueError, TypeError):
                continue
        
        return {'income': income, 'expenses': expenses}
    
    @staticmethod
    def calculate_analytics(transactions):
        """Calculate additional analytics from filtered transactions"""
        transfers = 0
        transfer_count = 0
        category_spending = {}
        payment_method_count = {}
        transaction_amounts = []
        
        for transaction in transactions:
            try:
                amount = abs(float(transaction.get('amount', 0)))
                transaction_type = transaction.get('type', '').lower()
                transaction_category = transaction.get('category', '')
                transaction_payment = transaction.get('payment_method', '')
                
                transaction_amounts.append(amount)
                
                # Transfer analysis
                if transaction_type == 'transfer':
                    transfers += amount
                    transfer_count += 1
                
                # Category spending (expenses only)
                if transaction_type == 'expense':
                    category_spending[transaction_category] = category_spending.get(transaction_category, 0) + amount
                
                # Payment method usage
                payment_method_count[transaction_payment] = payment_method_count.get(transaction_payment, 0) + 1
                
            except (ValueError, TypeError):
                continue
        
        # Top category
        top_category = max(category_spending.items(), key=lambda x: x[1]) if category_spending else ('N/A', 0)
        
        # Top payment method
        top_payment = max(payment_method_count.items(), key=lambda x: x[1]) if payment_method_count else ('N/A', 0)
        
        # Average transaction
        avg_transaction = sum(transaction_amounts) / len(transaction_amounts) if transaction_amounts else 0
        
        return {
            'transfers': transfers,
            'transfer_count': transfer_count,
            'top_category': top_category[0],
            'top_category_amount': top_category[1],
            'avg_transaction': avg_transaction,
            'transaction_count': len(transaction_amounts),
            'top_payment_method': top_payment[0],
            'top_payment_count': top_payment[1]
        }