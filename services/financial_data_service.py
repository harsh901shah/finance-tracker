import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.database_service import DatabaseService

class TransactionService:
    """Service for handling transaction data"""
    
    @staticmethod
    def add_transaction(transaction: Dict[str, Any]) -> int:
        """Add a transaction to the database"""
        return DatabaseService.add_transaction(transaction)
    
    @staticmethod
    def load_transactions() -> List[Dict[str, Any]]:
        """Load all transactions from the database"""
        return DatabaseService.get_transactions()
    
    @staticmethod
    def get_statement_metadata() -> Optional[Dict[str, Any]]:
        """Get the latest statement metadata from transactions"""
        transactions = DatabaseService.get_transactions()
        
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
        except Exception as e:
            print(f"Error saving budget: {e}")
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
            print(f"Error loading budget: {e}")
            return {}

class NetWorthService:
    """Service for handling net worth data"""
    
    NETWORTH_FILE = 'networth.json'
    
    @classmethod
    def save_networth(cls, networth_data: Dict[str, Any]) -> bool:
        """Save net worth data to database"""
        try:
            # Save investments
            investments = networth_data.get('investments', {})
            for asset_type, assets in investments.items():
                for asset in assets:
                    asset['asset_type'] = asset_type
                    DatabaseService.add_asset(asset)
            
            # Save debts
            debts = networth_data.get('debts', {})
            for liability_type, liabilities in debts.items():
                for liability in liabilities:
                    liability['liability_type'] = liability_type
                    DatabaseService.add_liability(liability)
            
            # Save real estate
            real_estate = networth_data.get('real_estate', [])
            for property in real_estate:
                DatabaseService.add_real_estate(property)
            
            return True
        except Exception as e:
            print(f"Error saving net worth data: {e}")
            return False
    
    @classmethod
    def load_networth(cls) -> Dict[str, Any]:
        """Load net worth data from database"""
        try:
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
            assets = DatabaseService.get_assets()
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
            liabilities = DatabaseService.get_liabilities()
            for liability in liabilities:
                liability_type = liability.get('liability_type')
                if liability_type in networth_data['debts']:
                    # Remove liability_type from the liability
                    liability_copy = dict(liability)
                    if 'liability_type' in liability_copy:
                        del liability_copy['liability_type']
                    networth_data['debts'][liability_type].append(liability_copy)
            
            # Load real estate
            real_estate = DatabaseService.get_real_estate()
            networth_data['real_estate'] = real_estate
            
            return networth_data
        except Exception as e:
            print(f"Error loading net worth data: {e}")
            return {}