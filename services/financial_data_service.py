import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class TransactionService:
    """Service for handling transaction data"""
    
    @staticmethod
    def add_transaction(transaction: Dict[str, Any], user_id: str = None) -> int:
        """Add a transaction to the database"""
        from utils.auth_middleware import AuthMiddleware
        
        if not user_id:
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
        
        return DatabaseService.add_transaction(transaction, user_id)
    
    @staticmethod
    def load_transactions(user_id: str = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Load all transactions from the database for a specific user with caching"""
        from utils.auth_middleware import AuthMiddleware
        
        if not user_id:
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
        
        # Use cached version if available and recent
        if use_cache:
            cached_data = TransactionService._get_cached_transactions(user_id)
            if cached_data:
                return cached_data
        
        transactions = DatabaseService.get_transactions(user_id)
        
        # Cache the results
        if use_cache:
            TransactionService._cache_transactions(user_id, transactions)
        
        return transactions
    
    @staticmethod
    def _get_cached_transactions(user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached transactions if they exist and are recent"""
        import streamlit as st
        
        cache_key = f"transactions_cache_{user_id}"
        cache_time_key = f"transactions_cache_time_{user_id}"
        
        if cache_key in st.session_state and cache_time_key in st.session_state:
            cache_time = st.session_state[cache_time_key]
            # Cache valid for 5 minutes
            if datetime.now() - cache_time < timedelta(minutes=5):
                return st.session_state[cache_key]
        
        return None
    
    @staticmethod
    def _cache_transactions(user_id: str, transactions: List[Dict[str, Any]]):
        """Cache transactions data"""
        import streamlit as st
        
        cache_key = f"transactions_cache_{user_id}"
        cache_time_key = f"transactions_cache_time_{user_id}"
        
        st.session_state[cache_key] = transactions
        st.session_state[cache_time_key] = datetime.now()
    
    @staticmethod
    def clear_cache(user_id: str = None):
        """Clear cached transaction data"""
        import streamlit as st
        from utils.auth_middleware import AuthMiddleware
        
        if not user_id:
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
        
        cache_key = f"transactions_cache_{user_id}"
        cache_time_key = f"transactions_cache_time_{user_id}"
        
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        if cache_time_key in st.session_state:
            del st.session_state[cache_time_key]
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_transaction_summary(user_id: str, date_range: str = "current_month") -> Dict[str, float]:
        """Get optimized transaction summary with caching"""
        transactions = TransactionService.load_transactions(user_id, use_cache=True)
        
        # Filter by date range
        if date_range == "current_month":
            current_month = datetime.now().strftime('%Y-%m')
            filtered_transactions = [t for t in transactions if t.get('date', '').startswith(current_month)]
        elif date_range == "last_30_days":
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            filtered_transactions = [t for t in transactions if t.get('date', '') >= cutoff_date]
        else:
            filtered_transactions = transactions
        
        # Calculate summary
        summary = {
            'total_income': sum(float(t.get('amount', 0)) for t in filtered_transactions if t.get('type') == 'Income'),
            'total_expenses': sum(float(t.get('amount', 0)) for t in filtered_transactions if t.get('type') == 'Expense'),
            'total_taxes': sum(float(t.get('amount', 0)) for t in filtered_transactions if t.get('type') == 'Tax'),
            'total_investments': sum(float(t.get('amount', 0)) for t in filtered_transactions if t.get('type') == 'Investment'),
            'total_transfers': sum(float(t.get('amount', 0)) for t in filtered_transactions if t.get('type') == 'Transfer'),
            'transaction_count': len(filtered_transactions)
        }
        
        summary['net_cash_flow'] = summary['total_income'] - summary['total_expenses'] - summary['total_taxes'] - summary['total_investments'] - summary['total_transfers']
        
        return summary
    
    @staticmethod
    def get_statement_metadata(user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get the latest statement metadata from transactions"""
        from utils.auth_middleware import AuthMiddleware
        
        if not user_id:
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
        
        transactions = DatabaseService.get_transactions(user_id)
        
        # Look for statement metadata in transactions
        for transaction in transactions:
            # Check if transaction has additional_data field
            if 'additional_data' in transaction and transaction['additional_data']:
                try:
                    # Parse additional_data as JSON
                    additional_data = json.loads(transaction['additional_data'])
                    
                    # Check if it contains statement_metadata
                    if 'statement_metadata' in additional_data:
                        return additional_data['statement_metadata']
                except:
                    pass
        
        return None

class BudgetService:
    """Service for handling budget data"""
    
    @classmethod
    def save_budget(cls, budget_data: Dict[str, float]) -> bool:
        """Save budget data to database"""
        try:
            # Get current month and year
            current_month = datetime.now().strftime('%m')
            current_year = datetime.now().year
            
            # Save each category as a budget item
            for category, amount in budget_data.items():
                budget_item = {
                    'category': category,
                    'amount': amount,
                    'month': current_month,
                    'year': current_year
                }
                
                DatabaseService.add_budget(budget_item)
            
            return True
        except ValueError as e:
            logger.warning(f"Invalid budget data: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving budget: {str(e)}")
            return False
    
    @classmethod
    def load_budget(cls) -> Dict[str, float]:
        """Load budget data from database"""
        try:
            # Get current month and year
            current_month = datetime.now().strftime('%m')
            current_year = datetime.now().year
            
            # Get budget items for current month
            budget_items = DatabaseService.get_budget(current_month, current_year)
            
            # Convert to dictionary
            budget_data = {}
            for item in budget_items:
                budget_data[item['category']] = item['amount']
            
            return budget_data
        except Exception as e:
            logger.error(f"Error loading budget data: {str(e)}")
            return {}

class NetWorthService:
    """Service for handling net worth data"""
    
    NETWORTH_FILE = 'networth.json'
    
    @classmethod
    def save_networth(cls, networth_data: Dict[str, Any], user_id: str = None) -> bool:
        """Save net worth data to database with user isolation"""
        try:
            from utils.auth_middleware import AuthMiddleware
            
            if not user_id:
                current_user = AuthMiddleware.get_current_user_id()
                user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
            
            # Save investments
            investments = networth_data.get('investments', {})
            for asset_type, assets in investments.items():
                for asset in assets:
                    asset['asset_type'] = asset_type
                    DatabaseService.add_asset(asset, user_id)
            
            # Save debts
            debts = networth_data.get('debts', {})
            for liability_type, liabilities in debts.items():
                for liability in liabilities:
                    liability['liability_type'] = liability_type
                    DatabaseService.add_liability(liability, user_id)
            
            # Save real estate
            real_estate = networth_data.get('real_estate', [])
            for property in real_estate:
                DatabaseService.add_real_estate(property, user_id)
            
            return True
        except ValueError as e:
            logger.warning(f"Invalid net worth data: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving net worth: {str(e)}")
            return False
    
    @classmethod
    def load_networth(cls, user_id: str = None) -> Dict[str, Any]:
        """Load net worth data from database for a specific user"""
        try:
            from utils.auth_middleware import AuthMiddleware
            
            if not user_id:
                current_user = AuthMiddleware.get_current_user_id()
                user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
            
            networth_data = {
                'investments': {
                    'stocks': [],
                    'savings': [],
                    'retirement': [],
                    'hsa': [],
                    'precious_metals': []
                },
                'debts': {
                    'loans': [],
                    'credit_cards': [],
                    'mortgage': []
                },
                'real_estate': [],
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Load assets
            assets = DatabaseService.get_assets(user_id)
            for asset in assets:
                asset_type = asset.get('asset_type')
                
                # Map account types to appropriate investment categories
                if asset_type == 'checking' or asset_type == 'savings' or asset_type == 'money market':
                    target_type = 'savings'  # All bank accounts go into savings category
                else:
                    target_type = asset_type
                    
                if target_type in networth_data['investments']:
                    # Remove asset_type from the asset
                    asset_copy = dict(asset)
                    if 'asset_type' in asset_copy:
                        del asset_copy['asset_type']
                    networth_data['investments'][target_type].append(asset_copy)
            
            # Load liabilities
            liabilities = DatabaseService.get_liabilities(user_id)
            for liability in liabilities:
                liability_type = liability.get('liability_type')
                if liability_type in networth_data['debts']:
                    # Remove liability_type from the liability
                    liability_copy = dict(liability)
                    if 'liability_type' in liability_copy:
                        del liability_copy['liability_type']
                    networth_data['debts'][liability_type].append(liability_copy)
            
            # Load real estate
            real_estate = DatabaseService.get_real_estate(user_id)
            networth_data['real_estate'] = real_estate
            
            return networth_data
        except Exception as e:
            logger.error(f"Error loading net worth data: {str(e)}")
            return {}