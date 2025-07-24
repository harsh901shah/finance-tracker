import json
import os
from datetime import datetime

# File path for storing transaction data
DATA_FILE = 'transactions.json'

def load_data():
    """Load transaction data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_data(transactions):
    """Save transaction data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)

def calculate_monthly_summary(transactions):
    """Calculate monthly income, expenses, and savings"""
    if not transactions:
        return {}
    
    # Group transactions by month
    monthly_data = {}
    
    for transaction in transactions:
        date = datetime.strptime(transaction['date'], '%Y-%m-%d')
        month_key = date.strftime('%Y-%m')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if transaction['type'] == 'Income':
            monthly_data[month_key]['income'] += transaction['amount']
        else:  # Expense
            monthly_data[month_key]['expense'] += transaction['amount']
    
    # Calculate savings
    for month in monthly_data:
        monthly_data[month]['savings'] = monthly_data[month]['income'] - monthly_data[month]['expense']
    
    return monthly_data

def get_category_spending(transactions, category=None):
    """Get spending by category"""
    if not transactions:
        return {}
    
    category_spending = {}
    
    for transaction in transactions:
        if transaction['type'] == 'Expense':
            if category and transaction['category'] != category:
                continue
                
            cat = transaction['category']
            if cat not in category_spending:
                category_spending[cat] = 0
            
            category_spending[cat] += transaction['amount']
    
    return category_spending

def get_date_range_transactions(transactions, start_date, end_date):
    """Filter transactions by date range"""
    if not transactions:
        return []
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    filtered_transactions = []
    
    for transaction in transactions:
        date = datetime.strptime(transaction['date'], '%Y-%m-%d')
        if start <= date <= end:
            filtered_transactions.append(transaction)
    
    return filtered_transactions