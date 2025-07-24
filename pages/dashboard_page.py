import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import random
from services.financial_data_service import TransactionService

class DashboardPage:
    """Dashboard page for the finance tracker application"""
    
    @classmethod
    def show(cls):
        """Display the dashboard page"""
        # Apply custom CSS
        cls._apply_custom_css()
        
        # Page header
        st.markdown("<h1 class='page-title'>Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p class='page-subtitle'>Your financial overview</p>", unsafe_allow_html=True)
        
        # Get current month and year
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        month_name = calendar.month_name[current_month]
        
        # Date filter
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_period = st.selectbox(
                "Period",
                [f"{month_name} {current_year}", "Last 3 Months", "Last 6 Months", "Year to Date", "Last 12 Months", "Custom"],
                index=0
            )
        
        with col2:
            if selected_period == "Custom":
                # Calculate first day of current month and today's date for default range
                first_day = date(current_year, current_month, 1)
                today = date.today()
                
                # Date range input
                date_range = st.date_input(
                    "Select date range",
                    value=(first_day, today),
                    min_value=date(2015, 1, 1),
                    max_value=today
                )
                
                # Apply button
                apply_filter = st.button("Apply Filter", type="primary", use_container_width=True)
            else:
                apply_filter = True  # Auto-apply for non-custom periods
        
        # Determine date range based on selection and apply button
        date_filter = None
        if selected_period == "Custom" and 'date_range' in locals() and len(date_range) == 2 and apply_filter:
            start_date, end_date = date_range
            date_filter = (start_date, end_date)
            st.success(f"📅 Showing data from {start_date} to {end_date}")
        elif selected_period != "Custom":
            # Handle other period selections
            if selected_period == "Last 3 Months":
                end_date = date.today()
                start_date = end_date - timedelta(days=90)
                date_filter = (start_date, end_date)
            elif selected_period == "Last 6 Months":
                end_date = date.today()
                start_date = end_date - timedelta(days=180)
                date_filter = (start_date, end_date)
            # Add more period options as needed
        
        # Get transactions data (force refresh)
        transactions = cls._get_transactions_data()
        
        # Summary cards
        st.markdown("<div class='summary-cards'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        # Only load data if filter is applied or it's not custom period
        if (selected_period == "Custom" and apply_filter) or selected_period != "Custom":
            # Get real financial data with date filter
            current_month_data = cls._get_current_month_data(date_filter)
        else:
            # Show placeholder when custom period is selected but not applied
            current_month_data = {'income': 0, 'expenses': 0}
            if selected_period == "Custom":
                st.info("👆 Select your date range and click 'Apply Filter' to view data")
        
        with col1:
            cls._summary_card("Income", f"${current_month_data['income']:,.2f}", "+12% vs last month", "positive")
        
        with col2:
            cls._summary_card("Expenses", f"${current_month_data['expenses']:,.2f}", "-5% vs last month", "negative")
        
        with col3:
            net_income = current_month_data['income'] - current_month_data['expenses']
            cls._summary_card("Net Income", f"${net_income:,.2f}", "+8% vs last month", "positive" if net_income >= 0 else "negative")
        
        with col4:
            savings_rate = (net_income / current_month_data['income'] * 100) if current_month_data['income'] > 0 else 0
            cls._summary_card("Savings Rate", f"{savings_rate:.1f}%", "+2.1% vs last month", "positive")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Cash flow chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Cash Flow</h2>", unsafe_allow_html=True)
        
        # Get real cash flow data
        cash_flow_data = cls._get_real_cash_flow_data()
        
        # Create cash flow chart
        fig = cls._create_cash_flow_chart(cash_flow_data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottom section with two columns
        col1, col2 = st.columns(2)
        
        # Spending by category
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h2>Spending by Category</h2>", unsafe_allow_html=True)
            
            # Get real spending by category data
            category_data = cls._get_real_category_data()
            
            # Create spending by category chart
            fig = cls._create_category_chart(category_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Budget progress
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h2>Budget Progress</h2>", unsafe_allow_html=True)
            
            # Get real budget progress data
            budget_data = cls._get_real_budget_data()
            
            # Create budget progress chart
            fig = cls._create_budget_chart(budget_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Recent transactions
        st.markdown("<div class='transactions-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Recent Transactions</h2>", unsafe_allow_html=True)
        
        # Get real recent transactions data
        transactions_data = cls._get_real_recent_transactions()
        
        # Display transactions table
        cls._display_transactions_table(transactions_data)
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def _summary_card(title, value, change, change_type):
        """Display a summary card with title, value, and change"""
        change_color = "var(--positive-color)" if change_type == "positive" else "var(--negative-color)"
        change_icon = "↑" if change_type == "positive" else "↓"
        
        st.markdown(f"""
        <div class="summary-card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="card-change" style="color: {change_color};">
                {change_icon} {change}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _get_transactions_data():
        """Get transactions data from the database"""
        try:
            # Force fresh data load
            transactions = TransactionService.load_transactions()
            print(f"Dashboard loaded {len(transactions)} transactions")
            return transactions
        except Exception as e:
            st.error(f"Error loading transactions: {str(e)}")
            return []
    
    @staticmethod
    def _get_current_month_data(date_filter=None):
        """Get financial data for specified date range or current month"""
        try:
            transactions = TransactionService.load_transactions()
            
            if date_filter:
                start_date, end_date = date_filter
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
            else:
                current_month = datetime.now().strftime('%Y-%m')
            
            income = 0
            expenses = 0
            
            for transaction in transactions:
                transaction_date = transaction.get('date', '')
                
                # Filter by date range
                if date_filter:
                    if not (start_str <= transaction_date <= end_str):
                        continue
                else:
                    if not transaction_date.startswith(current_month):
                        continue
                
                amount = float(transaction.get('amount', 0))
                transaction_type = transaction.get('type', '').lower().strip()
                
                if transaction_type in ['income']:
                    income += abs(amount)
                elif transaction_type in ['expense']:
                    expenses += abs(amount)
            
            return {'income': income, 'expenses': expenses}
        except Exception as e:
            print(f"Error getting current month data: {e}")
            return {'income': 0, 'expenses': 0}
    
    @staticmethod
    def _get_real_cash_flow_data():
        """Get real cash flow data from transactions"""
        try:
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                return pd.DataFrame({
                    'Month': [],
                    'Income': [],
                    'Expenses': [],
                    'Net': []
                })
            
            # Get last 6 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # Initialize monthly data
            monthly_data = {}
            current_date = start_date
            while current_date <= end_date:
                month_key = current_date.strftime('%Y-%m')
                month_name = current_date.strftime('%b %Y')
                monthly_data[month_key] = {
                    'month_name': month_name,
                    'income': 0,
                    'expenses': 0
                }
                current_date = current_date.replace(day=28) + timedelta(days=4)
                current_date = current_date.replace(day=1)
            
            # Process transactions
            for transaction in transactions:
                try:
                    transaction_date = datetime.strptime(transaction.get('date', ''), '%Y-%m-%d')
                    month_key = transaction_date.strftime('%Y-%m')
                    
                    if month_key in monthly_data:
                        amount = float(transaction.get('amount', 0))
                        transaction_type = transaction.get('type', '').lower().strip()
                        
                        if transaction_type in ['income']:
                            monthly_data[month_key]['income'] += abs(amount)
                        elif transaction_type in ['expense']:
                            monthly_data[month_key]['expenses'] += abs(amount)
                except (ValueError, TypeError):
                    continue
            
            # Create DataFrame
            months = []
            income = []
            expenses = []
            
            for month_key in sorted(monthly_data.keys()):
                data = monthly_data[month_key]
                months.append(data['month_name'])
                income.append(data['income'])
                expenses.append(data['expenses'])
            
            df = pd.DataFrame({
                'Month': months,
                'Income': income,
                'Expenses': expenses,
                'Net': [i - e for i, e in zip(income, expenses)]
            })
            
            return df
            
        except Exception:
            return pd.DataFrame({
                'Month': [],
                'Income': [],
                'Expenses': [],
                'Net': []
            })
    
    @staticmethod
    def _create_cash_flow_chart(data):
        """Create a cash flow chart using Plotly"""
        fig = go.Figure()
        
        # Add income bars
        fig.add_trace(go.Bar(
            x=data['Month'],
            y=data['Income'],
            name='Income',
            marker_color='#4CAF50'
        ))
        
        # Add expenses bars
        fig.add_trace(go.Bar(
            x=data['Month'],
            y=data['Expenses'],
            name='Expenses',
            marker_color='#FF5252'
        ))
        
        # Add net line
        fig.add_trace(go.Scatter(
            x=data['Month'],
            y=data['Net'],
            name='Net',
            mode='lines+markers',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ))
        
        # Update layout
        fig.update_layout(
            barmode='group',
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color="#333333"
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#E0E0E0',
                zeroline=False,
                tickprefix='$'
            )
        )
        
        return fig
    
    @staticmethod
    def _get_real_category_data():
        """Get real spending by category data"""
        try:
            transactions = TransactionService.load_transactions()
            current_month = datetime.now().strftime('%Y-%m')
            
            category_spending = {}
            for transaction in transactions:
                if (transaction.get('date', '').startswith(current_month) and 
                    transaction.get('type', '').lower() in ['expense']):
                    category = transaction.get('category', 'Other')
                    amount = float(transaction.get('amount', 0))
                    category_spending[category] = category_spending.get(category, 0) + abs(amount)
            
            if not category_spending:
                return pd.DataFrame({'Category': [], 'Amount': []})
            
            df = pd.DataFrame({
                'Category': list(category_spending.keys()),
                'Amount': list(category_spending.values())
            })
            
            return df
            
        except Exception:
            return pd.DataFrame({'Category': [], 'Amount': []})
    
    @staticmethod
    def _create_category_chart(data):
        """Create a spending by category chart using Plotly"""
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#3F51B5', '#009688']
        
        fig = go.Figure(data=[go.Pie(
            labels=data['Category'],
            values=data['Amount'],
            hole=.4,
            marker_colors=colors
        )])
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color="#333333"
            )
        )
        
        return fig
    
    @staticmethod
    def _get_real_budget_data():
        """Get real budget progress data"""
        try:
            from services.financial_data_service import BudgetService
            
            budget_data = BudgetService.load_budget()
            if not budget_data:
                return pd.DataFrame({'Category': [], 'Spent': [], 'Budget': [], 'Percentage': []})
            
            transactions = TransactionService.load_transactions()
            current_month = datetime.now().strftime('%Y-%m')
            
            # Calculate spending by category
            spending_by_category = {}
            for transaction in transactions:
                if (transaction.get('date', '').startswith(current_month) and 
                    transaction.get('type', '').lower() in ['expense']):
                    category = transaction.get('category', 'Other')
                    amount = float(transaction.get('amount', 0))
                    spending_by_category[category] = spending_by_category.get(category, 0) + abs(amount)
            
            # Create budget progress data
            categories = []
            spent = []
            budget = []
            percentages = []
            
            for category, budget_amount in budget_data.items():
                spent_amount = spending_by_category.get(category, 0)
                percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                
                categories.append(category)
                spent.append(spent_amount)
                budget.append(budget_amount)
                percentages.append(percentage)
            
            df = pd.DataFrame({
                'Category': categories,
                'Spent': spent,
                'Budget': budget,
                'Percentage': percentages
            })
            
            return df
            
        except Exception:
            return pd.DataFrame({'Category': [], 'Spent': [], 'Budget': [], 'Percentage': []})
    
    @staticmethod
    def _create_budget_chart(data):
        """Create a budget progress chart using Plotly"""
        fig = go.Figure()
        
        for i, row in data.iterrows():
            color = '#4CAF50' if row['Percentage'] <= 100 else '#F44336'
            
            fig.add_trace(go.Bar(
                x=[row['Percentage']],
                y=[row['Category']],
                orientation='h',
                name=row['Category'],
                showlegend=False,
                marker_color=color,
                text=f"${row['Spent']} of ${row['Budget']} ({row['Percentage']:.1f}%)",
                textposition='auto'
            ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color="#333333"
            ),
            xaxis=dict(
                range=[0, 120],
                showgrid=True,
                gridcolor='#E0E0E0',
                zeroline=False,
                ticksuffix='%'
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False
            ),
            height=350
        )
        
        return fig
    
    @staticmethod
    def _get_real_recent_transactions():
        """Get real recent transactions data"""
        try:
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                return []
            
            # Format and sort transactions (newest first)
            formatted_transactions = []
            for transaction in transactions:
                amount = float(transaction.get('amount', 0))
                transaction_type = transaction.get('type', '').lower()
                
                formatted_transactions.append({
                    'date': transaction.get('date', ''),
                    'category': transaction.get('category', 'Other'),
                    'merchant': transaction.get('description', 'Unknown'),
                    'amount': abs(amount),
                    'type': transaction.get('type', 'Expense')
                })
            
            # Sort by date (newest first) and limit to 10 most recent
            formatted_transactions.sort(key=lambda x: x['date'], reverse=True)
            return formatted_transactions[:10]
            
        except Exception:
            return []
    
    @staticmethod
    def _display_transactions_table(transactions):
        """Display transactions in a table"""
        if not transactions:
            st.info("No recent transactions found.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Display as table
        st.dataframe(
            df,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "category": st.column_config.TextColumn("Category"),
                "merchant": st.column_config.TextColumn("Merchant"),
                "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "type": st.column_config.TextColumn("Type")
            },
            hide_index=True,
            use_container_width=True
        )
    
    @staticmethod
    def _apply_custom_css():
        """Apply custom CSS for styling"""
        st.markdown("""
        <style>
        :root {
            --primary-color: #6200EA;
            --secondary-color: #03DAC6;
            --background-color: #F5F7FA;
            --card-background: #FFFFFF;
            --text-color: #333333;
            --light-text-color: #666666;
            --border-color: #E0E0E0;
            --positive-color: #4CAF50;
            --negative-color: #F44336;
        }
        
        /* Page title styling */
        .page-title {
            font-size: 2rem;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 0;
        }
        
        .page-subtitle {
            color: var(--light-text-color);
            margin-bottom: 2rem;
        }
        
        /* Summary cards styling */
        .summary-cards {
            display: flex;
            gap: 20px;
            margin-bottom: 2rem;
        }
        
        .summary-card {
            background-color: var(--card-background);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
        }
        
        .card-title {
            color: var(--light-text-color);
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .card-value {
            color: var(--text-color);
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .card-change {
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* Chart container styling */
        .chart-container {
            background-color: var(--card-background);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        
        .chart-container h2 {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 1rem;
        }
        
        /* Transactions container styling */
        .transactions-container {
            background-color: var(--card-background);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .transactions-container h2 {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 1rem;
        }
        
        /* Streamlit component styling */
        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
        
        div[data-testid="stSelectbox"] label {
            font-weight: 500;
        }
        
        div[data-testid="stDateInput"] label {
            font-weight: 500;
        }
        
        /* Dataframe styling */
        div[data-testid="stDataFrame"] {
            border: none !important;
        }
        
        div[data-testid="stDataFrame"] > div {
            border: none !important;
        }
        </style>
        """, unsafe_allow_html=True)