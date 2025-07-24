import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
from services.financial_data_service import TransactionService

class DashboardPage:
    """Dashboard page showing financial summary"""
    
    @staticmethod
    def show():
        st.header("Financial Dashboard")
        
        # Load transactions
        transactions = TransactionService.load_transactions()
        
        if not transactions:
            st.info("No transactions found. Add some transactions to see your financial summary.")
            return
        
        # Convert transactions to DataFrame
        df = pd.DataFrame(transactions)
        
        # Calculate key metrics
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expense = df[df['type'] == 'Expense']['amount'].sum()
        balance = total_income - total_expense
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"${total_income:.2f}", "")
        col2.metric("Total Expenses", f"${total_expense:.2f}", "")
        col3.metric("Balance", f"${balance:.2f}", f"{balance/total_income*100:.1f}%" if total_income > 0 else "0%")
        
        # Get statement metadata
        statement_metadata = None
        
        # First check for statement_metadata in additional_data
        for _, row in df.iterrows():
            if 'additional_data' in row and row['additional_data']:
                try:
                    additional_data = json.loads(row['additional_data'])
                    if 'statement_metadata' in additional_data:
                        statement_metadata = additional_data['statement_metadata']
                        break
                except:
                    pass
        
        # Display statement summary if available
        if statement_metadata:
            st.subheader("Bank Statement Summary")
            
            col1, col2 = st.columns(2)
            
            # Column 1: Bank and account info
            col1.markdown("**Account Information**")
            if "bank" in statement_metadata:
                col1.text(f"Bank: {statement_metadata['bank']}")
            if "account_holder" in statement_metadata:
                col1.text(f"Account Holder: {statement_metadata['account_holder']}")
            if "account_number" in statement_metadata:
                col1.text(f"Account Number: {statement_metadata['account_number']}")
            if "statement_period" in statement_metadata:
                col1.text(f"Statement Period: {statement_metadata['statement_period']}")
            
            # Column 2: Balance info
            col2.markdown("**Balance Information**")
            if "beginning_balance" in statement_metadata:
                col2.metric("Beginning Balance", f"${statement_metadata['beginning_balance']:.2f}")
            if "ending_balance" in statement_metadata:
                col2.metric("Ending Balance", f"${statement_metadata['ending_balance']:.2f}")
            if "deposits" in statement_metadata:
                col2.metric("Total Deposits", f"${statement_metadata['deposits']:.2f}")
            if "withdrawals" in statement_metadata:
                col2.metric("Total Withdrawals", f"${abs(statement_metadata['withdrawals']):.2f}")
        
        # Visualizations
        st.subheader("Expense Breakdown")
        if 'category' in df.columns and len(df[df['type'] == 'Expense']) > 0:
            expense_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().reset_index()
            fig = px.pie(expense_by_category, values='amount', names='category', title='Expenses by Category')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add categorized expenses to see the breakdown.")
        
        # Monthly trend
        if 'date' in df.columns and len(df) > 0:
            st.subheader("Monthly Trend")
            df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
            monthly_data = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
            
            if 'Income' not in monthly_data.columns:
                monthly_data['Income'] = 0
            if 'Expense' not in monthly_data.columns:
                monthly_data['Expense'] = 0
                
            monthly_data['Savings'] = monthly_data['Income'] - monthly_data['Expense']
            
            fig = px.bar(
                monthly_data.reset_index(), 
                x='month', 
                y=['Income', 'Expense', 'Savings'],
                title='Monthly Income, Expenses and Savings',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)