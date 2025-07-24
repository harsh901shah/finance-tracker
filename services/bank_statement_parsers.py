import re
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class BankStatementParser:
    """Base class for bank statement parsers"""
    
    @staticmethod
    def parse(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse bank statement text
        
        Returns:
            Tuple of (transactions, metadata)
        """
        raise NotImplementedError("Subclasses must implement this method")

class BankOfAmericaParser(BankStatementParser):
    """Parser for Bank of America statements"""
    
    @staticmethod
    def parse(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse Bank of America statement text
        
        Returns:
            Tuple of (transactions, metadata)
        """
        transactions = []
        metadata = {
            "bank": "Bank of America",
            "statement_date": None,
            "beginning_balance": None,
            "ending_balance": None,
            "total_deposits": None,
            "total_withdrawals": None
        }
        
        # Extract statement date
        date_match = re.search(r'Statement Period:\s+(\d{2}/\d{2}/\d{4})\s+to\s+(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            metadata["statement_start_date"] = date_match.group(1)
            metadata["statement_date"] = date_match.group(2)
        
        # Extract beginning balance
        begin_balance_match = re.search(r'Beginning Balance\s+\$?([\d,]+\.\d{2})', text)
        if begin_balance_match:
            metadata["beginning_balance"] = float(begin_balance_match.group(1).replace(',', ''))
        
        # Extract ending balance
        end_balance_match = re.search(r'Ending Balance\s+\$?([\d,]+\.\d{2})', text)
        if end_balance_match:
            metadata["ending_balance"] = float(end_balance_match.group(1).replace(',', ''))
        
        # Extract total deposits
        deposits_match = re.search(r'Total deposits and credits\s+\$?([\d,]+\.\d{2})', text)
        if deposits_match:
            metadata["total_deposits"] = float(deposits_match.group(1).replace(',', ''))
        
        # Extract total withdrawals
        withdrawals_match = re.search(r'Total withdrawals and debits\s+\$?([\d,]+\.\d{2})', text)
        if withdrawals_match:
            metadata["total_withdrawals"] = float(withdrawals_match.group(1).replace(',', ''))
        
        # Extract account number (masked)
        account_match = re.search(r'Account Number:\s+\*+(\d{4})', text)
        if account_match:
            metadata["account_number"] = f"xxxx{account_match.group(1)}"
        
        # Extract transactions
        # Bank of America format: MM/DD/YY Description Amount
        transaction_pattern = r'(\d{2}/\d{2}/\d{2})\s+([^\$]+?)\s+(\-?\$?[\d,]+\.\d{2})'
        
        for match in re.finditer(transaction_pattern, text):
            try:
                date_str, description, amount_str = match.groups()
                
                # Parse date
                date_obj = datetime.strptime(date_str, '%m/%d/%y')
                date = date_obj.strftime('%Y-%m-%d')
                
                # Parse amount
                amount_str = amount_str.replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                # Determine transaction type
                transaction_type = 'Income' if amount >= 0 else 'Expense'
                amount = abs(amount)  # Make amount positive
                
                # Create transaction
                transaction = {
                    'date': date,
                    'description': description.strip(),
                    'amount': amount,
                    'type': transaction_type,
                    'category': 'Uncategorized',
                    'payment_method': 'Bank Transfer',
                    'bank': 'Bank of America'
                }
                
                transactions.append(transaction)
            except Exception as e:
                print(f"Error parsing transaction: {e}")
        
        return transactions, metadata

# Factory for getting the right parser
def get_parser(bank_name: str) -> BankStatementParser:
    """Get the appropriate parser for a bank"""
    parsers = {
        "bank of america": BankOfAmericaParser,
    }
    
    bank_name = bank_name.lower()
    for key, parser in parsers.items():
        if key in bank_name:
            return parser
    
    # Default to Bank of America parser
    return BankOfAmericaParser