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
        
        # Generate month options for current and future months
        month_options = []
        for year in [current_year, current_year + 1]:
            for month in range(1, 13):
                month_name_opt = datetime(year, month, 1).strftime('%B')
                month_options.append(f"{month_name_opt} {year}")
        
        # Advanced filters
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_period = st.selectbox(
                "Period",
                month_options,
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
            payment_methods = st.multiselect(
                "Payment Method",
                ["Bank Transfer", "Credit Card", "Cash", "Check", "Direct Deposit", "Other"],
                default=[]
            )
        
        with col2:
            apply_filter = st.button("Apply Filters", type="primary", use_container_width=True)
        
        # Auto-apply for month selections
        if not apply_filter:
            apply_filter = True
        
        date_range = None
        
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
        """Process date filter based on monthly selection"""
        if apply_filter:
            # Handle specific month selection (e.g., "August 2025")
            import calendar
            try:
                # Parse month and year from selection
                parts = selected_period.split()
                if len(parts) == 2:
                    month_name, year_str = parts
                    year = int(year_str)
                    month = datetime.strptime(month_name, '%B').month
                    
                    # Get first and last day of the month
                    start_date = date(year, month, 1)
                    last_day = calendar.monthrange(year, month)[1]
                    end_date = date(year, month, last_day)
                    
                    return (start_date, end_date)
            except (ValueError, IndexError):
                pass
        
        return None