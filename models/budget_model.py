from typing import Dict, Any, List, Optional

class Budget:
    """Budget model class"""
    
    def __init__(self, category: str, amount: float):
        self.category = category
        self.amount = amount
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """Create a Budget object from a dictionary"""
        return cls(
            category=data.get('category', 'Other'),
            amount=data.get('amount', 0.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Budget object to dictionary"""
        return {
            'category': self.category,
            'amount': self.amount
        }