import pandas as pd
from typing import Dict, Any

def compute_kpis(filtered_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute KPIs from filtered dataframe"""
    if filtered_df.empty:
        return {
            'income': 0,
            'expenses': 0,
            'taxes': 0,
            'net_income': 0,
            'savings_rate': 0,
            'transfers': 0,
            'avg_transaction': 0,
            'top_category': 'N/A',
            'top_payment_method': 'N/A',
            'transaction_count': 0
        }
    
    # Income
    income = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
    
    # Expenses (excluding transfers and taxes)
    expense_df = filtered_df[
        (filtered_df['type'] == 'expense') & 
        (~filtered_df['category'].str.lower().isin(['transfer', 'tax']))
    ]
    expenses = expense_df['amount'].sum()
    
    # Taxes
    taxes = filtered_df[
        (filtered_df['type'] == 'expense') & 
        (filtered_df['category'].str.lower() == 'tax')
    ]['amount'].sum()
    
    # Net income
    net_income = income - expenses - taxes
    
    # Savings rate (guard divide-by-zero)
    savings_rate = (max(net_income, 0) / income * 100) if income > 0 else 0
    
    # Transfers
    transfers = filtered_df[filtered_df['type'] == 'transfer']['amount'].sum()
    
    # Average transaction
    avg_transaction = filtered_df['amount'].mean() if not filtered_df.empty else 0
    
    # Top category (expenses only)
    if not expense_df.empty:
        top_category = expense_df.groupby('category')['amount'].sum().idxmax()
    else:
        top_category = 'N/A'
    
    # Top payment method
    if not filtered_df.empty:
        top_payment_method = filtered_df['payment_method'].value_counts().index[0]
    else:
        top_payment_method = 'N/A'
    
    return {
        'income': income,
        'expenses': expenses,
        'taxes': taxes,
        'net_income': net_income,
        'savings_rate': savings_rate,
        'transfers': transfers,
        'avg_transaction': avg_transaction,
        'top_category': top_category,
        'top_payment_method': top_payment_method,
        'transaction_count': len(filtered_df)
    }