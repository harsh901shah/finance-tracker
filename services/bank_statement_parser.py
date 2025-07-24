import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

class BankStatementParser:
    """Parser for bank statements"""
    
    @staticmethod
    def parse_text(text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse bank statement text and extract transactions and metadata
        
        Args:
            text: The text content of the bank statement
            
        Returns:
            Tuple of (transactions, metadata)
        """
        transactions = []
        metadata = {}
        
        # Extract bank name
        bank_name = BankStatementParser._extract_bank_name(text)
        if bank_name:
            metadata["bank"] = bank_name
        
        # Extract account holder
        account_holder = BankStatementParser._extract_account_holder(text)
        if account_holder:
            metadata["account_holder"] = account_holder
        
        # Extract account number
        account_number = BankStatementParser._extract_account_number(text)
        if account_number:
            metadata["account_number"] = account_number
        
        # Extract statement period
        statement_period = BankStatementParser._extract_statement_period(text)
        if statement_period:
            metadata["statement_period"] = statement_period
        
        # Extract balances
        beginning_balance = BankStatementParser._extract_beginning_balance(text)
        if beginning_balance is not None:
            metadata["beginning_balance"] = beginning_balance
        
        ending_balance = BankStatementParser._extract_ending_balance(text)
        if ending_balance is not None:
            metadata["ending_balance"] = ending_balance
        
        # Extract deposits and withdrawals
        deposits = BankStatementParser._extract_deposits(text)
        if deposits is not None:
            metadata["deposits"] = deposits
        
        withdrawals = BankStatementParser._extract_withdrawals(text)
        if withdrawals is not None:
            metadata["withdrawals"] = withdrawals
        
        # Extract transactions
        transactions = BankStatementParser._extract_transactions(text)
        
        # If no transactions found but we have metadata, create a summary transaction
        if not transactions and metadata:
            date_str = datetime.now().strftime("%Y-%m-%d")
            if "statement_period" in metadata:
                # Try to extract end date from statement period
                match = re.search(r'to\s+(\d{1,2}/\d{1,2}/\d{2,4})', metadata["statement_period"])
                if match:
                    try:
                        date_obj = datetime.strptime(match.group(1), "%m/%d/%Y")
                        date_str = date_obj.strftime("%Y-%m-%d")
                    except:
                        pass
            
            amount = metadata.get("ending_balance", 0.0)
            
            transactions.append({
                "date": date_str,
                "description": f"{metadata.get('bank', 'Bank')} Statement Summary",
                "amount": amount,
                "type": "Expense",
                "category": "Other",
                "payment_method": "Bank Transfer",
                "statement_metadata": metadata
            })
        
        return transactions, metadata
    
    @staticmethod
    def _extract_bank_name(text: str) -> Optional[str]:
        """Extract bank name from text"""
        if "Bank of America" in text:
            return "Bank of America"
        elif "Chase" in text:
            return "Chase"
        elif "Wells Fargo" in text:
            return "Wells Fargo"
        elif "Citibank" in text:
            return "Citibank"
        return None
    
    @staticmethod
    def _extract_account_holder(text: str) -> Optional[str]:
        """Extract account holder from text"""
        # Look for name patterns
        patterns = [
            r'(?:Account Holder|Customer):\s*([A-Z\s]+)',
            r'(?:Prepared for|Statement for):\s*([A-Z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Try to find all-caps names
        lines = text.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            if re.match(r'^[A-Z\s]{5,30}$', line.strip()):
                return line.strip()
        
        return None
    
    @staticmethod
    def _extract_account_number(text: str) -> Optional[str]:
        """Extract account number from text"""
        patterns = [
            r'Account [Nn]umber:?\s*[•*Xx]*(\d{4})',
            r'Account [Nn]umber:?\s*[•*Xx]*(\d{3,4})',
            r'Account:?\s*[•*Xx]*(\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"xxxx{match.group(1)}"
        
        return None
    
    @staticmethod
    def _extract_statement_period(text: str) -> Optional[str]:
        """Extract statement period from text"""
        patterns = [
            r'[Ss]tatement [Pp]eriod:?\s*(.*?\d{4})\s+to\s+(.*?\d{4})',
            r'[Ss]tatement [Dd]ate:?\s*(.*?\d{4})\s+to\s+(.*?\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)} to {match.group(2)}"
        
        return None
    
    @staticmethod
    def _extract_beginning_balance(text: str) -> Optional[float]:
        """Extract beginning balance from text"""
        patterns = [
            r'[Bb]eginning [Bb]alance.*?(\$?[\d,]+\.\d{2})',
            r'[Pp]revious [Bb]alance.*?(\$?[\d,]+\.\d{2})',
            r'[Oo]pening [Bb]alance.*?(\$?[\d,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                amount_str = match.group(1).replace('$', '').replace(',', '')
                try:
                    return float(amount_str)
                except:
                    pass
        
        return None
    
    @staticmethod
    def _extract_ending_balance(text: str) -> Optional[float]:
        """Extract ending balance from text"""
        patterns = [
            r'[Ee]nding [Bb]alance.*?(\$?[\d,]+\.\d{2})',
            r'[Cc]losing [Bb]alance.*?(\$?[\d,]+\.\d{2})',
            r'[Nn]ew [Bb]alance.*?(\$?[\d,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                amount_str = match.group(1).replace('$', '').replace(',', '')
                try:
                    return float(amount_str)
                except:
                    pass
        
        return None
    
    @staticmethod
    def _extract_deposits(text: str) -> Optional[float]:
        """Extract total deposits from text"""
        patterns = [
            r'[Tt]otal [Dd]eposits.*?(\$?[\d,]+\.\d{2})',
            r'[Dd]eposits and [Cc]redits.*?(\$?[\d,]+\.\d{2})',
            r'[Dd]eposits and [Oo]ther [Aa]dditions.*?(\$?[\d,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                amount_str = match.group(1).replace('$', '').replace(',', '')
                try:
                    return float(amount_str)
                except:
                    pass
        
        return None
    
    @staticmethod
    def _extract_withdrawals(text: str) -> Optional[float]:
        """Extract total withdrawals from text"""
        patterns = [
            r'[Tt]otal [Ww]ithdrawals.*?(\$?[\d,]+\.\d{2})',
            r'[Ww]ithdrawals and [Dd]ebits.*?(\$?[\d,]+\.\d{2})',
            r'[Ww]ithdrawals and [Oo]ther [Ss]ubtractions.*?(\$?[\d,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                amount_str = match.group(1).replace('$', '').replace(',', '')
                try:
                    return -float(amount_str)  # Make withdrawals negative
                except:
                    pass
        
        return None
    
    @staticmethod
    def _extract_transactions(text: str) -> List[Dict[str, Any]]:
        """Extract transactions from text"""
        transactions = []
        
        # Common transaction patterns
        patterns = [
            # Date Description Amount
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+([^$\n]{5,}?)\s+(\$?[\d,]+\.\d{2})',
            
            # Date Description Debit/Credit
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+([^$\n]{5,}?)\s+(?:DEBIT|CREDIT|WITHDRAWAL|DEPOSIT)?\s+(\$?[\d,]+\.\d{2})'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
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
                        'payment_method': 'Bank Transfer'
                    }
                    
                    transactions.append(transaction)
                except Exception as e:
                    print(f"Error parsing transaction: {e}")
        
        return transactions