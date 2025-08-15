import pandas as pd
from datetime import datetime
from services.financial_data_service import TransactionService
from utils.filters import Filters
from utils.auth_middleware import AuthMiddleware

def load_transactions() -> pd.DataFrame:
    """Load and normalize transaction data"""
    try:
        transactions = TransactionService.load_transactions()
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Coerce dates and numbers
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        # Normalize types
        df['type'] = df['type'].str.lower().str.strip()
        df['category'] = df['category'].fillna('Other')
        df['payment_method'] = df['payment_method'].fillna('Other')
        
        return df
    except Exception:
        return pd.DataFrame()

def apply_filters(df: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Apply filters to transaction dataframe"""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Date filter
    if filters.start_date and filters.end_date:
        start_dt = pd.to_datetime(filters.start_date)
        end_dt = pd.to_datetime(filters.end_date)
        filtered_df = filtered_df[
            (filtered_df['date'] >= start_dt) & 
            (filtered_df['date'] <= end_dt)
        ]
    
    # Transaction type filter
    if filters.transaction_types:
        type_filter = [t.lower() for t in filters.transaction_types]
        filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]
    
    # Category filter
    if filters.categories:
        filtered_df = filtered_df[filtered_df['category'].isin(filters.categories)]
    
    # Payment method filter
    if filters.payment_methods:
        filtered_df = filtered_df[filtered_df['payment_method'].isin(filters.payment_methods)]
    
    return filtered_df