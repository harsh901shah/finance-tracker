import streamlit as st
from datetime import datetime, date
from services.database_service import DatabaseService

class AddTransactionPage:
    @staticmethod
    def show():
        st.header("💰 Add Transaction")
        
        # Quick add buttons for your specific categories
        st.subheader("Quick Add")
        
        # Income section
        with st.expander("💰 Income", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💰 Monthly Salary", use_container_width=True):
                    AddTransactionPage._quick_add("Monthly Salary", 5000.0, "Income", "Salary")
                if st.button("🏦 Interest Income", use_container_width=True):
                    AddTransactionPage._quick_add("Interest Income", 50.0, "Income", "Investment")
            
            with col2:
                if st.button("📈 BOX STOCKS ESPP", use_container_width=True):
                    AddTransactionPage._quick_add("BOX STOCKS ESPP", 1000.0, "Income", "Investment")
                if st.button("💸 Tax Refund", use_container_width=True):
                    AddTransactionPage._quick_add("Tax Refund", 800.0, "Income", "Tax")
            
            with col3:
                if st.button("📊 BOX RSU", use_container_width=True):
                    AddTransactionPage._quick_add("BOX RSU", 2000.0, "Income", "Investment")
                if st.button("💹 BOX ESPP PROFIT", use_container_width=True):
                    AddTransactionPage._quick_add("BOX ESPP PROFIT", 500.0, "Income", "Investment")
        
        # Deductions section
        with st.expander("🏛️ Deductions"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏛️ TAXES PAID", use_container_width=True):
                    AddTransactionPage._quick_add("TAXES PAID", 1200.0, "Expense", "Tax")
            
            with col2:
                if st.button("🏦 401K Pretax", use_container_width=True):
                    AddTransactionPage._quick_add("401K Pretax", 800.0, "Expense", "Retirement")
            
            with col3:
                if st.button("🏥 HSA", use_container_width=True):
                    AddTransactionPage._quick_add("HSA", 300.0, "Expense", "Healthcare")
        
        # Housing expenses
        with st.expander("🏠 Housing"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🏠 Mortgage", use_container_width=True):
                    AddTransactionPage._quick_add("Mortgage Payment", 2500.0, "Expense", "Housing")
                if st.button("🏢 HOA", use_container_width=True):
                    AddTransactionPage._quick_add("HOA Fee", 100.0, "Expense", "Housing")
            
            with col2:
                if st.button("🏘️ PROPERTY TAX", use_container_width=True):
                    AddTransactionPage._quick_add("Property Tax", 400.0, "Expense", "Housing")
                if st.button("🛋️ Furniture", use_container_width=True):
                    AddTransactionPage._quick_add("Furniture Purchase", 800.0, "Expense", "Shopping")
            
            with col3:
                if st.button("⚡ Utilities", use_container_width=True):
                    AddTransactionPage._quick_add("Electric + Phone + Wifi", 200.0, "Expense", "Utilities")
                if st.button("💎 Jewelry", use_container_width=True):
                    AddTransactionPage._quick_add("Jewelry Purchase", 500.0, "Expense", "Shopping")
        
        # Transportation expenses
        with st.expander("🚗 Transportation"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🚗 Car Loan", use_container_width=True):
                    AddTransactionPage._quick_add("Car Loan Payment", 450.0, "Expense", "Transportation")
            
            with col2:
                if st.button("🚙 Car Insurance", use_container_width=True):
                    AddTransactionPage._quick_add("Car Insurance", 150.0, "Expense", "Transportation")
            
            with col3:
                if st.button("⛽ Gas", use_container_width=True):
                    AddTransactionPage._quick_add("Gas Fill-up", 60.0, "Expense", "Transportation")
        
        # Credit & Debt
        with st.expander("💳 Credit & Debt"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💳 DISCOVER DEBT", use_container_width=True):
                    AddTransactionPage._quick_add("Discover Credit Card Payment", 300.0, "Expense", "Credit Card")
            
            with col2:
                if st.button("💳 Credit Card Payment", use_container_width=True):
                    AddTransactionPage._quick_add("Credit Card Payment", 200.0, "Expense", "Credit Card")
            
            with col3:
                if st.button("🏠 Extra Principal", use_container_width=True):
                    AddTransactionPage._quick_add("Extra Principal Payment", 300.0, "Expense", "Housing")
        
        # Investments & Transfers
        with st.expander("📈 Investments & Transfers"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💰 Savings Transfer", use_container_width=True):
                    AddTransactionPage._quick_add("Savings Bank Transfer", 1000.0, "Transfer", "Savings")
                if st.button("📈 ROBINHOOD", use_container_width=True):
                    AddTransactionPage._quick_add("Robinhood Investment", 500.0, "Investment", "Investment")
            
            with col2:
                if st.button("💸 Savings Withdraw", use_container_width=True):
                    AddTransactionPage._quick_add("Savings Bank Withdraw", 500.0, "Transfer", "Savings")
                if st.button("🥇 GOLD Investment", use_container_width=True):
                    AddTransactionPage._quick_add("Gold Investment", 200.0, "Investment", "Investment")
            
            with col3:
                if st.button("🌏 Money to India", use_container_width=True):
                    AddTransactionPage._quick_add("Money Sent India", 1000.0, "Transfer", "Transfer")
                if st.button("🏦 401k Roth", use_container_width=True):
                    AddTransactionPage._quick_add("401k Roth Contribution", 500.0, "Investment", "Retirement")
        
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
                category = st.selectbox("Category", [
                    "Salary", "Investment", "Tax", "Retirement", "Healthcare",
                    "Housing", "Transportation", "Utilities", "Shopping", 
                    "Credit Card", "Savings", "Transfer", "Food", "Entertainment", "Other"
                ])
                payment_method = st.selectbox("Payment Method", [
                    "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit", "Other"
                ])
            
            submitted = st.form_submit_button("Add Transaction", type="primary", use_container_width=True)
            
            if submitted:
                try:
                    transaction = {
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'amount': float(amount),
                        'type': transaction_type,
                        'description': description,
                        'category': category,
                        'payment_method': payment_method
                    }
                    
                    transaction_id = DatabaseService.add_transaction(transaction)
                    st.success(f"✅ Transaction added successfully! (ID: {transaction_id})")
                    
                    # Clear cache
                    if 'cached_transactions' in st.session_state:
                        del st.session_state['cached_transactions']
                    
                except Exception as e:
                    st.error(f"Error adding transaction: {str(e)}")
        
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
        
        # Show form in expander
        with st.expander(f"Add {description}", expanded=True):
            with st.form(f"quick_add_{description.replace(' ', '_')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    amount = st.number_input("Amount ($)", value=default_amount, step=0.01, key=f"amount_{modal_key}")
                    transaction_date = st.date_input("Date", value=date.today(), key=f"date_{modal_key}")
                
                with col2:
                    notes = st.text_input("Notes (optional)", placeholder="Additional details...", key=f"notes_{modal_key}")
                    payment_method = st.selectbox("Payment Method", [
                        "Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit"
                    ], key=f"payment_{modal_key}")
                
                col1, col2 = st.columns(2)
                with col1:
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
                            
                            # Clear cache
                            if 'cached_transactions' in st.session_state:
                                del st.session_state['cached_transactions']
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error adding transaction: {str(e)}")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.rerun()
    
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