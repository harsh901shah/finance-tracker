from typing import Dict, Any, List, Optional

class Asset:
    """Asset model class"""
    
    def __init__(self, name: str, value: float, owner: str = "Joint", asset_type: str = "Other"):
        self.name = name
        self.value = value
        self.owner = owner
        self.asset_type = asset_type
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        """Create an Asset object from a dictionary"""
        return cls(
            name=data.get('name', ''),
            value=data.get('value', 0.0),
            owner=data.get('owner', 'Joint'),
            asset_type=data.get('asset_type', 'Other')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Asset object to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'owner': self.owner
        }

class Liability:
    """Liability model class"""
    
    def __init__(self, name: str, value: float, owner: str = "Joint", liability_type: str = "Other"):
        self.name = name
        self.value = value
        self.owner = owner
        self.liability_type = liability_type
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Liability':
        """Create a Liability object from a dictionary"""
        return cls(
            name=data.get('name', ''),
            value=data.get('value', 0.0),
            owner=data.get('owner', 'Joint'),
            liability_type=data.get('liability_type', 'Other')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Liability object to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'owner': self.owner
        }

class RealEstate:
    """Real Estate model class"""
    
    def __init__(self, name: str, current_value: float, purchase_value: float = 0.0, owner: str = "Joint"):
        self.name = name
        self.current_value = current_value
        self.purchase_value = purchase_value
        self.owner = owner
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealEstate':
        """Create a RealEstate object from a dictionary"""
        return cls(
            name=data.get('name', ''),
            current_value=data.get('current_value', 0.0),
            purchase_value=data.get('purchase_value', 0.0),
            owner=data.get('owner', 'Joint')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert RealEstate object to dictionary"""
        return {
            'name': self.name,
            'current_value': self.current_value,
            'purchase_value': self.purchase_value,
            'owner': self.owner
        }
    
    @property
    def equity(self) -> float:
        """Calculate equity in the property"""
        return self.current_value - self.purchase_value