"""
Dashboard chart components
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.financial_data_service import TransactionService
from config.app_config import AppConfig

class DashboardCharts:
    """Handles all dashboard chart generation"""
    
    @staticmethod
    def render_cash_flow_chart():
        """Render cash flow chart section"""
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Cash Flow</h2>", unsafe_allow_html=True)
        
        cash_flow_data = DashboardCharts._get_cash_flow_data()
        fig = DashboardCharts._create_cash_flow_chart(cash_flow_data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def render_category_chart():
        """Render spending by category chart section"""
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Spending by Category</h2>", unsafe_allow_html=True)
        
        category_data = DashboardCharts._get_category_data()
        fig = DashboardCharts._create_category_chart(category_data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def render_budget_chart():
        """Render budget progress chart section"""
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Budget Progress</h2>", unsafe_allow_html=True)
        
        budget_data = DashboardCharts._get_budget_data()
        fig = DashboardCharts._create_budget_chart(budget_data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def render_recent_transactions():
        """Render recent transactions table section"""
        st.markdown("<div class='transactions-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Recent Transactions</h2>", unsafe_allow_html=True)
        
        transactions_data = DashboardCharts._get_recent_transactions()
        DashboardCharts._display_transactions_table(transactions_data)
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def _get_cash_flow_data():
        """Get cash flow data from transactions"""
        try:
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                return pd.DataFrame({'Month': [], 'Income': [], 'Expenses': [], 'Net': []})
            
            # Get last 6 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # Initialize monthly data
            monthly_data = {}
            current_date = start_date
            while current_date <= end_date:
                month_key = current_date.strftime('%Y-%m')
                month_name = current_date.strftime('%b %Y')
                monthly_data[month_key] = {'month_name': month_name, 'income': 0, 'expenses': 0}
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
            
            return pd.DataFrame({
                'Month': months,
                'Income': income,
                'Expenses': expenses,
                'Net': [i - e for i, e in zip(income, expenses)]
            })
            
        except Exception:
            return pd.DataFrame({'Month': [], 'Income': [], 'Expenses': [], 'Net': []})
    
    @staticmethod
    def _create_cash_flow_chart(data):
        """Create cash flow chart using Plotly"""
        fig = go.Figure()
        
        # Add income bars
        fig.add_trace(go.Bar(
            x=data['Month'], y=data['Income'], name='Income', marker_color='#4CAF50'
        ))
        
        # Add expenses bars
        fig.add_trace(go.Bar(
            x=data['Month'], y=data['Expenses'], name='Expenses', marker_color='#FF5252'
        ))
        
        # Add net line
        fig.add_trace(go.Scatter(
            x=data['Month'], y=data['Net'], name='Net', mode='lines+markers',
            line=dict(color='#2196F3', width=3), marker=dict(size=8)
        ))
        
        # Update layout
        fig.update_layout(
            barmode='group', margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12, color="#333333"),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='#E0E0E0', zeroline=False, tickprefix='$')
        )
        
        return fig
    
    @staticmethod
    def _get_category_data():
        """Get spending by category data"""
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
                # Return empty DataFrame with info message handled by caller
                return pd.DataFrame({'Category': [], 'Amount': []})
            
            return pd.DataFrame({
                'Category': list(category_spending.keys()),
                'Amount': list(category_spending.values())
            })
            
        except Exception:
            return pd.DataFrame({'Category': [], 'Amount': []})
    
    @staticmethod
    def _create_category_chart(data):
        """Create spending by category chart using Plotly"""
        colors = AppConfig.CHART_COLORS
        
        # Handle empty data gracefully
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No spending data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#666666")
            )
        else:
            fig = go.Figure(data=[go.Pie(
                labels=data['Category'], values=data['Amount'], hole=.4, marker_colors=colors
            )])
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12, color="#333333")
        )
        
        return fig
    
    @staticmethod
    def _get_budget_data():
        """Get budget progress data"""
        try:
            from services.financial_data_service import BudgetService
            
            budget_data = BudgetService.load_budget()
            if not budget_data:
                # Return empty DataFrame with info message handled by caller
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
            categories, spent, budget, percentages = [], [], [], []
            
            for category, budget_amount in budget_data.items():
                spent_amount = spending_by_category.get(category, 0)
                percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                
                categories.append(category)
                spent.append(spent_amount)
                budget.append(budget_amount)
                percentages.append(percentage)
            
            return pd.DataFrame({
                'Category': categories, 'Spent': spent, 
                'Budget': budget, 'Percentage': percentages
            })
            
        except Exception:
            return pd.DataFrame({'Category': [], 'Spent': [], 'Budget': [], 'Percentage': []})
    
    @staticmethod
    def _create_budget_chart(data):
        """Create budget progress chart using Plotly"""
        fig = go.Figure()
        
        # Handle empty data gracefully
        if data.empty:
            fig.add_annotation(
                text="No budget data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#666666")
            )
        else:
            for i, row in data.iterrows():
            color = '#4CAF50' if row['Percentage'] <= 100 else '#F44336'
            
            fig.add_trace(go.Bar(
                x=[row['Percentage']], y=[row['Category']], orientation='h',
                name=row['Category'], showlegend=False, marker_color=color,
                text=f"${row['Spent']} of ${row['Budget']} ({row['Percentage']:.1f}%)",
                textposition='auto'
            ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter, sans-serif", size=12, color="#333333"),
            xaxis=dict(range=[0, 120], showgrid=True, gridcolor='#E0E0E0', zeroline=False, ticksuffix='%'),
            yaxis=dict(showgrid=False, zeroline=False), height=350
        )
        
        return fig
    
    @staticmethod
    def _get_recent_transactions():
        """Get recent transactions data"""
        try:
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                return []
            
            # Format and sort transactions (newest first)
            formatted_transactions = []
            for transaction in transactions:
                amount = float(transaction.get('amount', 0))
                
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
        """Display transactions in a table with graceful empty data handling"""
        if not transactions:
            st.info("📊 No recent transactions found. Add some transactions to see them here!")
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
            hide_index=True, use_container_width=True
        )