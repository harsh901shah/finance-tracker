import streamlit as st
from datetime import datetime, date
from services.database_service import DatabaseService
from components.transaction_forms import TransactionFormHandler, UtilitiesFormHandler
from components.user_preferences import UserPreferencesManager
from config.app_config import AppConfig

class AddTransactionPage:
    @staticmethod
    def show():
        # Apply custom CSS for professional styling
        AddTransactionPage._apply_custom_css()
        
        st.header("💰 Add Transaction")
        
        # Quick add buttons for your specific categories
        st.subheader("Quick Add")
        
        # Income section
        with st.expander("💰 Income", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💰 Monthly Salary", use_container_width=True, key="salary_btn"):
                    st.session_state.show_salary_form = True
                
                # Show salary form inline
                if st.session_state.get('show_salary_form', False):
                    with st.container():
                        st.markdown("**Monthly Salary**")
                        amount = st.number_input("Amount ($)", value=5000.0, step=0.01, key="salary_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="salary_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="salary_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="salary_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="salary_cancel"):
                                st.session_state.show_salary_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="salary_add"):
                                TransactionFormHandler._process_transaction(
                                    "Monthly Salary", amount, transaction_date, "Income", 
                                    "Salary", payment_method, notes, "salary"
                                )
                
                if st.button("🏦 Interest Income", use_container_width=True, key="interest_btn"):
                    st.session_state.show_interest_form = True
                
                # Show interest form inline
                if st.session_state.get('show_interest_form', False):
                    with st.container():
                        st.markdown("**Interest Income**")
                        amount = st.number_input("Amount ($)", value=50.0, step=0.01, key="interest_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="interest_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Direct Deposit", "Credit Card", "Cash", "Check"
                        ], key="interest_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="interest_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="interest_cancel"):
                                st.session_state.show_interest_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="interest_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"Interest Income" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Interest Income added: ${amount:.2f}")
                                st.session_state.show_interest_form = False
                                st.rerun()
            
            with col2:
                if st.button("📈 BOX STOCKS ESPP", use_container_width=True, key="espp_btn"):
                    st.session_state.show_espp_form = True
                
                # Show ESPP form inline
                if st.session_state.get('show_espp_form', False):
                    with st.container():
                        st.markdown("**BOX STOCKS ESPP**")
                        amount = st.number_input("Amount ($)", value=1000.0, step=0.01, key="espp_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="espp_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="espp_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="espp_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="espp_cancel"):
                                st.session_state.show_espp_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="espp_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"BOX STOCKS ESPP" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ BOX STOCKS ESPP added: ${amount:.2f}")
                                st.session_state.show_espp_form = False
                                st.rerun()
                if st.button("💸 Tax Refund", use_container_width=True, key="tax_refund_btn"):
                    st.session_state.show_tax_refund_form = True
                
                # Show tax refund form inline
                if st.session_state.get('show_tax_refund_form', False):
                    with st.container():
                        st.markdown("**Tax Refund**")
                        amount = st.number_input("Amount ($)", value=800.0, step=0.01, key="tax_refund_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="tax_refund_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Check", "Credit Card", "Cash"
                        ], key="tax_refund_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="tax_refund_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="tax_refund_cancel"):
                                st.session_state.show_tax_refund_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="tax_refund_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"Tax Refund" + (f" - {notes}" if notes else ""),
                                    'category': 'Tax',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Tax Refund added: ${amount:.2f}")
                                st.session_state.show_tax_refund_form = False
                                st.rerun()
            
            with col3:
                if st.button("📊 BOX RSU", use_container_width=True, key="rsu_btn"):
                    st.session_state.show_rsu_form = True
                
                # Show RSU form inline
                if st.session_state.get('show_rsu_form', False):
                    with st.container():
                        st.markdown("**BOX RSU**")
                        amount = st.number_input("Amount ($)", value=2000.0, step=0.01, key="rsu_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="rsu_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="rsu_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="rsu_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="rsu_cancel"):
                                st.session_state.show_rsu_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="rsu_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"BOX RSU" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ BOX RSU added: ${amount:.2f}")
                                st.session_state.show_rsu_form = False
                                st.rerun()
                
                if st.button("💹 BOX ESPP PROFIT", use_container_width=True, key="espp_profit_btn"):
                    st.session_state.show_espp_profit_form = True
                
                # Show ESPP Profit form inline
                if st.session_state.get('show_espp_profit_form', False):
                    with st.container():
                        st.markdown("**BOX ESPP PROFIT**")
                        amount = st.number_input("Amount ($)", value=500.0, step=0.01, key="espp_profit_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="espp_profit_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="espp_profit_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="espp_profit_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="espp_profit_cancel"):
                                st.session_state.show_espp_profit_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="espp_profit_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"BOX ESPP PROFIT" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ BOX ESPP PROFIT added: ${amount:.2f}")
                                st.session_state.show_espp_profit_form = False
                                st.rerun()
        
        # Deductions section
        with st.expander("🏛️ Deductions"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏛️ TAXES PAID", use_container_width=True, key="taxes_paid_btn"):
                    st.session_state.show_taxes_paid_form = True
                
                # Show taxes paid form inline
                if st.session_state.get('show_taxes_paid_form', False):
                    with st.container():
                        st.markdown("**TAXES PAID**")
                        amount = st.number_input("Amount ($)", value=1200.0, step=0.01, key="taxes_paid_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="taxes_paid_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="taxes_paid_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="taxes_paid_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="taxes_paid_cancel"):
                                st.session_state.show_taxes_paid_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="taxes_paid_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"TAXES PAID" + (f" - {notes}" if notes else ""),
                                    'category': 'Tax',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ TAXES PAID added: ${amount:.2f}")
                                st.session_state.show_taxes_paid_form = False
                                st.rerun()
            
            with col2:
                if st.button("🏦 401K Pretax", use_container_width=True, key="401k_pretax_btn"):
                    st.session_state.show_401k_pretax_form = True
                
                # Show 401K pretax form inline
                if st.session_state.get('show_401k_pretax_form', False):
                    with st.container():
                        st.markdown("**401K Pretax**")
                        amount = st.number_input("Amount ($)", value=800.0, step=0.01, key="401k_pretax_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="401k_pretax_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="401k_pretax_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="401k_pretax_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="401k_pretax_cancel"):
                                st.session_state.show_401k_pretax_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="401k_pretax_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"401K Pretax" + (f" - {notes}" if notes else ""),
                                    'category': 'Retirement',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ 401K Pretax added: ${amount:.2f}")
                                st.session_state.show_401k_pretax_form = False
                                st.rerun()
            
            with col3:
                if st.button("🏥 HSA", use_container_width=True, key="hsa_btn"):
                    st.session_state.show_hsa_form = True
                
                # Show HSA form inline
                if st.session_state.get('show_hsa_form', False):
                    with st.container():
                        st.markdown("**HSA**")
                        amount = st.number_input("Amount ($)", value=300.0, step=0.01, key="hsa_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="hsa_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="hsa_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="hsa_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="hsa_cancel"):
                                st.session_state.show_hsa_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="hsa_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Income',
                                    'description': f"HSA" + (f" - {notes}" if notes else ""),
                                    'category': 'Healthcare',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ HSA added: ${amount:.2f}")
                                st.session_state.show_hsa_form = False
                                st.rerun()
        
        # Housing expenses
        with st.expander("🏠 Housing"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏠 Mortgage", use_container_width=True, key="mortgage_btn"):
                    st.session_state.show_mortgage_form = True
                
                # Show mortgage form inline
                if st.session_state.get('show_mortgage_form', False):
                    TransactionFormHandler.render_inline_form(
                        "Mortgage Payment", 2500.0, "Expense", "Housing", "Bank Transfer", "mortgage"
                    )
                
                if st.button("🏢 HOA", use_container_width=True, key="hoa_btn"):
                    st.session_state.show_hoa_form = True
                
                # Show HOA form inline
                if st.session_state.get('show_hoa_form', False):
                    with st.container():
                        st.markdown("**HOA Fee**")
                        amount = st.number_input("Amount ($)", value=100.0, step=0.01, key="hoa_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="hoa_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="hoa_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="hoa_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="hoa_cancel"):
                                st.session_state.show_hoa_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="hoa_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"HOA Fee" + (f" - {notes}" if notes else ""),
                                    'category': 'Housing',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ HOA Fee added: ${amount:.2f}")
                                st.session_state.show_hoa_form = False
                                st.rerun()
            
            with col2:
                if st.button("🏘️ PROPERTY TAX", use_container_width=True, key="property_tax_btn"):
                    st.session_state.show_property_tax_form = True
                
                # Show property tax form inline
                if st.session_state.get('show_property_tax_form', False):
                    with st.container():
                        st.markdown("**Property Tax**")
                        amount = st.number_input("Amount ($)", value=400.0, step=0.01, key="property_tax_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="property_tax_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="property_tax_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="property_tax_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="property_tax_cancel"):
                                st.session_state.show_property_tax_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="property_tax_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Property Tax" + (f" - {notes}" if notes else ""),
                                    'category': 'Housing',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Property Tax added: ${amount:.2f}")
                                st.session_state.show_property_tax_form = False
                                st.rerun()
                
                if st.button("🛋️ Furniture", use_container_width=True, key="furniture_btn"):
                    st.session_state.show_furniture_form = True
                
                # Show furniture form inline
                if st.session_state.get('show_furniture_form', False):
                    with st.container():
                        st.markdown("**Furniture Purchase**")
                        amount = st.number_input("Amount ($)", value=800.0, step=0.01, key="furniture_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="furniture_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Credit Card", "Bank Transfer", "Cash", "Check", "Direct Deposit"
                        ], key="furniture_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="furniture_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="furniture_cancel"):
                                st.session_state.show_furniture_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="furniture_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Furniture Purchase" + (f" - {notes}" if notes else ""),
                                    'category': 'Shopping',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Furniture Purchase added: ${amount:.2f}")
                                st.session_state.show_furniture_form = False
                                st.rerun()
            
            with col3:
                if st.button("⚡ Utilities", use_container_width=True, key="utilities_btn"):
                    st.session_state.show_utilities_form = True
                
                # Show utilities form inline
                if st.session_state.get('show_utilities_form', False):
                    UtilitiesFormHandler.render_utilities_form("utilities")
                
                if st.button("💎 Jewelry", use_container_width=True, key="jewelry_btn"):
                    st.session_state.show_jewelry_form = True
                
                # Show jewelry form inline
                if st.session_state.get('show_jewelry_form', False):
                    with st.container():
                        st.markdown("**Jewelry Purchase**")
                        amount = st.number_input("Amount ($)", value=500.0, step=0.01, key="jewelry_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="jewelry_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Credit Card", "Bank Transfer", "Cash", "Check", "Direct Deposit"
                        ], key="jewelry_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="jewelry_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="jewelry_cancel"):
                                st.session_state.show_jewelry_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="jewelry_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Jewelry Purchase" + (f" - {notes}" if notes else ""),
                                    'category': 'Shopping',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Jewelry Purchase added: ${amount:.2f}")
                                st.session_state.show_jewelry_form = False
                                st.rerun()
        
        # Transportation expenses
        with st.expander("🚗 Transportation"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🚗 Car Loan", use_container_width=True, key="car_loan_btn"):
                    st.session_state.show_car_loan_form = True
                
                # Show car loan form inline
                if st.session_state.get('show_car_loan_form', False):
                    with st.container():
                        st.markdown("**Car Loan Payment**")
                        amount = st.number_input("Amount ($)", value=450.0, step=0.01, key="car_loan_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="car_loan_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="car_loan_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="car_loan_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="car_loan_cancel"):
                                st.session_state.show_car_loan_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="car_loan_add"):
                                TransactionFormHandler._process_transaction(
                                    "Car Loan Payment", amount, transaction_date, "Expense", 
                                    "Transportation", payment_method, notes, "car_loan"
                                )
            
            with col2:
                if st.button("🚙 Car Insurance", use_container_width=True, key="car_insurance_btn"):
                    st.session_state.show_car_insurance_form = True
                
                # Show car insurance form inline
                if st.session_state.get('show_car_insurance_form', False):
                    with st.container():
                        st.markdown("**Car Insurance**")
                        amount = st.number_input("Amount ($)", value=150.0, step=0.01, key="car_insurance_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="car_insurance_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="car_insurance_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="car_insurance_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="car_insurance_cancel"):
                                st.session_state.show_car_insurance_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="car_insurance_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Car Insurance" + (f" - {notes}" if notes else ""),
                                    'category': 'Transportation',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Car Insurance added: ${amount:.2f}")
                                st.session_state.show_car_insurance_form = False
                                st.rerun()
            
            with col3:
                if st.button("⛽ Gas", use_container_width=True, key="gas_btn"):
                    st.session_state.show_gas_form = True
                
                # Show gas form inline
                if st.session_state.get('show_gas_form', False):
                    with st.container():
                        st.markdown("**Gas Fill-up**")
                        amount = st.number_input("Amount ($)", value=60.0, step=0.01, key="gas_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="gas_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Credit Card", "Cash", "Bank Transfer", "Check", "Direct Deposit"
                        ], key="gas_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="gas_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="gas_cancel"):
                                st.session_state.show_gas_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="gas_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Gas Fill-up" + (f" - {notes}" if notes else ""),
                                    'category': 'Transportation',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Gas Fill-up added: ${amount:.2f}")
                                st.session_state.show_gas_form = False
                                st.rerun()
        
        # Credit & Debt
        with st.expander("💳 Credit & Debt"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💳 DISCOVER DEBT", use_container_width=True, key="discover_debt_btn"):
                    st.session_state.show_discover_debt_form = True
                
                # Show discover debt form inline
                if st.session_state.get('show_discover_debt_form', False):
                    with st.container():
                        st.markdown("**Discover Credit Card Payment**")
                        amount = st.number_input("Amount ($)", value=300.0, step=0.01, key="discover_debt_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="discover_debt_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="discover_debt_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="discover_debt_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="discover_debt_cancel"):
                                st.session_state.show_discover_debt_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="discover_debt_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Discover Credit Card Payment" + (f" - {notes}" if notes else ""),
                                    'category': 'Credit Card',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Discover Credit Card Payment added: ${amount:.2f}")
                                st.session_state.show_discover_debt_form = False
                                st.rerun()
            
            with col2:
                if st.button("💳 Credit Card Payment", use_container_width=True, key="credit_card_payment_btn"):
                    st.session_state.show_credit_card_payment_form = True
                
                # Show credit card payment form inline
                if st.session_state.get('show_credit_card_payment_form', False):
                    with st.container():
                        st.markdown("**Credit Card Payment**")
                        amount = st.number_input("Amount ($)", value=200.0, step=0.01, key="credit_card_payment_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="credit_card_payment_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="credit_card_payment_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="credit_card_payment_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="credit_card_payment_cancel"):
                                st.session_state.show_credit_card_payment_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="credit_card_payment_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Credit Card Payment" + (f" - {notes}" if notes else ""),
                                    'category': 'Credit Card',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Credit Card Payment added: ${amount:.2f}")
                                st.session_state.show_credit_card_payment_form = False
                                st.rerun()
            
            with col3:
                if st.button("🏠 Extra Principal", use_container_width=True, key="extra_principal_btn"):
                    st.session_state.show_extra_principal_form = True
                
                # Show extra principal form inline
                if st.session_state.get('show_extra_principal_form', False):
                    with st.container():
                        st.markdown("**Extra Principal Payment**")
                        amount = st.number_input("Amount ($)", value=300.0, step=0.01, key="extra_principal_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="extra_principal_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="extra_principal_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="extra_principal_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="extra_principal_cancel"):
                                st.session_state.show_extra_principal_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="extra_principal_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Expense',
                                    'description': f"Extra Principal Payment" + (f" - {notes}" if notes else ""),
                                    'category': 'Housing',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Extra Principal Payment added: ${amount:.2f}")
                                st.session_state.show_extra_principal_form = False
                                st.rerun()
        
        # Investments & Transfers
        with st.expander("📈 Investments & Transfers"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💰 Savings Transfer", use_container_width=True, key="savings_transfer_btn"):
                    st.session_state.show_savings_transfer_form = True
                
                # Show savings transfer form inline
                if st.session_state.get('show_savings_transfer_form', False):
                    with st.container():
                        st.markdown("**Savings Bank Transfer**")
                        amount = st.number_input("Amount ($)", value=1000.0, step=0.01, key="savings_transfer_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="savings_transfer_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="savings_transfer_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="savings_transfer_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="savings_transfer_cancel"):
                                st.session_state.show_savings_transfer_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="savings_transfer_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Transfer',
                                    'description': f"Savings Bank Transfer" + (f" - {notes}" if notes else ""),
                                    'category': 'Savings',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Savings Bank Transfer added: ${amount:.2f}")
                                st.session_state.show_savings_transfer_form = False
                                st.rerun()
                
                if st.button("📈 ROBINHOOD", use_container_width=True, key="robinhood_btn"):
                    st.session_state.show_robinhood_form = True
                
                # Show robinhood form inline
                if st.session_state.get('show_robinhood_form', False):
                    with st.container():
                        st.markdown("**Robinhood Investment**")
                        amount = st.number_input("Amount ($)", value=500.0, step=0.01, key="robinhood_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="robinhood_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="robinhood_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="robinhood_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="robinhood_cancel"):
                                st.session_state.show_robinhood_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="robinhood_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Investment',
                                    'description': f"Robinhood Investment" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Robinhood Investment added: ${amount:.2f}")
                                st.session_state.show_robinhood_form = False
                                st.rerun()
            
            with col2:
                if st.button("💸 Savings Withdraw", use_container_width=True, key="savings_withdraw_btn"):
                    st.session_state.show_savings_withdraw_form = True
                
                # Show savings withdraw form inline
                if st.session_state.get('show_savings_withdraw_form', False):
                    with st.container():
                        st.markdown("**Savings Bank Withdraw**")
                        amount = st.number_input("Amount ($)", value=500.0, step=0.01, key="savings_withdraw_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="savings_withdraw_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="savings_withdraw_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="savings_withdraw_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="savings_withdraw_cancel"):
                                st.session_state.show_savings_withdraw_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="savings_withdraw_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Transfer',
                                    'description': f"Savings Bank Withdraw" + (f" - {notes}" if notes else ""),
                                    'category': 'Savings',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Savings Bank Withdraw added: ${amount:.2f}")
                                st.session_state.show_savings_withdraw_form = False
                                st.rerun()
                
                if st.button("🥇 GOLD Investment", use_container_width=True, key="gold_investment_btn"):
                    st.session_state.show_gold_investment_form = True
                
                # Show gold investment form inline
                if st.session_state.get('show_gold_investment_form', False):
                    with st.container():
                        st.markdown("**Gold Investment**")
                        amount = st.number_input("Amount ($)", value=200.0, step=0.01, key="gold_investment_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="gold_investment_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="gold_investment_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="gold_investment_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="gold_investment_cancel"):
                                st.session_state.show_gold_investment_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="gold_investment_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Investment',
                                    'description': f"Gold Investment" + (f" - {notes}" if notes else ""),
                                    'category': 'Investment',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Gold Investment added: ${amount:.2f}")
                                st.session_state.show_gold_investment_form = False
                                st.rerun()
            
            with col3:
                if st.button("🌏 Money to India", use_container_width=True, key="money_india_btn"):
                    st.session_state.show_money_india_form = True
                
                # Show money to India form inline
                if st.session_state.get('show_money_india_form', False):
                    with st.container():
                        st.markdown("**Money Sent India**")
                        amount = st.number_input("Amount ($)", value=1000.0, step=0.01, key="money_india_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="money_india_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                        ], key="money_india_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="money_india_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="money_india_cancel"):
                                st.session_state.show_money_india_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="money_india_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Transfer',
                                    'description': f"Money Sent India" + (f" - {notes}" if notes else ""),
                                    'category': 'Transfer',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ Money Sent India added: ${amount:.2f}")
                                st.session_state.show_money_india_form = False
                                st.rerun()
                if st.button("🏦 401k Roth", use_container_width=True, key="401k_roth_btn"):
                    st.session_state.show_401k_roth_form = True
                
                # Show 401k Roth form inline
                if st.session_state.get('show_401k_roth_form', False):
                    with st.container():
                        st.markdown("**401k Roth Contribution**")
                        amount = st.number_input("Amount ($)", value=500.0, step=0.01, key="401k_roth_amount")
                        transaction_date = st.date_input("Date", value=date.today(), key="401k_roth_date")
                        payment_method = st.selectbox("Payment Method", [
                            "Direct Deposit", "Bank Transfer", "Credit Card", "Cash", "Check"
                        ], key="401k_roth_payment")
                        notes = st.text_input("Notes (optional)", placeholder="Add details here...", key="401k_roth_notes")
                        
                        col_cancel, col_add = st.columns(2)
                        with col_cancel:
                            if st.button("Cancel", key="401k_roth_cancel"):
                                st.session_state.show_401k_roth_form = False
                                st.rerun()
                        with col_add:
                            if st.button("Add", type="primary", key="401k_roth_add"):
                                transaction = {
                                    'date': transaction_date.strftime('%Y-%m-%d'),
                                    'amount': float(amount),
                                    'type': 'Investment',
                                    'description': f"401k Roth Contribution" + (f" - {notes}" if notes else ""),
                                    'category': 'Retirement',
                                    'payment_method': payment_method
                                }
                                transaction_id = DatabaseService.add_transaction(transaction)
                                st.success(f"✅ 401k Roth Contribution added: ${amount:.2f}")
                                st.session_state.show_401k_roth_form = False
                                st.rerun()
        
        # Settings section - only show if customization features are enabled
        if AppConfig.FEATURES.get('custom_categories', True) or AppConfig.FEATURES.get('custom_payment_methods', True):
            UserPreferencesManager.render_settings_panel()
        
        # Manual entry form
        st.subheader("Manual Entry")
        
        with st.form("manual_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_date = st.date_input("Date", value=date.today())
                transaction_type = st.selectbox("Type", ["Income", "Expense", "Investment", "Transfer"])
                amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=0.01)
            
            with col2:
                description = st.text_input("Description", placeholder="Enter description...")
                # Use custom categories and payment methods
                all_categories = UserPreferencesManager.get_all_categories()
                category = st.selectbox("Category", all_categories)
                
                all_payment_methods = UserPreferencesManager.get_all_payment_methods()
                default_payment = UserPreferencesManager.get_default_payment_method()
                default_index = all_payment_methods.index(default_payment) if default_payment in all_payment_methods else 0
                payment_method = st.selectbox("Payment Method", all_payment_methods, index=default_index)
            
            if st.form_submit_button("Add Transaction", type="primary", use_container_width=True):
                # Input validation
                if not description.strip():
                    st.error("Description is required")
                elif amount <= 0:
                    st.error("Amount must be greater than zero")
                elif not transaction_date:
                    st.error("Date is required")
                else:
                    try:
                        transaction = {
                            'date': transaction_date.strftime('%Y-%m-%d'),
                            'amount': float(amount),
                            'type': transaction_type,
                            'description': description.strip(),
                            'category': category,
                            'payment_method': payment_method
                        }
                        
                        # Get current user ID - require authentication
                        user_id = AuthMiddleware.get_current_user_id()
                        if not user_id:
                            st.error("🔒 Please login to add transactions")
                            return
                        transaction_id = DatabaseService.add_transaction(transaction, user_id)
                        st.success(f"✅ Transaction added successfully!")
                        
                        # Clear all session states
                        for key in list(st.session_state.keys()):
                            if key.startswith(('show_', 'cached_')):
                                del st.session_state[key]
                        
                        st.rerun()
                    except Exception as e:
                        st.error("Failed to add transaction. Please try again.")
                        print(f"Manual transaction error: {str(e)}")  # Log for debugging
        

        
        # Monthly summary
        st.subheader("📊 This Month Summary")
        AddTransactionPage._show_monthly_summary()
    
    @staticmethod
    def _quick_add(description, default_amount, transaction_type, category):
        """Quick add transaction with modal"""
        # Use session state to show modal
        modal_key = f"modal_{description.replace(' ', '_')}"
        
        if modal_key not in st.session_state:
            st.session_state[modal_key] = True
        
        # Show form in expander with clean layout
        with st.expander(f"Add {description}", expanded=True):
            with st.form(f"quick_add_{description.replace(' ', '_')}"):
                st.markdown(f"**{description}**")
                st.markdown("---")
                
                # Simple stacked layout
                amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"amount_{modal_key}")
                transaction_date = st.date_input("Date", value=date.today(), key=f"date_{modal_key}")
                payment_method = st.selectbox("Payment Method", [
                    "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                ], key=f"payment_{modal_key}")
                notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"notes_{modal_key}")
                
                st.markdown("")
                
                # Action buttons with proper spacing
                col1, col2 = st.columns(2, gap="medium")
                
                with col1:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Add Transaction", type="primary", use_container_width=True):
                        try:
                            transaction = {
                                'date': transaction_date.strftime('%Y-%m-%d'),
                                'amount': float(amount),
                                'type': transaction_type,
                                'description': f"{description}" + (f" - {notes}" if notes else ""),
                                'category': category,
                                'payment_method': payment_method
                            }
                            
                            transaction_id = DatabaseService.add_transaction(transaction)
                            st.success(f"✅ {description} added: ${amount}")
                            
                            # Clear all cached data to force refresh
                            for key in list(st.session_state.keys()):
                                if key.startswith('cached_'):
                                    del st.session_state[key]
                            
                            # Force page refresh
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error adding transaction: {str(e)}")
    
    @staticmethod
    def _show_monthly_summary():
        """Show automated monthly calculations"""
        try:
            from services.financial_data_service import TransactionService
            transactions = TransactionService.load_transactions()
            
            # Get current month transactions
            current_month = datetime.now().strftime('%Y-%m')
            current_transactions = [t for t in transactions if t.get('date', '').startswith(current_month)]
            
            # Calculate totals
            total_income = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Income')
            total_expenses = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Expense')
            total_investments = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Investment')
            total_transfers = sum(float(t.get('amount', 0)) for t in current_transactions if t.get('type') == 'Transfer')
            
            net_cash_flow = total_income - total_expenses - total_investments - total_transfers
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("💰 Income", f"${total_income:,.2f}")
            
            with col2:
                st.metric("💸 Expenses", f"${total_expenses:,.2f}")
            
            with col3:
                st.metric("📈 Investments", f"${total_investments:,.2f}")
            
            with col4:
                st.metric("🔄 Transfers", f"${total_transfers:,.2f}")
            
            with col5:
                st.metric("💰 Net Cash Flow", f"${net_cash_flow:,.2f}", 
                         delta=f"{(net_cash_flow/total_income*100):.1f}%" if total_income > 0 else "0%")
            
            # Show transaction count
            st.info(f"📊 {len(current_transactions)} transactions this month")
            
        except Exception as e:
            st.error(f"Error calculating summary: {str(e)}")
    
    @staticmethod
    def _smart_add(description, default_amount, transaction_type, category, default_payment_method):
        """Smart add with amount input and duplicate detection"""
        modal_key = f"smart_{description.replace(' ', '_')}"
        
        # Show input form
        with st.expander(f"Add {description}", expanded=True):
            with st.form(f"smart_add_{description.replace(' ', '_')}"):
                st.markdown(f"**{description}**")
                st.markdown("---")
                
                amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"amount_{modal_key}")
                transaction_date = st.date_input("Date", value=date.today(), key=f"date_{modal_key}")
                payment_method = st.selectbox("Payment Method", [
                    default_payment_method, "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                ], key=f"payment_{modal_key}")
                notes = st.text_input("Notes (optional)", placeholder="Add details here...", key=f"notes_{modal_key}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Add Transaction", type="primary", use_container_width=True):
                        # Add transaction directly
                        transaction = {
                            'date': transaction_date.strftime('%Y-%m-%d'),
                            'amount': float(amount),
                            'type': transaction_type,
                            'description': f"{description}" + (f" - {notes}" if notes else ""),
                            'category': category,
                            'payment_method': payment_method
                        }
                        
                        try:
                            transaction_id = DatabaseService.add_transaction(transaction)
                            st.success(f"✅ {description} added: ${amount:.2f} (ID: {transaction_id})")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding transaction: {str(e)}")
    
    # Removed - now handled by modular components
    
    @staticmethod
    def _apply_custom_css():
        """Apply custom CSS for professional Add Transaction page styling"""
        st.markdown("""
        <style>
        /* Transaction page styling */
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .stExpander:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
            transform: translateY(-2px);
        }
        
        .stExpander > div:first-child {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px 12px 0 0;
            padding: 1rem 1.5rem;
            font-weight: 600;
            border-bottom: 1px solid #dee2e6;
        }
        
        /* Simplified form styling */
        .stExpander .stForm {
            padding: 1rem;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            height: 48px;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            background-color: #ffffff;
            color: #374151;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        .stButton > button:hover {
            background-color: #f3f4f6;
            border-color: #9ca3af;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Form styling */
        .stForm {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Input field styling */
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            border-radius: 6px !important;
            border: 1px solid #d1d5db !important;
            font-size: 0.875rem !important;
            transition: all 0.2s ease !important;
        }
        
        /* Number input controls styling */
        .stNumberInput > div > div {
            border-radius: 6px !important;
            overflow: hidden !important;
        }
        
        .stNumberInput button {
            border-left: 1px solid #e5e7eb !important;
            background-color: #f9fafb !important;
            color: #6b7280 !important;
            transition: all 0.2s ease !important;
        }
        
        .stNumberInput button:hover {
            background-color: #f3f4f6 !important;
            color: #374151 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: #059669 !important;
            box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1) !important;
            transform: scale(1.01);
        }
        
        /* Label styling */
        .stSelectbox label,
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label {
            font-weight: 500 !important;
            color: #374151 !important;
            font-size: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Help text styling */
        .stTextInput .help {
            font-size: 0.75rem !important;
            color: #6b7280 !important;
            font-style: italic;
        }
        
        /* Form button styling */
        .stForm button {
            height: 44px !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Primary button styling */
        .stForm button[kind="primary"] {
            background-color: #059669 !important;
            color: white !important;
            border: none !important;
        }
        
        .stForm button[kind="primary"]:hover {
            background-color: #047857 !important;
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 6px 16px rgba(5, 150, 105, 0.3);
        }
        
        .stForm button[kind="primary"]:active {
            transform: translateY(0) scale(0.98);
            transition: all 0.1s ease;
        }
        
        /* Primary button styling */
        .stForm button[kind="primary"] {
            font-weight: 600 !important;
        }
        
        /* Secondary button styling */
        .stForm button:not([kind="primary"]) {
            background-color: #ffffff !important;
            color: #6b7280 !important;
            border: 1px solid #d1d5db !important;
            font-weight: 400 !important;
        }
        
        .stForm button:not([kind="primary"]):hover {
            background-color: #f9fafb !important;
            color: #374151 !important;
            border-color: #9ca3af !important;
            transform: translateY(-1px);
        }
        
        .stForm button:not([kind="primary"]):active {
            transform: translateY(0);
            transition: all 0.1s ease;
        }
        
        /* Column spacing */
        .row-widget.stHorizontal {
            gap: 1.5rem;
        }
        
        /* Form spacing */
        .stForm > div {
            margin-bottom: 1rem;
        }
        
        /* Metrics styling */
        .metric-container {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Section headers */
        .stSubheader {
            color: #1f2937;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .stButton > button {
                font-size: 0.8rem;
                padding: 0.5rem;
                height: 44px;
            }
            
            .stForm {
                padding: 1rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)