"""
Transaction button components for quick add functionality
"""
import streamlit as st
from datetime import date
from components.transaction_forms import TransactionFormHandler, UtilitiesFormHandler

class TransactionButtons:
    """Handles all transaction button rendering and form management"""
    
    @staticmethod
    def render_income_section():
        """Render income transaction buttons"""
        with st.expander("💰 Income", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("💰 Monthly Salary", "salary", 
                    "Monthly Salary", 5000.0, "Income", "Salary", "Direct Deposit")
                TransactionButtons._render_button_with_form("🏦 Interest Income", "interest", 
                    "Interest Income", 50.0, "Income", "Investment", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("📈 BOX STOCKS ESPP", "espp", 
                    "BOX STOCKS ESPP", 1000.0, "Income", "Investment", "Direct Deposit")
                TransactionButtons._render_button_with_form("💸 Tax Refund", "tax_refund", 
                    "Tax Refund", 800.0, "Income", "Tax", "Direct Deposit")
            
            with col3:
                TransactionButtons._render_button_with_form("📊 BOX RSU", "rsu", 
                    "BOX RSU", 2000.0, "Income", "Investment", "Direct Deposit")
                TransactionButtons._render_button_with_form("💹 BOX ESPP PROFIT", "espp_profit", 
                    "BOX ESPP PROFIT", 500.0, "Income", "Investment", "Direct Deposit")
    
    @staticmethod
    def render_deductions_section():
        """Render deductions transaction buttons"""
        with st.expander("🏛️ Deductions"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("🏛️ TAXES PAID", "taxes_paid", 
                    "TAXES PAID", 1200.0, "Expense", "Tax", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("🏦 401K Pretax", "401k_pretax", 
                    "401K Pretax", 800.0, "Transfer", "401k", "Direct Deposit")
            
            with col3:
                TransactionButtons._render_button_with_form("🏥 HSA", "hsa", 
                    "HSA", 300.0, "Transfer", "PreTax", "Direct Deposit")
    
    @staticmethod
    def render_housing_section():
        """Render housing transaction buttons"""
        with st.expander("🏠 Housing"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("🏠 Mortgage", "mortgage", 
                    "Mortgage Payment", 2500.0, "Expense", "Housing", "Bank Transfer")
                TransactionButtons._render_button_with_form("🏢 HOA", "hoa", 
                    "HOA Fee", 100.0, "Expense", "Housing", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("🏘️ PROPERTY TAX", "property_tax", 
                    "Property Tax", 400.0, "Expense", "Housing", "Bank Transfer")
                TransactionButtons._render_button_with_form("🛋️ Furniture", "furniture", 
                    "Furniture Purchase", 800.0, "Expense", "Shopping", "Credit Card")
            
            with col3:
                # Special utilities button with smart form
                if st.button("⚡ Utilities", use_container_width=True, key="utilities_btn"):
                    st.session_state.show_utilities_form = True
                
                if st.session_state.get('show_utilities_form', False):
                    UtilitiesFormHandler.render_utilities_form("utilities")
                
                TransactionButtons._render_button_with_form("💎 Jewelry", "jewelry", 
                    "Jewelry Purchase", 500.0, "Expense", "Shopping", "Credit Card")
    
    @staticmethod
    def render_transportation_section():
        """Render transportation transaction buttons"""
        with st.expander("🚗 Transportation"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("🚗 Car Loan", "car_loan", 
                    "Car Loan Payment", 450.0, "Expense", "Transportation", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("🚙 Car Insurance", "car_insurance", 
                    "Car Insurance", 150.0, "Expense", "Transportation", "Bank Transfer")
            
            with col3:
                TransactionButtons._render_button_with_form("⛽ Gas", "gas", 
                    "Gas Fill-up", 60.0, "Expense", "Transportation", "Credit Card")
    
    @staticmethod
    def render_credit_debt_section():
        """Render credit & debt transaction buttons"""
        with st.expander("💳 Credit & Debt"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("💳 Credit Card", "credit_card_payment", 
                    "Credit Card Payment", 200.0, "Expense", "Credit Card", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("🏠 Extra Principal", "extra_principal", 
                    "Extra Principal Payment", 300.0, "Expense", "Housing", "Bank Transfer")
            
            with col3:
                pass
    
    @staticmethod
    def render_investments_transfers_section():
        """Render investments & transfers transaction buttons"""
        with st.expander("📈 Investments & Transfers"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                TransactionButtons._render_button_with_form("💰 Savings Transfer", "savings_transfer", 
                    "Savings Bank Transfer", 1000.0, "Transfer", "Savings", "Bank Transfer")
                TransactionButtons._render_button_with_form("📈 ROBINHOOD", "robinhood", 
                    "Robinhood Investment", 500.0, "Investment", "Investment", "Bank Transfer")
            
            with col2:
                TransactionButtons._render_button_with_form("💸 Savings Withdraw", "savings_withdraw", 
                    "Savings Bank Withdraw", 500.0, "Transfer", "Savings", "Bank Transfer")
                TransactionButtons._render_button_with_form("🥇 GOLD Investment", "gold_investment", 
                    "Gold Investment", 200.0, "Investment", "Investment", "Bank Transfer")
            
            with col3:
                TransactionButtons._render_button_with_form("🌏 Money to India", "money_india", 
                    "Money Sent India", 1000.0, "Transfer", "Transfer", "Bank Transfer")
                TransactionButtons._render_button_with_form("🏦 401k Roth", "401k_roth", 
                    "401k Roth Contribution", 500.0, "Transfer", "Roth", "Direct Deposit")
    
    @staticmethod
    def _render_button_with_form(button_text, form_key, description, default_amount, 
                                transaction_type, category, default_payment_method):
        """Render button with associated inline form"""
        if st.button(button_text, use_container_width=True, key=f"{form_key}_btn"):
            st.session_state[f"show_{form_key}_form"] = True
        
        if st.session_state.get(f'show_{form_key}_form', False):
            TransactionFormHandler.render_inline_form(
                description, default_amount, transaction_type, 
                category, default_payment_method, form_key
            )