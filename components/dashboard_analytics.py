"""
Dashboard analytics and filtering components
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from services.financial_data_service import TransactionService
from utils.logger import AppLogger
from utils.transaction_filter import TransactionFilter

class DashboardAnalytics:
    """Handles dashboard analytics and data processing"""
    
    @staticmethod
    def get_filtered_data(date_filter=None, filters=None):
        """Get financial data with advanced filtering"""
        try:
            filtered_transactions = TransactionFilter.get_filtered_transactions(date_filter, filters)
            return TransactionFilter.calculate_financial_summary(filtered_transactions)
        except Exception as e:
            AppLogger.log_error("Error getting filtered financial data", e, show_user=False)
            return {'income': 0, 'expenses': 0}
    
    @staticmethod
    def get_additional_analytics(date_filter=None, filters=None):
        """Get additional analytics for enhanced summary cards"""
        try:
            filtered_transactions = TransactionFilter.get_filtered_transactions(date_filter, filters)
            return TransactionFilter.calculate_analytics(filtered_transactions)
        except Exception as e:
            AppLogger.log_error("Error getting additional analytics", e, show_user=False)
            return {}
    
    @staticmethod
    def calculate_trends(date_filter=None, filters=None):
        """Calculate trends by comparing current period with previous period"""
        try:
            if not date_filter:
                # Use current month as default when no date_filter provided
                today = date.today()
                start_date = date(today.year, today.month, 1)
                end_date = today
                date_filter = (start_date, end_date)

            
            start_date, end_date = date_filter
            period_days = (end_date - start_date).days
            
            # Calculate previous period (same duration)
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=period_days)
            
            # Get current period data
            current_data = DashboardAnalytics.get_filtered_data(date_filter, filters)
            
            # Get previous period data
            prev_filter = (prev_start_date, prev_end_date)
            prev_data = DashboardAnalytics.get_filtered_data(prev_filter, filters)
            
            # Calculate percentage changes
            def calc_change(current, previous):
                if previous == 0:
                    return 0 if current == 0 else 100
                return ((current - previous) / previous) * 100
            
            current_income = current_data['income']
            current_expenses = current_data['expenses']
            current_net = current_income - current_expenses
            current_savings_rate = (current_net / current_income * 100) if current_income > 0 else 0
            
            prev_income = prev_data['income']
            prev_expenses = prev_data['expenses']
            prev_net = prev_income - prev_expenses
            prev_savings_rate = (prev_net / prev_income * 100) if prev_income > 0 else 0
            
            # Check if there's meaningful previous data
            has_previous_data = prev_income > 0 or prev_expenses > 0
            

            
            return {
                'income_trend': calc_change(current_income, prev_income),
                'expense_trend': calc_change(current_expenses, prev_expenses),
                'net_trend': calc_change(current_net, prev_net),
                'savings_trend': calc_change(current_savings_rate, prev_savings_rate),
                'has_previous_data': has_previous_data
            }
        except Exception as e:
            AppLogger.log_error("Error calculating trends", e, show_user=False)
            return {}

class DashboardFilters:
    """Handles dashboard filtering UI and logic"""
    
    @staticmethod
    def render_filter_controls():
        """Render all filter controls and return filter configuration"""
        # Get current date info
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        month_name = current_date.strftime('%B')
        
        # Advanced filters
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_period = st.selectbox(
                "Period",
                [f"{month_name} {current_year}", "This Week", "Last Week", "Last 3 Months", 
                 "Last 6 Months", "Year to Date", "Last 12 Months", "This Year", "Custom"],
                index=0
            )
        
        with col2:
            transaction_types = st.multiselect(
                "Transaction Type",
                ["Income", "Expense", "Investment", "Transfer"],
                default=["Income", "Expense"]
            )
        
        with col3:
            all_categories = ["All Categories", "Salary", "Investment", "Tax", "Retirement", "Healthcare", 
                            "Housing", "Transportation", "Utilities", "Shopping", "Credit Card", 
                            "Savings", "Transfer", "Food", "Entertainment", "Other"]
            selected_categories = st.selectbox("Category", all_categories, index=0)
        
        # Additional filters row
        col1, col2, col3 = st.columns(3)
        with col1:
            date_range = None
            if selected_period == "Custom":
                first_day = date(current_year, current_month, 1)
                today = date.today()
                date_range = st.date_input(
                    "Select date range",
                    value=(first_day, today),
                    min_value=date(2015, 1, 1),
                    max_value=today
                )
        
        with col2:
            payment_methods = st.multiselect(
                "Payment Method",
                ["Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit", "Other"],
                default=[]
            )
        
        with col3:
            apply_filter = st.button("Apply Filters", type="primary", use_container_width=True)
            if selected_period != "Custom":
                apply_filter = True
        
        # Process filters
        date_filter = DashboardFilters._process_date_filter(selected_period, date_range, apply_filter)
        filters = {
            'transaction_types': transaction_types,
            'categories': [selected_categories] if selected_categories != "All Categories" else [],
            'payment_methods': payment_methods
        }
        
        return date_filter, filters, apply_filter
    
    @staticmethod
    def _process_date_filter(selected_period, date_range, apply_filter):
        """Process date filter based on selection"""
        if selected_period == "Custom" and date_range and len(date_range) == 2 and apply_filter:
            start_date, end_date = date_range
            st.success(f"📅 Showing data from {start_date} to {end_date}")
            return (start_date, end_date)
        elif selected_period != "Custom" and apply_filter:
            today = date.today()
            if selected_period == "This Week":
                start_date = today - timedelta(days=today.weekday())
                return (start_date, today)
            elif selected_period == "Last Week":
                start_date = today - timedelta(days=today.weekday() + 7)
                end_date = today - timedelta(days=today.weekday() + 1)
                return (start_date, end_date)
            elif selected_period == "Last 3 Months":
                start_date = today - timedelta(days=90)
                return (start_date, today)
            elif selected_period == "Last 6 Months":
                start_date = today - timedelta(days=180)
                return (start_date, today)
            elif selected_period == "Year to Date":
                start_date = date(today.year, 1, 1)
                return (start_date, today)
            elif selected_period == "Last 12 Months":
                start_date = today - timedelta(days=365)
                return (start_date, today)
            elif selected_period == "This Year":
                start_date = date(today.year, 1, 1)
                end_date = date(today.year, 12, 31)
                return (start_date, min(end_date, today))
        
        return None