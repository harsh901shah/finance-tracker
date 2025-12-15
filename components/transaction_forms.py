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
            if default_amount > 0:
                amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"{form_key}_amount")
            else:
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, key=f"{form_key}_amount")
            transaction_date = st.date_input("Date", value=date.today(), key=f"{form_key}_date")
            # Create payment method list using constants
            from config.constants import PaymentMethods
            payment_methods = PaymentMethods.DEFAULT.copy()
            
            # Normalize default payment method
            normalized_default = PaymentMethods.normalize(default_payment_method)
            
            if normalized_default not in payment_methods:
                payment_methods.insert(0, normalized_default)
            else:
                # Move default to front if it exists in the list
                payment_methods.remove(normalized_default)
                payment_methods.insert(0, normalized_default)
            
            payment_method = st.selectbox("Payment Method", payment_methods, key=f"{form_key}_payment")
            notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"{form_key}_notes")
            
            col_cancel, col_add = st.columns(2)
            with col_cancel:
                if st.button("Cancel", key=f"{form_key}_cancel"):
                    st.session_state[f"show_{form_key}_form"] = False
                    st.rerun()
            
            with col_add:
                if st.button("Add", type="primary", key=f"{form_key}_add"):
                    final_amount = amount
                    TransactionFormHandler._process_transaction(
                        description, final_amount, transaction_date, transaction_type, 
                        category, payment_method, notes, form_key
                    )
    
    @staticmethod
    def _process_transaction(description, amount, transaction_date, transaction_type, category, payment_method, notes, form_key):
        """Process transaction with validation and duplicate detection"""
        from utils.validation import InputValidator
        
        # Comprehensive validation
        transaction_data = {
            'amount': amount,
            'description': description,
            'date': transaction_date,
            'type': transaction_type
        }
        
        is_valid, errors = InputValidator.validate_transaction_data(transaction_data)
        if not is_valid:
            for error in errors:
                st.error(error)
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
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
            transaction_id = DatabaseService.add_transaction(transaction, user_id)
            
            # Auto-update net worth based on transaction
            TransactionFormHandler._update_networth_from_transaction(transaction, user_id)
            
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
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
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
    def _update_networth_from_transaction(transaction, user_id):
        """Automatically update net worth based on transaction type"""
        try:
            from services.database_service import DatabaseService
            
            amount = float(transaction.get('amount', 0))
            transaction_type = transaction.get('type', '').lower()
            description = transaction.get('description', '').lower()
            
            assets = DatabaseService.get_assets(user_id)
            
            # Income - add to checking account
            if transaction_type == 'income':
                for asset in assets:
                    if 'checking' in asset.get('name', '').lower():
                        new_value = asset.get('value', 0) + amount
                        DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
                        return
            
            # Expense - subtract from checking account
            elif transaction_type == 'expense':
                for asset in assets:
                    if 'checking' in asset.get('name', '').lower():
                        new_value = max(0, asset.get('value', 0) - amount)
                        DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
                        return
            
            # Transfer - handle specific transfers
            elif transaction_type == 'transfer':
                if '401k' in description:
                    for asset in assets:
                        if '401k' in asset.get('name', '').lower():
                            new_value = asset.get('value', 0) + amount
                            DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
                        elif 'checking' in asset.get('name', '').lower():
                            new_value = max(0, asset.get('value', 0) - amount)
                            DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
                elif 'investment' in description:
                    for asset in assets:
                        if 'investment' in asset.get('name', '').lower():
                            new_value = asset.get('value', 0) + amount
                            DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
                        elif 'checking' in asset.get('name', '').lower():
                            new_value = max(0, asset.get('value', 0) - amount)
                            DatabaseService.update_asset(asset['id'], new_value, transaction.get('date'))
            
        except Exception as e:
            logger.warning(f"Could not update net worth: {e}")
    
    @staticmethod
    def _clear_session_states():
        """Clear transaction form-related session states only"""
        form_prefixes = (
            'show_mortgage_form', 'show_utilities_form', 'show_salary_form',
            'show_car_loan_form', 'show_car_insurance_form', 'show_gas_form',
            'show_savings_transfer_form', 'show_robinhood_form', 'show_savings_withdraw_form',
            'show_gold_investment_form', 'show_money_india_form', 'show_401k_roth_form',
            'show_property_tax_form', 'cached_transaction_data'
        )
        
        for key in list(st.session_state.keys()):
            if any(key.startswith(prefix) for prefix in form_prefixes) and 'property_tax' not in key:
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
                payment_method = st.selectbox("Payment Method", 
                    AppConfig.PaymentMethods.DEFAULT, key=f"{form_key}_payment")
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
            
            # Get current user ID
            current_user = AuthMiddleware.get_current_user_id()
            user_id = str(current_user.get('user_id') if isinstance(current_user, dict) else current_user or 'default_user')
            transaction_id = DatabaseService.add_transaction(transaction, user_id)
            
            # Auto-update net worth based on transaction
            TransactionFormHandler._update_networth_from_transaction(transaction, user_id)
            
            st.success(f"✅ {utility_type} added: ${amount:.2f}")
            
            # Clear session states
            TransactionFormHandler._clear_session_states()
            
            st.rerun()
            
        except Exception as e:
            AppLogger.log_error("Failed to add utility bill", e, show_user=True)