from datetime import datetime
from typing import Dict, Any, List, Optional

class Transaction:
    """Transaction model class"""
    
    def __init__(self, 
                 date: str, 
                 amount: float, 
                 type: str, 
                 description: str = "", 
                 category: str = "Other", 
                 payment_method: str = "Other"):
        self.date = date
        self.amount = amount
        self.type = type
        self.description = description
        self.category = category
        self.payment_method = payment_method
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create a Transaction object from a dictionary"""
        return cls(
            date=data.get('date', datetime.now().strftime("%Y-%m-%d")),
            amount=data.get('amount', 0.0),
            type=data.get('type', 'Expense'),
            description=data.get('description', ''),
            category=data.get('category', 'Other'),
            payment_method=data.get('payment_method', 'Other')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Transaction object to dictionary"""
        return {
            'date': self.date,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'category': self.category,
            'payment_method': self.payment_method
        }