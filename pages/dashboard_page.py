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
                
                # Ensure the default date range is within allowed bounds
                date_range = st.date_input(
                    "Select date range",
                    value=(first_day, today),
                    min_value=date(2015, 1, 1),
                    max_value=today
                )
        
        # Get transactions data
        transactions = cls._get_transactions_data()
        
        # Summary cards
        st.markdown("<div class='summary-cards'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cls._summary_card("Income", "$5,240", "+12% vs last month", "positive")
        
        with col2:
            cls._summary_card("Expenses", "$3,890", "-5% vs last month", "negative")
        
        with col3:
            cls._summary_card("Net Income", "$1,350", "+8% vs last month", "positive")
        
        with col4:
            cls._summary_card("Savings Rate", "25.8%", "+2.1% vs last month", "positive")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Cash flow chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Cash Flow</h2>", unsafe_allow_html=True)
        
        # Create cash flow data
        cash_flow_data = cls._generate_cash_flow_data()
        
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
            
            # Create spending by category data
            category_data = cls._generate_category_data()
            
            # Create spending by category chart
            fig = cls._create_category_chart(category_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Budget progress
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h2>Budget Progress</h2>", unsafe_allow_html=True)
            
            # Create budget progress data
            budget_data = cls._generate_budget_data()
            
            # Create budget progress chart
            fig = cls._create_budget_chart(budget_data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Recent transactions
        st.markdown("<div class='transactions-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Recent Transactions</h2>", unsafe_allow_html=True)
        
        # Create recent transactions data
        transactions_data = cls._generate_transactions_data()
        
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
            return TransactionService.load_transactions()
        except Exception as e:
            st.error(f"Error loading transactions: {str(e)}")
            return []
    
    @staticmethod
    def _generate_cash_flow_data():
        """Generate sample cash flow data"""
        # Get the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        # Generate monthly data
        months = []
        income = []
        expenses = []
        
        current_date = start_date
        while current_date <= end_date:
            month_name = current_date.strftime("%b")
            months.append(month_name)
            
            # Generate random income and expenses
            month_income = random.randint(4000, 6000)
            month_expenses = random.randint(3000, 5000)
            
            income.append(month_income)
            expenses.append(month_expenses)
            
            # Move to next month
            current_date = current_date.replace(day=28) + timedelta(days=4)
            current_date = current_date.replace(day=1)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Month': months,
            'Income': income,
            'Expenses': expenses,
            'Net': [i - e for i, e in zip(income, expenses)]
        })
        
        return df
    
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
    def _generate_category_data():
        """Generate sample spending by category data"""
        categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        amounts = [1200, 650, 450, 320, 280, 490, 500]
        
        df = pd.DataFrame({
            'Category': categories,
            'Amount': amounts
        })
        
        return df
    
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
    def _generate_budget_data():
        """Generate sample budget data"""
        categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        spent = [1200, 580, 320, 290, 250, 420, 380]
        budget = [1200, 600, 400, 300, 300, 500, 400]
        
        df = pd.DataFrame({
            'Category': categories,
            'Spent': spent,
            'Budget': budget,
            'Percentage': [s/b*100 for s, b in zip(spent, budget)]
        })
        
        return df
    
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
    def _generate_transactions_data():
        """Generate sample transactions data"""
        categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        merchants = [
            'Apartment Rental', 'Grocery Store', 'Gas Station', 'Movie Theater', 
            'Electric Company', 'Online Store', 'Pharmacy', 'Restaurant', 'Coffee Shop'
        ]
        
        transactions = []
        
        # Generate 10 random transactions
        for i in range(10):
            date = datetime.now() - timedelta(days=random.randint(0, 15))
            category = random.choice(categories)
            merchant = random.choice(merchants)
            amount = round(random.uniform(10, 200), 2)
            
            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'merchant': merchant,
                'amount': amount,
                'type': 'Expense'
            })
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return transactions
    
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