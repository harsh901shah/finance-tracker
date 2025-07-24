import re
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple

def parse_bank_statement(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parse bank statement text and extract transactions and metadata
    
    Args:
        text: The text content of the bank statement
        
    Returns:
        Tuple of (transactions, metadata)
    """
    transactions = []
    metadata = {
        "bank": "Unknown",
        "statement_date": None,
        "ending_balance": None
    }
    
    # Detect bank type
    if "Bank of America" in text:
        metadata["bank"] = "Bank of America"
    elif "Chase" in text:
        metadata["bank"] = "Chase"
    elif "Wells Fargo" in text:
        metadata["bank"] = "Wells Fargo"
    
    # Extract statement date
    date_match = re.search(r'Statement Period:?\s+.*?to\s+(\d{2}/\d{2}/\d{4})', text)
    if date_match:
        metadata["statement_date"] = date_match.group(1)
    
    # Extract ending balance
    balance_match = re.search(r'[Ee]nding [Bb]alance.*?(\$?[\d,]+\.\d{2})', text, re.DOTALL)
    if balance_match:
        balance_str = balance_match.group(1).replace('$', '').replace(',', '')
        try:
            metadata["ending_balance"] = float(balance_str)
        except:
            pass
    
    # Extract transactions using a more flexible pattern
    # Format: Date Description Amount
    transaction_pattern = r'(\d{2}/\d{2}/\d{2,4})\s+([^$\n]{5,}?)\s+(\$?[\d,]+\.\d{2})'
    
    for match in re.finditer(transaction_pattern, text):
        try:
            date_str, description, amount_str = match.groups()
            
            # Parse date
            try:
                if len(date_str) == 8:  # MM/DD/YY
                    date_obj = datetime.strptime(date_str, '%m/%d/%y')
                else:  # MM/DD/YYYY
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                date = date_obj.strftime('%Y-%m-%d')
            except:
                continue
            
            # Clean description
            description = description.strip()
            
            # Parse amount
            amount_str = amount_str.replace('$', '').replace(',', '')
            amount = float(amount_str)
            
            # Determine transaction type
            transaction_type = 'Income' if amount >= 0 else 'Expense'
            amount = abs(amount)
            
            # Create transaction
            transaction = {
                'date': date,
                'description': description,
                'amount': amount,
                'type': transaction_type,
                'category': 'Uncategorized',
                'payment_method': 'Bank Transfer',
                'bank': metadata["bank"]
            }
            
            transactions.append(transaction)
        except Exception as e:
            print(f"Error parsing transaction: {e}")
    
    return transactions, metadata