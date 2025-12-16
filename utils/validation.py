"""
Input validation utilities
"""
from typing import Optional, Tuple
from config.constants import ValidationRules

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Centralized input validation"""
    
    @staticmethod
    def validate_amount(amount: Optional[float]) -> Tuple[bool, str]:
        """Validate transaction amount"""
        if amount is None:
            return False, "Amount is required"
        
        if amount <= 0:
            return False, "Amount must be greater than zero"
            
        if amount > ValidationRules.MAX_AMOUNT:
            return False, f"Amount cannot exceed ${ValidationRules.MAX_AMOUNT:,.0f}"
            
        return True, ""
    
    @staticmethod
    def validate_description(description: Optional[str]) -> Tuple[bool, str]:
        """Validate transaction description"""
        if not description or not description.strip():
            return False, "Description is required"
            
        if len(description.strip()) > ValidationRules.MAX_DESCRIPTION_LENGTH:
            return False, f"Description cannot exceed {ValidationRules.MAX_DESCRIPTION_LENGTH} characters"
            
        return True, ""
    
    @staticmethod
    def validate_transaction_data(transaction_data: dict) -> Tuple[bool, list]:
        """Validate complete transaction data"""
        errors = []
        
        # Validate amount
        is_valid, error = InputValidator.validate_amount(transaction_data.get('amount'))
        if not is_valid:
            errors.append(error)
            
        # Validate description
        is_valid, error = InputValidator.validate_description(transaction_data.get('description'))
        if not is_valid:
            errors.append(error)
            
        # Validate date
        if not transaction_data.get('date'):
            errors.append("Date is required")
            
        # Validate type
        from config.constants import TransactionTypes
        if transaction_data.get('type') not in TransactionTypes.ALL:
            errors.append("Invalid transaction type")
            
        return len(errors) == 0, errors