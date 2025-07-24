import streamlit as st
import pandas as pd
import json
from datetime import datetime
from services.financial_data_service import TransactionService

class TransactionPage:
    """Transaction page for adding and viewing transactions"""
    
    @staticmethod
    def show_add():
        st.header("Add New Transaction")
        
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now())
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
                transaction_type = st.selectbox("Type", ["Expense", "Income"])
                
            with col2:
                description = st.text_input("Description")
                category = st.selectbox(
                    "Category", 
                    ["Food", "Transportation", "Housing", "Utilities", "Entertainment", 
                     "Healthcare", "Education", "Shopping", "Salary", "Investment", "Other"]
                )
                payment_method = st.selectbox(
                    "Payment Method", 
                    ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other"]
                )
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                new_transaction = {
                    "date": date.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "type": transaction_type,
                    "description": description,
                    "category": category,
                    "payment_method": payment_method
                }
                
                # Add transaction to storage
                TransactionService.add_transaction(new_transaction)
                st.success("Transaction added successfully!")
    
    @staticmethod
    def show_list():
        st.header("Transaction History")
        
        # Load transactions
        transactions = TransactionService.load_transactions()
        
        if not transactions:
            st.info("No transactions found. Add some transactions to see them here.")
            return
        
        # Convert transactions to DataFrame
        df = pd.DataFrame(transactions)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            transaction_type_filter = st.multiselect(
                "Filter by Type", 
                options=["Income", "Expense"],
                default=["Income", "Expense"]
            )
        
        with col2:
            if 'category' in df.columns:
                categories = sorted(df['category'].unique())
                category_filter = st.multiselect(
                    "Filter by Category", 
                    options=categories,
                    default=[]
                )
            else:
                category_filter = []
        
        with col3:
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            else:
                date_range = None
        
        # Apply filters
        filtered_df = df.copy()
        
        if transaction_type_filter:
            filtered_df = filtered_df[filtered_df['type'].isin(transaction_type_filter)]
        
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'] >= pd.Timestamp(start_date)) & 
                (filtered_df['date'] <= pd.Timestamp(end_date))
            ]
        
        # Display transactions
        if not filtered_df.empty:
            # Convert date back to string for display
            display_df = filtered_df.copy()
            if 'date' in display_df.columns:
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            
            # Identify standard columns and additional data columns
            standard_columns = ['date', 'description', 'amount', 'type', 'category', 'payment_method']
            display_columns = [col for col in standard_columns if col in display_df.columns]
            
            # Check for additional data
            additional_columns = [col for col in display_df.columns if col not in standard_columns and col != 'additional_data']
            has_additional_data = len(additional_columns) > 0 or 'additional_data' in display_df.columns
            
            # Display standard columns
            st.dataframe(
                display_df[display_columns],
                column_config={
                    "amount": st.column_config.NumberColumn(
                        "Amount ($)",
                        format="$%.2f",
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Option to view additional data if available
            if has_additional_data:
                with st.expander("View Additional Transaction Data"):
                    # Create a list of transaction descriptions for selection
                    transaction_options = [
                        f"{row['date']} - {row['description']} (${float(row['amount']):.2f})"
                        for _, row in display_df.iterrows()
                    ]
                    
                    selected_index = st.selectbox(
                        "Select transaction to view details",
                        range(len(transaction_options)),
                        format_func=lambda i: transaction_options[i]
                    )
                    
                    if selected_index is not None:
                        row_data = display_df.iloc[selected_index]
                        st.subheader("Transaction Details")
                        
                        # Display additional columns
                        details = {}
                        
                        # Add columns that start with 'original_'
                        for col in additional_columns:
                            if col.startswith('original_'):
                                # Format the column name for display
                                display_name = col.replace('original_', '').replace('_', ' ').title()
                                details[display_name] = row_data[col]
                        
                        # Check for JSON in additional_data field
                        if 'additional_data' in row_data and row_data['additional_data']:
                            try:
                                additional_data = json.loads(row_data['additional_data'])
                                for key, value in additional_data.items():
                                    display_name = key.replace('_', ' ').title()
                                    details[display_name] = value
                            except:
                                details['Raw Additional Data'] = row_data['additional_data']
                        
                        if details:
                            st.json(details)
                        else:
                            st.info("No additional data available for this transaction.")
            
            # Add delete functionality
            if st.button("Delete Selected Transactions"):
                st.warning("Delete functionality would be implemented here")
        else:
            st.info("No transactions match your filters.")