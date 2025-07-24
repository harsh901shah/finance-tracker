import pandas as pd
import yaml
import csv
import os
from datetime import datetime

def load_accounts_config():
    """Load accounts configuration from YAML file"""
    if os.path.exists('accounts.yaml'):
        with open('accounts.yaml', 'r') as file:
            return yaml.safe_load(file)
    return None

def parse_csv_transactions(file_path, mapping=None):
    """
    Parse transactions from CSV file
    
    Args:
        file_path: Path to the CSV file
        mapping: Dictionary mapping CSV columns to transaction fields
                e.g. {'Date': 'date', 'Amount': 'amount', ...}
    
    Returns:
        List of transaction dictionaries
    """
    if not mapping:
        # Default mapping for common CSV formats
        mapping = {
            'Date': 'date',
            'Description': 'description',
            'Amount': 'amount',
            'Category': 'category'
        }
    
    try:
        df = pd.read_csv(file_path)
        
        # Rename columns based on mapping
        columns_to_rename = {}
        for csv_col, trans_field in mapping.items():
            if csv_col in df.columns:
                columns_to_rename[csv_col] = trans_field
        
        if columns_to_rename:
            df = df.rename(columns=columns_to_rename)
        
        # Ensure required fields exist
        required_fields = ['date', 'amount']
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"Required field '{field}' not found in CSV")
        
        # Process date format
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Determine transaction type based on amount
        if 'type' not in df.columns:
            df['type'] = df['amount'].apply(lambda x: 'Income' if x >= 0 else 'Expense')
            # Make all amounts positive
            df['amount'] = df['amount'].abs()
        
        # Add default values for missing fields
        if 'description' not in df.columns:
            df['description'] = 'Imported transaction'
        
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        if 'payment_method' not in df.columns:
            df['payment_method'] = 'Other'
        
        # Convert DataFrame to list of dictionaries
        transactions = df.to_dict('records')
        return transactions
    
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []

def categorize_transaction(description):
    """
    Automatically categorize a transaction based on its description
    Simple rule-based categorization
    """
    description = description.lower()
    
    # Food related
    if any(keyword in description for keyword in ['restaurant', 'cafe', 'food', 'grocery', 'market', 'supermarket']):
        return 'Food'
    
    # Transportation
    if any(keyword in description for keyword in ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'transport', 'parking']):
        return 'Transportation'
    
    # Housing
    if any(keyword in description for keyword in ['rent', 'mortgage', 'home', 'apartment', 'housing']):
        return 'Housing'
    
    # Utilities
    if any(keyword in description for keyword in ['electric', 'water', 'utility', 'internet', 'phone', 'bill']):
        return 'Utilities'
    
    # Entertainment
    if any(keyword in description for keyword in ['movie', 'theatre', 'concert', 'netflix', 'spotify', 'entertainment']):
        return 'Entertainment'
    
    # Healthcare
    if any(keyword in description for keyword in ['doctor', 'hospital', 'medical', 'pharmacy', 'health']):
        return 'Healthcare'
    
    # Education
    if any(keyword in description for keyword in ['school', 'college', 'university', 'course', 'book', 'education']):
        return 'Education'
    
    # Shopping
    if any(keyword in description for keyword in ['amazon', 'walmart', 'target', 'shop', 'store', 'purchase']):
        return 'Shopping'
    
    # Income
    if any(keyword in description for keyword in ['salary', 'paycheck', 'deposit', 'income']):
        return 'Salary'
    
    # Default
    return 'Other'