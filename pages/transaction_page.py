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
        st.header("📋 Transaction History")
        
        # Load transactions
        transactions = TransactionService.load_transactions()
        
        if not transactions:
            st.info("No transactions found. Add some transactions to see them here.")
            st.info("💡 Click 'Add Transaction' in the sidebar to get started!")
            return
        
        # Convert transactions to DataFrame
        df = pd.DataFrame(transactions)
        
        # Search and filters section
        st.subheader("🔍 Search & Filters")
        
        # Search bar
        search_term = st.text_input("🔍 Search transactions", placeholder="Search by description, amount, or category...")
        
        # Advanced filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Transaction type filter
            all_types = sorted(df['type'].unique()) if 'type' in df.columns else []
            transaction_type_filter = st.multiselect(
                "Type", 
                options=all_types,
                default=all_types
            )
        
        with col2:
            # Category filter
            if 'category' in df.columns:
                categories = sorted(df['category'].unique())
                category_filter = st.multiselect(
                    "Category", 
                    options=categories,
                    default=[]
                )
            else:
                category_filter = []
        
        with col3:
            # Amount range filter
            if 'amount' in df.columns:
                min_amount = float(df['amount'].min())
                max_amount = float(df['amount'].max())
                amount_range = st.slider(
                    "Amount Range ($)",
                    min_value=min_amount,
                    max_value=max_amount,
                    value=(min_amount, max_amount),
                    step=1.0
                )
            else:
                amount_range = None
        
        with col4:
            # Date range filter
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
        
        # Apply search filter
        if search_term:
            search_mask = (
                filtered_df['description'].str.contains(search_term, case=False, na=False) |
                filtered_df['category'].str.contains(search_term, case=False, na=False) |
                filtered_df['amount'].astype(str).str.contains(search_term, na=False)
            )
            filtered_df = filtered_df[search_mask]
        
        # Apply type filter
        if transaction_type_filter:
            filtered_df = filtered_df[filtered_df['type'].isin(transaction_type_filter)]
        
        # Apply category filter
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        
        # Apply amount range filter
        if amount_range:
            min_amt, max_amt = amount_range
            filtered_df = filtered_df[
                (filtered_df['amount'] >= min_amt) & 
                (filtered_df['amount'] <= max_amt)
            ]
        
        # Apply date range filter
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'] >= pd.Timestamp(start_date)) & 
                (filtered_df['date'] <= pd.Timestamp(end_date))
            ]
        
        # Display results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Transactions Found", len(filtered_df))
        with col2:
            if not filtered_df.empty:
                total_amount = filtered_df['amount'].sum()
                st.metric("💰 Total Amount", f"${total_amount:,.2f}")
        with col3:
            if not filtered_df.empty:
                avg_amount = filtered_df['amount'].mean()
                st.metric("📈 Average Amount", f"${avg_amount:,.2f}")
        
        # Display transactions
        if not filtered_df.empty:
            # Sort options
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.subheader("📋 Transactions")
            with col2:
                sort_by = st.selectbox("Sort by", ["date", "amount", "description", "category", "type"])
            with col3:
                sort_order = st.selectbox("Order", ["Descending", "Ascending"])
            
            # Apply sorting
            ascending = sort_order == "Ascending"
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            
            # Convert date back to string for display
            display_df = filtered_df.copy()
            if 'date' in display_df.columns:
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            
            # Identify standard columns
            standard_columns = ['date', 'description', 'amount', 'type', 'category', 'payment_method']
            display_columns = [col for col in standard_columns if col in display_df.columns]
            
            # Display transactions table
            st.dataframe(
                display_df[display_columns],
                column_config={
                    "date": st.column_config.DateColumn("Date"),
                    "description": st.column_config.TextColumn("Description", width="large"),
                    "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
                    "type": st.column_config.TextColumn("Type"),
                    "category": st.column_config.TextColumn("Category"),
                    "payment_method": st.column_config.TextColumn("Payment Method")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Bulk operations
            st.subheader("🔧 Bulk Operations")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export to CSV", use_container_width=True):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📈 View Summary", use_container_width=True):
                    TransactionPage._show_transaction_summary(filtered_df)
            
            with col3:
                if st.button("🗑️ Delete Selected", use_container_width=True, type="secondary"):
                    st.warning("Select transactions to delete (feature coming soon)")
            
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
            
        else:
            st.info("No transactions match your filters.")
            st.info("💡 Try adjusting your search terms or filters.")
    
    @staticmethod
    def _show_transaction_summary(df):
        """Show detailed transaction summary"""
        st.subheader("📊 Transaction Summary")
        
        # Summary by type
        type_summary = df.groupby('type')['amount'].agg(['count', 'sum', 'mean']).round(2)
        st.write("**By Type:**")
        st.dataframe(type_summary, column_config={
            "count": "Count",
            "sum": st.column_config.NumberColumn("Total ($)", format="$%.2f"),
            "mean": st.column_config.NumberColumn("Average ($)", format="$%.2f")
        })
        
        # Summary by category
        if 'category' in df.columns:
            category_summary = df.groupby('category')['amount'].agg(['count', 'sum', 'mean']).round(2)
            st.write("**By Category:**")
            st.dataframe(category_summary, column_config={
                "count": "Count",
                "sum": st.column_config.NumberColumn("Total ($)", format="$%.2f"),
                "mean": st.column_config.NumberColumn("Average ($)", format="$%.2f")
            })
        
        # Monthly summary
        if 'date' in df.columns:
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
            monthly_summary = df.groupby('month')['amount'].agg(['count', 'sum']).round(2)
            st.write("**By Month:**")
            st.dataframe(monthly_summary, column_config={
                "count": "Count",
                "sum": st.column_config.NumberColumn("Total ($)", format="$%.2f")
            })