"""
Application configuration constants

Notes:
- DEFAULT_CATEGORIES: Core transaction categories, extensible via user preferences
- DEFAULT_PAYMENT_METHODS: Standard payment options, customizable per user
- UTILITY_TYPES: Supported utility types with suggested default amounts
- CHART_COLORS: Consistent color palette across all visualizations
- BUDGET_COLORS: Configurable colors for budget status indicators
- FEATURES: Toggle switches for optional functionality
"""
from config.constants import PaymentMethods, TransactionTypes

class AppConfig:
    """Centralized configuration for the application"""
    
    # Default categories - can be extended by user preferences
    DEFAULT_CATEGORIES = [
        "Salary", "Investment", "Retirement", "401k", "Roth", "PreTax", "Healthcare",
        "Housing", "Transportation", "Utilities", "Shopping", "Tax", 
        "Credit Card", "Savings", "Transfer", "Food", "Entertainment", "Other"
    ]
    
    # Default payment methods - backward compatibility
    DEFAULT_PAYMENT_METHODS = PaymentMethods.DEFAULT
    
    # Transaction types
    TRANSACTION_TYPES = TransactionTypes.ALL
    
    # Utility types with default amounts
    UTILITY_TYPES = {
        "Electric": 120.0,
        "Phone": 50.0, 
        "Wifi/Internet": 80.0,
        "Water": 60.0,
        "Gas": 90.0
    }
    
    # Chart color palette for consistent theming
    CHART_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#3F51B5', '#009688']
    
    # Budget chart colors for different states
    BUDGET_COLORS = {
        'under_budget': '#4CAF50',  # Green for under budget
        'over_budget': '#F44336',   # Red for over budget
        'at_budget': '#FF9800'      # Orange for at budget (90-100%)
    }
    
    # Feature toggles for enabling/disabling functionality
    FEATURES = {
        'custom_categories': True,
        'custom_payment_methods': True,
        'budget_tracking': True,
        'advanced_analytics': True
    }
    
    # Date periods for filtering
    DATE_PERIODS = [
        "This Week", "Last Week", "Last 3 Months", "Last 6 Months", 
        "Year to Date", "Last 12 Months", "This Year", "Custom"
    ]