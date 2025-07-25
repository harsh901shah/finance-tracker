"""
Application configuration constants
"""

class AppConfig:
    """Centralized configuration for the application"""
    
    # Default categories - can be extended by user preferences
    DEFAULT_CATEGORIES = [
        "Salary", "Investment", "Tax", "Retirement", "Healthcare",
        "Housing", "Transportation", "Utilities", "Shopping", 
        "Credit Card", "Savings", "Transfer", "Food", "Entertainment", "Other"
    ]
    
    # Default payment methods - can be extended by user preferences
    DEFAULT_PAYMENT_METHODS = [
        "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit", "Other"
    ]
    
    # Transaction types
    TRANSACTION_TYPES = ["Income", "Expense", "Investment", "Transfer"]
    
    # Utility types with default amounts
    UTILITY_TYPES = {
        "Electric": 120.0,
        "Phone": 50.0, 
        "Wifi/Internet": 80.0,
        "Water": 60.0,
        "Gas": 90.0
    }
    
    # Chart colors
    CHART_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#3F51B5', '#009688']
    
    # Date periods for filtering
    DATE_PERIODS = [
        "This Week", "Last Week", "Last 3 Months", "Last 6 Months", 
        "Year to Date", "Last 12 Months", "This Year", "Custom"
    ]