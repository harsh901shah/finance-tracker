import json
from typing import Dict, Any, List
from datetime import datetime
from services.database_service import DatabaseService

class StatementProcessor:
    """Process bank statements and update net worth data"""
    
    @staticmethod
    def process_statement_metadata(metadata: Dict[str, Any]) -> bool:
        """
        Process statement metadata and update net worth data
        
        Args:
            metadata: Statement metadata from parsed statement
            
        Returns:
            bool: True if statement was processed, False if duplicate detected
        """
        if not metadata:
            return False
        
        # Extract bank name and account info
        bank_name = metadata.get('bank', 'Unknown Bank')
        account_holder = metadata.get('account_holder', 'Joint')
        account_number = metadata.get('account_number', 'Unknown')
        ending_balance = metadata.get('ending_balance')
        account_type = metadata.get('account_type', 'savings')
        statement_period = metadata.get('statement_period', '')
        
        # Extract statement month and year
        statement_month = None
        statement_year = None
        if statement_period:
            # Try to extract date from statement period (e.g., "May 28, 2025 to June 25, 2025")
            import re
            end_date_match = re.search(r'to\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', statement_period)
            if end_date_match:
                month_name, day, year = end_date_match.groups()
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
                    statement_month = date_obj.month
                    statement_year = date_obj.year
                except ValueError:
                    pass
        
        # If we couldn't extract date, use current month/year
        if statement_month is None or statement_year is None:
            from datetime import datetime
            now = datetime.now()
            statement_month = now.month
            statement_year = now.year
        
        # Only proceed if we have an ending balance
        if ending_balance is None:
            return False
        
        # Check for duplicate statement - CRITICAL CHECK
        if StatementProcessor._is_duplicate_statement(bank_name, account_number, account_type, statement_month, statement_year):
            print(f"Duplicate statement detected and blocked: {bank_name} {account_type} {account_number}")
            return False
        
        # Create an asset entry for the bank account with the selected account type
        asset = {
            'name': f"{bank_name} {account_type.title()} Account {account_number}",
            'value': ending_balance,
            'owner': account_holder,
            'asset_type': account_type,  # Use the exact account type selected by the user
            'statement_month': statement_month,
            'statement_year': statement_year
        }
        
        # Add or update the asset in the database
        StatementProcessor._add_or_update_asset(asset)
        
        # Record this statement to prevent duplicates
        StatementProcessor._record_statement(bank_name, account_number, account_type, statement_month, statement_year)
        
        return True
    
    @staticmethod
    def _is_duplicate_statement(bank_name: str, account_number: str, account_type: str, 
                               statement_month: int, statement_year: int) -> bool:
        """
        Check if a statement for this bank account and month/year already exists
        
        Args:
            bank_name: Name of the bank
            account_number: Account number
            account_type: Type of account (checking, savings, etc.)
            statement_month: Month of the statement
            statement_year: Year of the statement
            
        Returns:
            bool: True if duplicate, False otherwise
        """
        # Get all statements from the database
        statements = DatabaseService.get_statements()
        
        # Check for matching statement
        for stmt in statements:
            if (stmt.get('bank_name') == bank_name and
                stmt.get('account_number') == account_number and
                stmt.get('account_type') == account_type and
                stmt.get('statement_month') == statement_month and
                stmt.get('statement_year') == statement_year):
                print(f"Duplicate statement found: {bank_name} {account_type} {account_number} {statement_month}/{statement_year}")
                return True
        
        return False
    
    @staticmethod
    def _record_statement(bank_name: str, account_number: str, account_type: str,
                         statement_month: int, statement_year: int):
        """
        Record a processed statement to prevent duplicates
        
        Args:
            bank_name: Name of the bank
            account_number: Account number
            account_type: Type of account (checking, savings, etc.)
            statement_month: Month of the statement
            statement_year: Year of the statement
        """
        statement = {
            'bank_name': bank_name,
            'account_number': account_number,
            'account_type': account_type,
            'statement_month': statement_month,
            'statement_year': statement_year,
            'processed_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        DatabaseService.add_statement(statement)
    
    @staticmethod
    def _add_or_update_asset(asset: Dict[str, Any]):
        """
        Add or update an asset in the database
        
        Args:
            asset: Asset data to add or update
        """
        # Extract statement month/year for statement tracking
        statement_month = asset.pop('statement_month', None)
        statement_year = asset.pop('statement_year', None)
        
        # Check if asset already exists
        existing_assets = DatabaseService.get_assets()
        asset_updated = False
        
        for existing in existing_assets:
            # Match by name and asset_type
            if (existing.get('name') == asset.get('name') and 
                existing.get('asset_type') == asset.get('asset_type')):
                
                # Update the existing asset
                DatabaseService.update_asset(
                    existing['id'],
                    asset.get('value'),
                    datetime.now().strftime('%Y-%m-%d')
                )
                asset_updated = True
                break
        
        # If no match found, add as new asset
        if not asset_updated:
            DatabaseService.add_asset(asset)