"""
Centralized constants and enumerations for the application
"""
import os

class DatabaseConstants:
    """Database configuration constants. DB path can be overridden via FINANCE_TRACKER_DB_PATH for hosting."""
    DB_FILE = os.environ.get('FINANCE_TRACKER_DB_PATH', 'finance_tracker.db')
    TEST_DB_PREFIX = 'test_'

class TransactionTypes:
    INCOME = "Income"
    EXPENSE = "Expense"
    INVESTMENT = "Investment"
    TRANSFER = "Transfer"
    TAX = "Tax"
    
    ALL = [INCOME, EXPENSE, INVESTMENT, TRANSFER, TAX]
    DEFAULT_FILTER = [INCOME, EXPENSE]

class Categories:
    # Income categories
    SALARY = "Salary"
    INVESTMENT = "Investment"
    
    # Expense categories
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    SHOPPING = "Shopping"
    FOOD = "Food"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    
    # Special categories
    TAX = "Tax"
    RETIREMENT = "Retirement"
    CREDIT_CARD = "Credit Card"
    SAVINGS = "Savings"
    TRANSFER = "Transfer"
    OTHER = "Other"
    
    ALL = [
        SALARY, INVESTMENT, RETIREMENT, HEALTHCARE,
        HOUSING, TRANSPORTATION, UTILITIES, SHOPPING, 
        TAX, CREDIT_CARD, SAVINGS, TRANSFER, 
        FOOD, ENTERTAINMENT, OTHER
    ]

class PaymentMethods:
    BANK_TRANSFER = "Bank Transfer"
    CREDIT_CARD = "Credit Card"
    CASH = "Cash"
    CHECK = "Check"
    DIRECT_DEPOSIT = "Direct Deposit"
    OTHER = "Other"
    
    ALL = [BANK_TRANSFER, CREDIT_CARD, CASH, CHECK, DIRECT_DEPOSIT, OTHER]
    DEFAULT = [BANK_TRANSFER, CREDIT_CARD, CASH, CHECK, DIRECT_DEPOSIT]
    
    # Backward compatibility
    LEGACY_MAPPING = {
        "Cheque": CHECK,
        "Debit Card": CREDIT_CARD,
    }
    
    @classmethod
    def normalize(cls, payment_method):
        """Normalize payment method for consistent storage"""
        return cls.LEGACY_MAPPING.get(payment_method, payment_method)

class ValidationRules:
    MIN_AMOUNT = 0.01
    MAX_AMOUNT = 1000000.0
    MAX_DESCRIPTION_LENGTH = 255
    
class UIConstants:
    MAX_COLUMNS_PER_ROW = 5
    DEFAULT_STEP_AMOUNT = 0.01
    CHART_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#3F51B5', '#009688']