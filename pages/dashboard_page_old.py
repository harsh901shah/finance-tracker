import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
from utils.filters import Filters, get_period_range
from utils.data import load_transactions, apply_filters
from utils.kpis import compute_kpis

class DashboardPage:
    """Dashboard page for the finance tracker application"""
    
    @classmethod
    def show(cls):
        """Display the dashboard page"""
        # Apply world-class CSS
        cls._apply_world_class_css()
        
        # Page header
        st.markdown("<h1 class='page-title'>Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p class='page-subtitle'>Your financial overview</p>", unsafe_allow_html=True)
        
        # Compact filter bar
        date_filter, filters, apply_filter = cls._render_compact_filter_bar()
        
        # Get transactions data (force refresh)
        transactions = cls._get_transactions_data()
        
        # Load data by default, with filters if applied
        if apply_filter:
            current_month_data = DashboardAnalytics.get_filtered_data(date_filter, filters)
        else:
            current_month_data = DashboardAnalytics.get_filtered_data()
        
        # Get trend data for comparison
        trends = DashboardAnalytics.calculate_trends(date_filter, filters) if apply_filter else {}
        
        # Get additional analytics
        if apply_filter:
            analytics = DashboardAnalytics.get_additional_analytics(date_filter, filters) if AppConfig.FEATURES.get('advanced_analytics', True) else {}
        else:
            analytics = DashboardAnalytics.get_additional_analytics() if AppConfig.FEATURES.get('advanced_analytics', True) else {}
        
        # World-class KPI grid
        cls._render_kpi_grid(current_month_data, trends, analytics)
        
        # Cash flow chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Cash Flow</h2>", unsafe_allow_html=True)
        
        # Get real cash flow data
        cash_flow_data = cls._get_real_cash_flow_data()
        
        # Create cash flow chart
        fig = cls._create_cash_flow_chart(cash_flow_data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add equal height CSS for cards
        st.markdown("""
        <style>
        .k-equal { display: flex; flex-direction: column; height: 100%; }
        .k-equal .chart-container { flex: 1; display: flex; flex-direction: column; }
        @media (max-width: 900px) {
            div[data-testid="stHorizontalBlock"] > div { margin-bottom: 12px; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Bottom section with two columns
        col1, col2 = st.columns(2)
        
        # Spending by category
        with col1:
            st.markdown('<div class="k-equal">', unsafe_allow_html=True)
            st.markdown("""
            <div class='chart-container'>
                <div style='display: flex; align-items: center; margin-bottom: 12px;'>
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px;'>
                        <span style='font-size: 1.2rem;'>📊</span>
                    </div>
                    <div>
                        <h2 style='margin: 0; font-size: 1.2rem; font-weight: 600; color: #1e293b;'>Spending by Category</h2>
                        <p style='margin: 0; color: #64748b; font-size: 0.8rem;'>Current month breakdown</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Get real spending by category data
            category_data = cls._get_real_category_data(date_filter if apply_filter else None, filters if apply_filter else None)
            
            if not category_data.empty:
                # Create spending by category chart
                fig = cls._create_category_chart(category_data)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #e2e8f0; height: 360px; display: flex; flex-direction: column; justify-content: center;'>
                    <h3 style='color: #64748b; margin-bottom: 1rem;'>📊 No Spending Data</h3>
                    <p style='color: #64748b; margin: 0;'>Add expense transactions to see breakdown</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Budget progress
        with col2:
            st.markdown('<div class="k-equal">', unsafe_allow_html=True)
            if AppConfig.FEATURES.get('budget_tracking', True):
                st.markdown("""
                <div class='chart-container'>
                    <div style='display: flex; align-items: center; margin-bottom: 12px;'>
                        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px;'>
                            <span style='font-size: 1.2rem;'>🎯</span>
                        </div>
                        <div>
                            <h2 style='margin: 0; font-size: 1.2rem; font-weight: 600; color: #1e293b;'>Budget Progress</h2>
                            <p style='margin: 0; color: #64748b; font-size: 0.8rem;'>Monthly budget tracking</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Get real budget progress data
                budget_data = cls._get_real_budget_data(date_filter if apply_filter else None, filters if apply_filter else None)
                
                if not budget_data.empty:
                    # Create budget progress chart
                    fig = cls._create_budget_chart(budget_data)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown("""
                    <div style='text-align: center; padding: 2rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #e2e8f0; height: 360px; display: flex; flex-direction: column; justify-content: center;'>
                        <h3 style='color: #64748b; margin-bottom: 1rem;'>🎯 No Budget Set</h3>
                        <p style='color: #64748b; margin: 0;'>Go to Budget Planning to set limits</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='chart-container'>
                    <div style='height: 360px; display: flex; align-items: center; justify-content: center;'>
                        <div>📊 Budget tracking is currently disabled</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
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
    def _render_compact_filter_bar():
        """Render compact single-row filter bar"""
        # Get filter controls once to avoid duplicate IDs
        date_filter, filters, apply_filter = DashboardFilters.render_filter_controls()
        return date_filter, filters, apply_filter
    
    @classmethod
    def _render_kpi_grid(cls, current_month_data, trends, analytics):
        """Render responsive KPI grid with world-class design"""
        
        # Calculate all KPI values (keeping original logic)
        net_income = current_month_data['income'] - current_month_data['expenses']
        savings_rate = (net_income / current_month_data['income'] * 100) if current_month_data['income'] > 0 else 0
        
        income_trend = trends.get('income_trend', 0)
        expense_trend = trends.get('expense_trend', 0)
        net_trend = trends.get('net_trend', 0)
        savings_trend = trends.get('savings_trend', 0)
        
        has_trend_data = len(trends) > 0
        
        # KPI data array
        kpis = [
            {
                'icon': '💰',
                'title': 'Income',
                'value': f"${current_month_data['income']:,.0f}",
                'delta': income_trend if has_trend_data else None,
                'delta_type': 'positive' if income_trend >= 0 else 'negative' if has_trend_data else 'neutral'
            },
            {
                'icon': '💸',
                'title': 'Expenses', 
                'value': f"${current_month_data['expenses']:,.0f}",
                'delta': expense_trend if has_trend_data else None,
                'delta_type': 'negative' if expense_trend > 0 else 'positive' if has_trend_data else 'neutral'
            },
            {
                'icon': '📈',
                'title': 'Net Income',
                'value': f"${net_income:,.0f}",
                'delta': net_trend if has_trend_data else None,
                'delta_type': 'positive' if net_income >= 0 else 'negative' if has_trend_data else 'neutral'
            },
            {
                'icon': '🎯',
                'title': 'Savings Rate',
                'value': f"{savings_rate:.1f}%",
                'delta': savings_trend if has_trend_data else None,
                'delta_type': 'positive' if savings_trend >= 0 else 'negative' if has_trend_data else 'neutral'
            },
            {
                'icon': '🔄',
                'title': 'Transfers',
                'value': f"${analytics.get('transfers', 0):,.0f}",
                'delta': None,
                'delta_type': 'neutral'
            },
            {
                'icon': '🏆',
                'title': 'Top Category',
                'value': analytics.get('top_category', 'N/A'),
                'delta': None,
                'delta_type': 'neutral'
            },
            {
                'icon': '📊',
                'title': 'Avg Transaction',
                'value': f"${analytics.get('avg_transaction', 0):,.0f}",
                'delta': None,
                'delta_type': 'neutral'
            },
            {
                'icon': '💳',
                'title': 'Payment Method',
                'value': analytics.get('top_payment_method', 'N/A'),
                'delta': None,
                'delta_type': 'neutral'
            }
        ]
        
        # Render KPI cards in responsive grid
        for i in range(0, len(kpis), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(kpis):
                    with col:
                        cls._render_kpi_card(kpis[i + j])
    
    @staticmethod
    def _render_kpi_card(kpi):
        """Render individual KPI card with world-class design"""
        delta_html = ""
        if kpi['delta'] is not None:
            delta_color = {
                'positive': '#00D924',
                'negative': '#FF3B30', 
                'neutral': '#8E8E93'
            }[kpi['delta_type']]
            
            delta_icon = '↗' if kpi['delta_type'] == 'positive' else '↘' if kpi['delta_type'] == 'negative' else '→'
            delta_html = f'<div class="kpi-delta" style="background-color: {delta_color}15; color: {delta_color};">{delta_icon} {abs(kpi["delta"]):.1f}%</div>'
        
        caption_text = "vs last period" if kpi['delta'] is not None else ""
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <div class="kpi-icon">{kpi['icon']}</div>
                <div class="kpi-title">{kpi['title']}</div>
            </div>
            <div class="kpi-value">{kpi['value']}</div>
            {delta_html}
            <div class="kpi-caption">{caption_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _get_transactions_data():
        """Get transactions data from the database"""
        try:
            # Force fresh data load with proper user isolation
            transactions = TransactionService.load_transactions()
            return transactions
        except Exception as e:
            st.error(f"Error loading transactions: {str(e)}")
            return []
    

    

    
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
                        
                        # Include pre-tax and Roth contributions as income since they represent earned money
                        if transaction_type in ['income'] or (transaction_type == 'transfer' and transaction.get('category', '').lower() in ['retirement', '401k', 'roth', 'pretax']):
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
    def _get_real_category_data(date_filter=None, filters=None):
        """Get real spending by category data with proper filtering"""
        try:
            from utils.transaction_filter import TransactionFilter
            
            # Get filtered transactions
            filtered_transactions = TransactionFilter.get_filtered_transactions(date_filter, filters)
            
            category_spending = {}
            for transaction in filtered_transactions:
                if transaction.get('type', '').lower() == 'expense':
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
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
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
    def _get_real_budget_data(date_filter=None, filters=None):
        """Get real budget progress data with proper filtering"""
        try:
            from services.financial_data_service import BudgetService
            from utils.transaction_filter import TransactionFilter
            
            budget_data = BudgetService.load_budget()
            if not budget_data:
                return pd.DataFrame({'Category': [], 'Spent': [], 'Budget': [], 'Percentage': []})
            
            # Get filtered transactions
            filtered_transactions = TransactionFilter.get_filtered_transactions(date_filter, filters)
            
            # Calculate spending by category
            spending_by_category = {}
            for transaction in filtered_transactions:
                if transaction.get('type', '').lower() == 'expense':
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
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
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
            )
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
    def _apply_world_class_css():
        """Apply world-class CSS inspired by Stripe, Coinbase, Robinhood"""
        st.markdown("""
        <style>
        /* World-class design system */
        :root {
            --surface-primary: #FFFFFF;
            --surface-secondary: #FAFBFC;
            --border-light: #E6E8EB;
            --text-primary: #0A0B0D;
            --text-secondary: #5A5D63;
            --text-tertiary: #8B949E;
            --positive: #00D924;
            --negative: #FF3B30;
            --neutral: #8E8E93;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
            --radius-md: 12px;
            --spacing-xs: 8px;
            --spacing-sm: 12px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
        }
        
        /* Page styling */
        .page-title {
            font-size: 2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0;
            letter-spacing: -0.02em;
        }
        
        .page-subtitle {
            color: var(--text-secondary);
            margin-bottom: var(--spacing-lg);
            font-size: 1rem;
        }
        
        /* Remove filter bar container styling since we're not using it */
        
        /* KPI Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-lg);
        }
        
        @media (max-width: 1024px) {
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 640px) {
            .kpi-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* KPI Card */
        .kpi-card {
            background: var(--surface-primary);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .kpi-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        
        .kpi-header {
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            margin-bottom: var(--spacing-xs);
        }
        
        .kpi-icon {
            width: 32px;
            height: 32px;
            background: var(--surface-secondary);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        
        .kpi-title {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: -0.01em;
        }
        
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            margin: var(--spacing-xs) 0;
        }
        
        .kpi-delta {
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: var(--spacing-xs);
        }
        
        .kpi-caption {
            font-size: 0.75rem;
            color: var(--text-tertiary);
            margin-top: auto;
        }
        
        /* Chart containers */
        .chart-container {
            background: var(--surface-primary);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--spacing-md);
        }
        
        .chart-container h2 {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--spacing-md);
            letter-spacing: -0.01em;
        }
        
        /* Streamlit overrides */
        div[data-testid="stVerticalBlock"] {
            gap: var(--spacing-sm);
        }
        
        .stButton > button {
            height: 40px;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .stSelectbox > div > div {
            height: 40px;
        }
        
        .stDateInput > div > div {
            height: 40px;
        }
        </style>
        """, unsafe_allow_html=True)