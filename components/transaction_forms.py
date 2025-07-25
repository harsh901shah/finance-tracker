"""
Modular transaction form components
"""
import streamlit as st
import re
from datetime import date
from services.database_service import DatabaseService
from config.app_config import AppConfig
from utils.logger import AppLogger
from utils.auth_middleware import AuthMiddleware

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
            
            # Get current user ID or use default for now
            user_id = AuthMiddleware.get_current_user_id() or 'default_user'
            transaction_id = DatabaseService.add_transaction(transaction, user_id)
            st.success(f"✅ {description} added: ${amount:.2f}")
            
            # Clear session states
            TransactionFormHandler._clear_session_states()
            st.rerun()
            
        except Exception as e:
            AppLogger.log_error("Failed to add transaction", e, show_user=True)
    
    @staticmethod
    def _check_duplicate(description, amount, date_str, category):
        """Check for duplicate transactions"""
        try:
            # Get current user ID or use default for now
            user_id = AuthMiddleware.get_current_user_id() or 'default_user'
            existing_transactions = DatabaseService.get_transactions(user_id)
            
            for txn in existing_transactions:
                if (txn.get('date') == date_str and 
                    txn.get('category') == category and
                    abs(float(txn.get('amount', 0)) - amount) < 0.01 and
                    description.lower() in txn.get('description', '').lower()):
                    return True
            return False
        except Exception as e:
            AppLogger.log_error("Error checking duplicate transaction", e, show_user=False)
            return False
    
    @staticmethod
    def _clear_session_states():
        """Clear transaction form-related session states only"""
        form_prefixes = (
            'show_mortgage_form', 'show_utilities_form', 'show_salary_form',
            'show_car_loan_form', 'show_car_insurance_form', 'show_gas_form',
            'show_savings_transfer_form', 'show_robinhood_form', 'show_savings_withdraw_form',
            'show_gold_investment_form', 'show_money_india_form', 'show_401k_roth_form',
            'cached_transaction_data'
        )
        
        for key in list(st.session_state.keys()):
            if any(key.startswith(prefix) for prefix in form_prefixes):
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
                    desc = txn.get('description', '').lower()
                    
                    # Use regex patterns for robust utility type detection
                    utility_patterns = {
                        'Electric': r'\b(electric|electricity|power|energy|elec|pwr)\b',
                        'Phone': r'\b(phone|mobile|cellular|cell|tel|telephone)\b',
                        'Wifi/Internet': r'\b(wifi|internet|broadband|web|net|isp|wi-fi)\b',
                        'Water': r'\b(water|h2o|aqua|sewer|sewage)\b',
                        'Gas': r'\b(gas|natural gas|lng|propane)\b'
                    }
                    
                    # Find all matching utilities (allow multiple matches)
                    matched_utilities = []
                    for utility_type, pattern in utility_patterns.items():
                        if re.search(pattern, desc):
                            matched_utilities.append(utility_type)
                    
                    # Add the most specific match or first match if multiple
                    if matched_utilities:
                        # Prioritize more specific matches
                        priority_order = ['Electric', 'Gas', 'Water', 'Phone', 'Wifi/Internet']
                        for priority_util in priority_order:
                            if priority_util in matched_utilities:
                                existing_utilities.add(priority_util)
                                break
                        else:
                            existing_utilities.add(matched_utilities[0])
            
            # Available utility options from config
            all_utilities = list(AppConfig.UTILITY_TYPES.keys())
            available_utilities = [u for u in all_utilities if u not in existing_utilities]
            
            if not available_utilities:
                st.warning(f"All utilities already added for {selected_month}")
                if st.button("Cancel", key=f"{form_key}_cancel"):
                    st.session_state[f"show_{form_key}_form"] = False
                    st.rerun()
            else:
                utility_type = st.selectbox("Utility Type", available_utilities, key=f"{form_key}_type")
                
                # Set default amounts from config
                default_amount = AppConfig.UTILITY_TYPES.get(utility_type, 100.0)
                
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
            TransactionFormHandler._clear_session_states()
            
            st.rerun()
            
        except Exception as e:
            AppLogger.log_error("Failed to add utility bill", e, show_user=True)