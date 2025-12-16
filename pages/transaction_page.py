import streamlit as st
import pandas as pd
import json
from datetime import datetime
from services.financial_data_service import TransactionService
from services.database_service import DatabaseService
from services.tooltip_service import TooltipService
from services.logger_service import LoggerService
from utils.auth_middleware import AuthMiddleware


logger = LoggerService.get_logger("transaction_page")

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
        
        # Show contextual help
        TooltipService.show_contextual_help('view_transactions')
        
        # Resolve the current user once for consistent downstream use
        current_user = AuthMiddleware.get_current_user_id()
        if isinstance(current_user, dict) and 'user_id' in current_user:
            user_id = current_user['user_id']
        else:
            user_id = current_user or "default_user"
        undo_snapshots = DatabaseService.get_undo_snapshots(user_id)
        if undo_snapshots:
            with st.expander("↩️ Undo Recent Actions", expanded=False):
                for snapshot in undo_snapshots[:3]:  # Show last 3 undo options
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{snapshot['action'].replace('_', ' ').title()}** - {snapshot['created_at'][:16]}")
                    with col2:
                        if st.button("Undo", key=f"undo_{snapshot['id']}"):
                            if DatabaseService.restore_from_undo(snapshot['id'], user_id):
                                st.success("Action undone successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to undo action")
        
        # Load transactions
        # Clear cache to force fresh load
        TransactionService.clear_cache()
        transactions = TransactionService.load_transactions()

        logger.info("Loaded %d transactions for user_id=%s", len(transactions), user_id)

        if not transactions:
            st.info("No transactions found. Add some transactions to see them here.")
            st.info("💡 Click 'Add Transaction' in the sidebar to get started!")
            logger.info("No transactions found for user_id=%s", user_id)
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
            if 'amount' in df.columns and len(df) > 0:
                min_amount = float(df['amount'].min())
                max_amount = float(df['amount'].max())
                
                # Handle case where all amounts are the same
                if min_amount >= max_amount:
                    st.write(f"Amount: ${min_amount:.2f}")
                    amount_range = (min_amount, min_amount)
                else:
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
        
        # Apply filters in order: search -> type -> category -> amount -> date
        # This order optimizes performance by reducing dataset size progressively
        
        # Apply search filter across multiple fields
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
            
            # Bulk selection interface
            st.subheader("Select Transactions")
            selected_transactions = []
            
            # Select all checkbox
            select_all = st.checkbox("Select All Visible Transactions")
            
            # Display transactions table with selection and delete buttons
            for idx, row in display_df.iterrows():
                col1, col2, col3 = st.columns([1, 7, 1])
                
                with col1:
                    # Individual selection checkbox
                    is_selected = select_all or st.checkbox("Select", key=f"select_{row['id']}", label_visibility="collapsed")
                    if is_selected:
                        selected_transactions.append(row['id'])
                
                with col2:
                    # Display transaction info with tooltips
                    type_emoji = {"Income": "💰", "Expense": "💸", "Tax": "🏛️", "Transfer": "🔄", "Investment": "📈"}
                    emoji = type_emoji.get(row['type'], "📝")
                    st.write(f"{emoji} **{row['date']}** | {row['description']} | **${row['amount']:.2f}** | {row['type']} | {row['category']} | {row['payment_method']}")
                
                with col3:
                    # Delete button for individual transaction
                    if st.button("🗑️", key=f"delete_{row['id']}", help="Delete this transaction"):
                        st.write(f"Debug - Deleting transaction {row['id']} with user_id: {user_id} (type: {type(user_id)})")
                        if TransactionPage._delete_single_transaction(row['id'], user_id, dict(row)):
                            st.success("Transaction deleted! Check undo options above to restore.")
                            st.rerun()
                        else:
                            st.error("Failed to delete transaction")
                
                st.divider()
            
            # Bulk operations
            st.subheader("🔧 Bulk Operations")
            
            if selected_transactions:
                st.info(f"Selected {len(selected_transactions)} transactions")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete Selected", use_container_width=True, type="secondary"):
                        if st.session_state.get('confirm_bulk_delete'):
                            deleted_count = TransactionPage._bulk_delete_transactions(selected_transactions, user_id, display_df)
                            if deleted_count > 0:
                                st.success(f"Deleted {deleted_count} transactions! Check undo options to restore.")
                                st.rerun()
                            else:
                                st.error("Failed to delete transactions")
                            st.session_state['confirm_bulk_delete'] = False
                        else:
                            st.session_state['confirm_bulk_delete'] = True
                            st.warning(f"Click again to confirm deletion of {len(selected_transactions)} transactions")
                
                with col2:
                    if st.button("📊 Export Selected", use_container_width=True):
                        selected_df = display_df[display_df['id'].isin(selected_transactions)]
                        csv = selected_df.to_csv(index=False)
                        st.download_button(
                            label="Download Selected CSV",
                            data=csv,
                            file_name=f"selected_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            
            # Other bulk operations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export All", use_container_width=True):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Download All CSV",
                        data=csv,
                        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📈 View Summary", use_container_width=True):
                    TransactionPage._show_transaction_summary(filtered_df)
            
            with col3:
                if st.button("🔍 Advanced Filters", use_container_width=True):
                    st.info("Use the filters above to narrow down transactions")
            
            # Check for additional data columns
            standard_columns = ['date', 'description', 'amount', 'type', 'category', 'payment_method']
            additional_columns = [col for col in display_df.columns if col not in standard_columns and col != 'additional_data']
            has_additional_data = len(additional_columns) > 0 or 'additional_data' in display_df.columns
            
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
    def _delete_single_transaction(transaction_id, user_id, transaction_data):
        """Delete a single transaction with undo support"""
        try:
            # Create undo snapshot
            DatabaseService.create_undo_snapshot(user_id, 'DELETE_TRANSACTION', transaction_data)
            
            # Delete transaction
            return DatabaseService.delete_transaction(transaction_id, user_id)
        except Exception as e:
            st.error(f"Error deleting transaction: {e}")
            return False
    
    @staticmethod
    def _bulk_delete_transactions(transaction_ids, user_id, df):
        """Delete multiple transactions with undo support"""
        try:
            # Get transaction data for undo
            transactions_data = []
            for tid in transaction_ids:
                transaction_row = df[df['id'] == tid].iloc[0]
                transactions_data.append(dict(transaction_row))
            
            # Create undo snapshot
            DatabaseService.create_undo_snapshot(user_id, 'BULK_DELETE_TRANSACTIONS', {'transactions': transactions_data})
            
            # Delete transactions
            return DatabaseService.bulk_delete_transactions(transaction_ids, user_id)
        except Exception as e:
            st.error(f"Error deleting transactions: {e}")
            return 0
    
    @staticmethod
    def _show_transaction_summary(df):
        """Display comprehensive transaction analytics and breakdowns.
        
        Provides summary views by transaction type, category, and time period
        to help users understand their spending patterns.
        """
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