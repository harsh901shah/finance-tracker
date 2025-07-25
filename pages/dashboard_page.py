import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
from services.financial_data_service import TransactionService
from components.dashboard_analytics import DashboardAnalytics, DashboardFilters
from config.app_config import AppConfig

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
        
        # Render filter controls
        date_filter, filters, apply_filter = DashboardFilters.render_filter_controls()
        
        # Get transactions data (force refresh)
        transactions = cls._get_transactions_data()
        
        # Summary cards
        st.markdown("<div class='summary-cards'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        # Only load data if filter is applied
        if apply_filter:
            # Get real financial data with all filters
            current_month_data = DashboardAnalytics.get_filtered_data(date_filter, filters)
        else:
            # Show placeholder when filters not applied
            current_month_data = {'income': 0, 'expenses': 0}
            st.info("👆 Configure your filters and click 'Apply Filters' to view data")
        
        # Get trend data for comparison
        trends = DashboardAnalytics.calculate_trends(date_filter, filters) if apply_filter else {}
        
        with col1:
            income_trend = trends.get('income_trend', 0)
            has_trend_data = trends.get('has_previous_data', False)
            trend_text = f"{income_trend:+.1f}% vs prev period" if has_trend_data else "First period"
            cls._summary_card("Income", f"${current_month_data['income']:,.2f}", trend_text, "neutral" if not has_trend_data else ("positive" if income_trend >= 0 else "negative"))
        
        with col2:
            expense_trend = trends.get('expense_trend', 0)
            trend_text = f"{expense_trend:+.1f}% vs prev period" if has_trend_data else "First period"
            cls._summary_card("Expenses", f"${current_month_data['expenses']:,.2f}", trend_text, "neutral" if not has_trend_data else ("negative" if expense_trend > 0 else "positive"))
        
        with col3:
            net_income = current_month_data['income'] - current_month_data['expenses']
            net_trend = trends.get('net_trend', 0)
            trend_text = f"{net_trend:+.1f}% vs prev period" if has_trend_data else "First period"
            cls._summary_card("Net Income", f"${net_income:,.2f}", trend_text, "neutral" if not has_trend_data else ("positive" if net_income >= 0 else "negative"))
        
        with col4:
            savings_rate = (net_income / current_month_data['income'] * 100) if current_month_data['income'] > 0 else 0
            savings_trend = trends.get('savings_trend', 0)
            trend_text = f"{savings_trend:+.1f}% vs prev period" if has_trend_data else "First period"
            cls._summary_card("Savings Rate", f"{savings_rate:.1f}%", trend_text, "neutral" if not has_trend_data else ("positive" if savings_trend >= 0 else "negative"))
        
        # Second row - Additional insights
        col1, col2, col3, col4 = st.columns(4)
        
        # Get additional analytics - only if advanced analytics is enabled
        analytics = DashboardAnalytics.get_additional_analytics(date_filter, filters) if (apply_filter and AppConfig.FEATURES.get('advanced_analytics', True)) else {}
        
        with col1:
            transfers = analytics.get('transfers', 0)
            transfer_count = analytics.get('transfer_count', 0)
            cls._summary_card("Total Transfers", f"${transfers:,.2f}", f"{transfer_count} transactions", "neutral")
        
        with col2:
            top_category = analytics.get('top_category', 'N/A')
            top_amount = analytics.get('top_category_amount', 0)
            cls._summary_card("Top Category", top_category, f"${top_amount:,.2f}", "neutral")
        
        with col3:
            avg_transaction = analytics.get('avg_transaction', 0)
            transaction_count = analytics.get('transaction_count', 0)
            cls._summary_card("Avg Transaction", f"${avg_transaction:,.2f}", f"{transaction_count} total", "neutral")
        
        with col4:
            top_payment = analytics.get('top_payment_method', 'N/A')
            payment_count = analytics.get('top_payment_count', 0)
            cls._summary_card("Most Used Payment", top_payment, f"{payment_count} times", "neutral")
        
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
        
        # Budget progress - only show if budget tracking is enabled
        with col2:
            if AppConfig.FEATURES.get('budget_tracking', True):
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.markdown("<h2>Budget Progress</h2>", unsafe_allow_html=True)
                
                # Get real budget progress data
                budget_data = cls._get_real_budget_data()
                
                # Create budget progress chart
                fig = cls._create_budget_chart(budget_data)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.info("📊 Budget tracking is currently disabled")
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
        if change_type == "positive":
            change_color = "var(--positive-color)"
            change_icon = "↑"
        elif change_type == "negative":
            change_color = "var(--negative-color)"
            change_icon = "↓"
        else:  # neutral
            change_color = "var(--light-text-color)"
            change_icon = "ℹ️"
        
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
    def _get_filtered_data(date_filter=None, filters=None):
        """Get financial data with advanced filtering"""
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
                transaction_type = transaction.get('type', '')
                transaction_category = transaction.get('category', '')
                transaction_payment = transaction.get('payment_method', '')
                
                # Apply all filters
                # Date filter
                if date_filter:
                    if not (start_str <= transaction_date <= end_str):
                        continue
                else:
                    if not transaction_date.startswith(current_month):
                        continue
                
                # Transaction type filter
                if filters and filters.get('transaction_types') and transaction_type not in filters['transaction_types']:
                    continue
                
                # Category filter
                if filters and filters.get('categories') and transaction_category not in filters['categories']:
                    continue
                
                # Payment method filter
                if filters and filters.get('payment_methods') and transaction_payment not in filters['payment_methods']:
                    continue
                
                amount = float(transaction.get('amount', 0))
                transaction_type_lower = transaction_type.lower().strip()
                
                if transaction_type_lower in ['income']:
                    income += abs(amount)
                elif transaction_type_lower in ['expense']:
                    expenses += abs(amount)
            
            return {'income': income, 'expenses': expenses}
        except Exception as e:
            print(f"Error getting current month data: {e}")
            return {'income': 0, 'expenses': 0}
    
    @staticmethod
    def _get_additional_analytics(date_filter=None, filters=None):
        """Get additional analytics for enhanced summary cards"""
        try:
            transactions = TransactionService.load_transactions()
            
            if date_filter:
                start_date, end_date = date_filter
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
            else:
                current_month = datetime.now().strftime('%Y-%m')
            
            transfers = 0
            transfer_count = 0
            category_spending = {}
            payment_method_count = {}
            transaction_amounts = []
            
            for transaction in transactions:
                transaction_date = transaction.get('date', '')
                transaction_type = transaction.get('type', '')
                transaction_category = transaction.get('category', '')
                transaction_payment = transaction.get('payment_method', '')
                
                # Apply filters
                if date_filter:
                    if not (start_str <= transaction_date <= end_str):
                        continue
                else:
                    if not transaction_date.startswith(current_month):
                        continue
                
                if filters and filters.get('transaction_types') and transaction_type not in filters['transaction_types']:
                    continue
                if filters and filters.get('categories') and transaction_category not in filters['categories']:
                    continue
                if filters and filters.get('payment_methods') and transaction_payment not in filters['payment_methods']:
                    continue
                
                amount = abs(float(transaction.get('amount', 0)))
                transaction_amounts.append(amount)
                
                # Transfer analysis
                if transaction_type.lower() == 'transfer':
                    transfers += amount
                    transfer_count += 1
                
                # Category spending (expenses only)
                if transaction_type.lower() == 'expense':
                    category_spending[transaction_category] = category_spending.get(transaction_category, 0) + amount
                
                # Payment method usage
                payment_method_count[transaction_payment] = payment_method_count.get(transaction_payment, 0) + 1
            
            # Top category
            top_category = max(category_spending.items(), key=lambda x: x[1]) if category_spending else ('N/A', 0)
            
            # Top payment method
            top_payment = max(payment_method_count.items(), key=lambda x: x[1]) if payment_method_count else ('N/A', 0)
            
            # Average transaction
            avg_transaction = sum(transaction_amounts) / len(transaction_amounts) if transaction_amounts else 0
            
            return {
                'transfers': transfers,
                'transfer_count': transfer_count,
                'top_category': top_category[0],
                'top_category_amount': top_category[1],
                'avg_transaction': avg_transaction,
                'transaction_count': len(transaction_amounts),
                'top_payment_method': top_payment[0],
                'top_payment_count': top_payment[1]
            }
        except Exception as e:
            print(f"Error getting additional analytics: {e}")
            return {}
    
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
    def _calculate_trends(date_filter=None, filters=None):
        """Calculate trends by comparing current period with previous period"""
        try:
            if not date_filter:
                return {}
            
            start_date, end_date = date_filter
            period_days = (end_date - start_date).days
            
            # Calculate previous period (same duration)
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=period_days)
            
            # Get current period data
            current_data = DashboardPage._get_filtered_data(date_filter, filters)
            
            # Get previous period data
            prev_filter = (prev_start_date, prev_end_date)
            prev_data = DashboardPage._get_filtered_data(prev_filter, filters)
            
            # Calculate percentage changes
            def calc_change(current, previous):
                if previous == 0:
                    return 0  # No previous data to compare
                return ((current - previous) / previous) * 100
            
            current_income = current_data['income']
            current_expenses = current_data['expenses']
            current_net = current_income - current_expenses
            current_savings_rate = (current_net / current_income * 100) if current_income > 0 else 0
            
            prev_income = prev_data['income']
            prev_expenses = prev_data['expenses']
            prev_net = prev_income - prev_expenses
            prev_savings_rate = (prev_net / prev_income * 100) if prev_income > 0 else 0
            
            return {
                'income_trend': calc_change(current_income, prev_income),
                'expense_trend': calc_change(current_expenses, prev_expenses),
                'net_trend': calc_change(current_net, prev_net),
                'savings_trend': calc_change(current_savings_rate, prev_savings_rate)
            }
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
    
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