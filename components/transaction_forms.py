"""
Modular transaction form components
"""
import streamlit as st
from datetime import date
from services.database_service import DatabaseService

class TransactionFormHandler:
    """Handles all transaction form operations"""
    
    @staticmethod
    def render_inline_form(description, default_amount, transaction_type, category, default_payment_method, form_key):
        """Render inline transaction form with validation and duplicate detection"""
        with st.container():
            st.markdown(f"**{description}**")
            amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"{form_key}_amount")
            transaction_date = st.date_input("Date", value=date.today(), key=f"{form_key}_date")
            payment_method = st.selectbox("Payment Method", [
                default_payment_method, "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
            ], key=f"{form_key}_payment")
            notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"{form_key}_notes")
            
            col_cancel, col_add = st.columns(2)
            with col_cancel:
                if st.button("Cancel", key=f"{form_key}_cancel"):
                    st.session_state[f"show_{form_key}_form"] = False
                    st.rerun()
            
            with col_add:
                if st.button("Add", type="primary", key=f"{form_key}_add"):
                    TransactionFormHandler._process_transaction(
                        description, amount, transaction_date, transaction_type, 
                        category, payment_method, notes, form_key
                    )
    
    @staticmethod
    def _process_transaction(description, amount, transaction_date, transaction_type, category, payment_method, notes, form_key):
        """Process transaction with validation and duplicate detection"""
        # Input validation
        if amount <= 0:
            st.error("Amount must be greater than zero")
            return
        elif not transaction_date:
            st.error("Date is required")
            return
        
        try:
            date_str = transaction_date.strftime('%Y-%m-%d')
            
            # Check for duplicates
            if TransactionFormHandler._check_duplicate(description, amount, date_str, category):
                st.warning(f"⚠️ Similar {description} already exists for {date_str}")
                return
            
            # Create transaction
            transaction = {
                'date': date_str,
                'amount': float(amount),
                'type': transaction_type,
                'description': f"{description}" + (f" - {notes}" if notes else ""),
                'category': category,
                'payment_method': payment_method
            }
            
            transaction_id = DatabaseService.add_transaction(transaction)
            st.success(f"✅ {description} added: ${amount:.2f}")
            
            # Clear session states
            TransactionFormHandler._clear_session_states()
            st.rerun()
            
        except Exception as e:
            st.error("Failed to add transaction. Please try again.")
            print(f"Transaction error: {str(e)}")
    
    @staticmethod
    def _check_duplicate(description, amount, date_str, category):
        """Check for duplicate transactions"""
        try:
            existing_transactions = DatabaseService.get_transactions()
            
            for txn in existing_transactions:
                if (txn.get('date') == date_str and 
                    txn.get('category') == category and
                    abs(float(txn.get('amount', 0)) - amount) < 0.01 and
                    description.lower() in txn.get('description', '').lower()):
                    return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def _clear_session_states():
        """Clear all form-related session states"""
        for key in list(st.session_state.keys()):
            if key.startswith(('show_', 'cached_')):
                del st.session_state[key]

class UtilitiesFormHandler:
    """Special handler for utilities with smart duplicate prevention"""
    
    @staticmethod
    def render_utilities_form(form_key):
        """Render utilities form with month-based duplicate detection"""
        from services.financial_data_service import TransactionService
        
        with st.container():
            st.markdown("**Utilities**")
            
            transaction_date = st.date_input("Date", value=date.today(), key=f"{form_key}_date")
            selected_month = transaction_date.strftime('%Y-%m')
            
            # Check existing utilities for selected month
            transactions = TransactionService.load_transactions()
            existing_utilities = set()
            for txn in transactions:
                if (txn.get('date', '').startswith(selected_month) and 
                    txn.get('category') == 'Utilities'):
                    desc = txn.get('description', '')
                    if 'Electric' in desc:
                        existing_utilities.add('Electric')
                    elif 'Phone' in desc:
                        existing_utilities.add('Phone')
                    elif 'Wifi' in desc or 'Internet' in desc:
                        existing_utilities.add('Wifi/Internet')
            
            # Available utility options
            all_utilities = ['Electric', 'Phone', 'Wifi/Internet']
            available_utilities = [u for u in all_utilities if u not in existing_utilities]
            
            if not available_utilities:
                st.warning(f"All utilities already added for {selected_month}")
                if st.button("Cancel", key=f"{form_key}_cancel"):
                    st.session_state[f"show_{form_key}_form"] = False
                    st.rerun()
            else:
                utility_type = st.selectbox("Utility Type", available_utilities, key=f"{form_key}_type")
                
                # Set default amounts
                default_amounts = {'Electric': 120.0, 'Phone': 50.0, 'Wifi/Internet': 80.0}
                default_amount = default_amounts.get(utility_type, 100.0)
                
                amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"{form_key}_amount")
                payment_method = st.selectbox("Payment Method", [
                    "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                ], key=f"{form_key}_payment")
                notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"{form_key}_notes")
                
                col_cancel, col_add = st.columns(2)
                with col_cancel:
                    if st.button("Cancel", key=f"{form_key}_cancel"):
                        st.session_state[f"show_{form_key}_form"] = False
                        st.rerun()
                
                with col_add:
                    if st.button("Add", type="primary", key=f"{form_key}_add"):
                        UtilitiesFormHandler._process_utility_transaction(
                            utility_type, amount, transaction_date, payment_method, notes, form_key
                        )
    
    @staticmethod
    def _process_utility_transaction(utility_type, amount, transaction_date, payment_method, notes, form_key):
        """Process utility transaction"""
        if amount <= 0:
            st.error("Amount must be greater than zero")
            return
        
        try:
            transaction = {
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': float(amount),
                'type': 'Expense',
                'description': f"{utility_type} Bill" + (f" - {notes}" if notes else ""),
                'category': 'Utilities',
                'payment_method': payment_method
            }
            
            transaction_id = DatabaseService.add_transaction(transaction)
            st.success(f"✅ {utility_type} added: ${amount:.2f}")
            
            # Clear session states
            for key in list(st.session_state.keys()):
                if key.startswith(('show_', 'cached_')):
                    del st.session_state[key]
            
            st.rerun()
            
        except Exception as e:
            st.error("Failed to add utility bill. Please try again.")
            print(f"Utility transaction error: {str(e)}")