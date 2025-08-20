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
        # Clear cache to ensure fresh data
        TransactionService.clear_cache()
        
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
            current_month_data = cls._get_filtered_data(date_filter, filters)
        else:
            current_month_data = cls._get_filtered_data()
        
        # Get trend data for comparison
        trends = cls._calculate_trends(date_filter, filters) if apply_filter else {}
        
        # Get additional analytics
        if apply_filter:
            analytics = cls._get_additional_analytics(date_filter, filters) if AppConfig.FEATURES.get('advanced_analytics', True) else {}
        else:
            analytics = cls._get_additional_analytics() if AppConfig.FEATURES.get('advanced_analytics', True) else {}
        
        # World-class KPI grid
        from components.dashboard_filters import render_kpi_grid
        
        # Calculate all KPI values
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
            }
        ]
        
        render_kpi_grid(kpis)
        
        # Cash flow chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Cash Flow</h2>", unsafe_allow_html=True)
        
        # Get real cash flow data with timeline view (6 months default)
        cash_flow_data = cls._get_real_cash_flow_data(date_filter if apply_filter else None, months_to_show=6)
        
        # Create modern timeline cash flow chart
        fig = cls._create_cash_flow_chart(cash_flow_data, months_to_show=6)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Two-column section with robust data handling
        col1, col2 = st.columns(2)
        
        # Get and normalize transaction data with period filter
        tx_data = cls._get_normalized_transactions(transactions, date_filter if apply_filter else None)
        
        with col1:
            st.markdown("### Spending by Category")
            st.caption("Current month breakdown")
            
            if tx_data['total_spent'] <= 0:
                st.info("No spending in the selected month.")
            else:
                # Show total
                st.metric("Total Spent", f"${tx_data['total_spent']:,.0f}")
                
                # Show top categories
                for cat, amt in tx_data['top_categories']:
                    pct = amt/tx_data['total_spent']*100
                    st.write(f"**{cat}**: ${amt:,.0f} ({pct:.1f}%)")
        
        with col2:
            st.markdown("### Budget Progress")
            st.caption("Monthly budget tracking")
            
            budget_data = cls._get_budget_progress(tx_data['spending_by_category'], date_filter if apply_filter else None)
            
            if not budget_data:
                st.info("No budgets set or no spending this month.")
            else:
                for item in budget_data:
                    color = "🟢" if item['pct'] <= 100 else "🔴"
                    st.write(f"{color} **{item['category']}**: ${item['spent']:,.0f} / ${item['budget']:,.0f} ({item['pct']:.1f}%)")
                    st.progress(min(item['pct']/100, 1.0))

        
        # Recent transactions
        st.markdown("<div class='transactions-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Recent Transactions</h2>", unsafe_allow_html=True)
        
        # Get real recent transactions data with period filter
        transactions_data = cls._get_real_recent_transactions(date_filter if apply_filter else None)
        
        # Display transactions table
        cls._display_transactions_table(transactions_data)
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def _render_compact_filter_bar():
        """Render compact single-row filter bar"""
        # Get filter controls once to avoid duplicate IDs
        date_filter, filters, apply_filter = DashboardFilters.render_filter_controls()
        return date_filter, filters, apply_filter
    

    
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
    def _get_filtered_data(date_filter=None, filters=None):
        """Get financial data with advanced filtering"""
        try:
            transactions = TransactionService.load_transactions()
            
            if date_filter:
                start_date, end_date = date_filter
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
            
            income = 0
            expenses = 0
            
            for transaction in transactions:
                transaction_date = transaction.get('date', '')
                transaction_type = transaction.get('type', '')
                transaction_category = transaction.get('category', '')
                transaction_payment = transaction.get('payment_method', '')
                
                # Apply date filter only if specified
                if date_filter:
                    if not (start_str <= transaction_date <= end_str):
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
                
                # Include pre-tax and Roth contributions as income since they represent earned money
                if transaction_type_lower in ['income'] or (transaction_type_lower == 'transfer' and transaction_category.lower() in ['retirement', '401k', 'roth', 'pretax']):
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
                
                # Apply date filter only if specified
                if date_filter:
                    if not (start_str <= transaction_date <= end_str):
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
    def _get_real_cash_flow_data(date_filter=None, months_to_show=6):
        """Get cash flow data with consistent monthly timeline (presentation only)"""
        try:
            transactions = TransactionService.load_transactions()
            
            # Show from January to current month
            end_date = datetime.now()
            start_date = datetime(end_date.year, 1, 1)  # January 1st of current year
            
            # Initialize all months from Jan to current month with zeros
            monthly_data = {}
            current_date = start_date
            while current_date <= end_date:
                month_key = current_date.strftime('%Y-%m')
                month_name = current_date.strftime('%b')
                monthly_data[month_key] = {
                    'month_name': month_name,
                    'income': 0,
                    'expenses': 0
                }
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Process transactions (unchanged logic)
            for transaction in transactions:
                try:
                    transaction_date = datetime.strptime(transaction.get('date', ''), '%Y-%m-%d')
                    month_key = transaction_date.strftime('%Y-%m')
                    
                    if month_key in monthly_data:
                        amount = float(transaction.get('amount', 0))
                        transaction_type = transaction.get('type', '').lower().strip()
                        
                        if transaction_type in ['income'] or (transaction_type == 'transfer' and transaction.get('category', '').lower() in ['retirement', '401k', 'roth', 'pretax']):
                            monthly_data[month_key]['income'] += abs(amount)
                        elif transaction_type in ['expense']:
                            monthly_data[month_key]['expenses'] += abs(amount)
                except (ValueError, TypeError):
                    continue
            
            # Create timeline DataFrame
            months = []
            income = []
            expenses = []
            net_clamped = []
            deficit = []
            
            for month_key in sorted(monthly_data.keys()):
                data = monthly_data[month_key]
                income_total = data['income']
                expense_total = data['expenses']
                net_raw = income_total - expense_total
                
                months.append(data['month_name'])
                income.append(income_total)
                expenses.append(expense_total)
                net_clamped.append(max(0.0, net_raw))
                deficit.append(max(0.0, -net_raw))
            
            return pd.DataFrame({
                'Month': months,
                'Income': income,
                'Expenses': expenses,
                'Net': net_clamped,
                'Deficit': deficit
            })
            
        except Exception:
            return pd.DataFrame({
                'Month': [],
                'Income': [],
                'Expenses': [],
                'Net': [],
                'Deficit': []
            })
    
    @staticmethod
    def _create_cash_flow_chart(data, months_to_show=6):
        """Create modern finance app timeline chart (Credit Karma style)"""
        if data.empty:
            return go.Figure()
        
        months = data['Month'].tolist()
        incomes = data['Income'].tolist()
        expenses = data['Expenses'].tolist()
        net_values = data['Net'].tolist()
        deficits = data['Deficit'].tolist()
        
        # Calculate nice y-axis max
        max_val = max(max(incomes + expenses + net_values, default=0), 100)
        def nice_max(val):
            """Round up to nice tick values"""
            if val <= 1000: return ((val // 100) + 1) * 100
            elif val <= 5000: return ((val // 500) + 1) * 500
            elif val <= 10000: return ((val // 1000) + 1) * 1000
            else: return ((val // 5000) + 1) * 5000
        
        y_max = nice_max(max_val * 1.15)
        
        fig = go.Figure()
        
        # Income bar (base layer)
        fig.add_trace(go.Bar(
            name="Income",
            x=months,
            y=incomes,
            width=0.58,
            marker=dict(color="#22c55e"),
            marker_line_width=0,
            text=[f"${v:,.0f}" if v > 0 else "" for v in incomes],
            textposition="outside",
            cliponaxis=False,
            textfont_size=11,
            hovertemplate="%{x}<br>Income: $%{y:,.0f}<extra></extra>"
        ))
        
        # Expenses bar (overlay, renders on top)
        fig.add_trace(go.Bar(
            name="Expenses",
            x=months,
            y=expenses,
            width=0.58,
            marker=dict(
                color="rgba(239,68,68,0.35)",
                line=dict(width=0)
            ),
            text=[f"${v:,.0f}" if v > 0 else "" for v in expenses],
            textposition="outside",
            cliponaxis=False,
            textfont_size=11,
            hovertemplate="%{x}<br>Expenses: $%{y:,.0f}<extra></extra>"
        ))
        
        # Net line (blue) - uses same categorical labels for center alignment
        fig.add_trace(go.Scatter(
            name="Net",
            x=months,  # Same categorical labels as bars
            y=net_values,
            mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8, color="#2563eb"),
            hovertemplate="%{x}<br>Net: $%{y:,.0f}<extra></extra>"
        ))
        
        # Annotations for no income months
        for month, net_y, income, deficit in zip(months, net_values, incomes, deficits):
            if income == 0 and deficit > 0:
                fig.add_annotation(
                    x=month,
                    y=0,
                    text="No income recorded",
                    showarrow=False,
                    yshift=15,
                    font=dict(size=10, color="#64748b")
                )
        
        # Professional layout (Credit Karma style)
        fig.update_layout(
            barmode="overlay",
            bargap=0.30,
            legend=dict(
                orientation="h",
                y=1.08,
                x=1.0,
                xanchor="right",
                font_size=12
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=24, r=24, b=48, l=64),
            autosize=True,
            font=dict(family="Inter, sans-serif", size=12, color="#374151")
        )
        
        # Professional axis styling
        fig.update_yaxes(
            rangemode="tozero",
            range=[0, y_max],
            tickformat="$~s",  # Compact currency format ($1k, $2k, etc.)
            showgrid=True,
            gridcolor="#f3f4f6",
            gridwidth=1,
            tickcolor="#d1d5db",
            linecolor="#d1d5db"
        )
        
        fig.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=months,
            showgrid=False,
            tickcolor="#d1d5db",
            linecolor="#d1d5db",
            tickangle=0
        )
        
        # Bars styled directly in traces above
        
        # Config will be passed to st.plotly_chart() instead
        
        return fig
    
    @staticmethod
    def _get_normalized_transactions(transactions, date_filter=None):
        """Get normalized transaction data with robust filtering and period support"""
        if date_filter:
            start_date, end_date = date_filter
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
        else:
            current_month = datetime.now().strftime('%Y-%m')
            start_str = end_str = None
        
        # Normalize and filter transactions
        spending_by_category = {}
        total_spent = 0
        
        for tx in transactions:
            # Normalize fields
            tx_date = str(tx.get('date', '')).strip()
            tx_type = str(tx.get('type', '')).lower().strip()
            tx_category = str(tx.get('category', 'Other')).strip()
            
            try:
                tx_amount = abs(float(tx.get('amount', 0)))
            except (ValueError, TypeError):
                tx_amount = 0
            
            # Filter for period expenses
            date_match = False
            if date_filter:
                date_match = start_str <= tx_date <= end_str
            else:
                date_match = tx_date.startswith(current_month)
            
            if date_match and tx_type == 'expense' and tx_amount > 0:
                spending_by_category[tx_category] = spending_by_category.get(tx_category, 0) + tx_amount
                total_spent += tx_amount
        
        # Get top categories
        top_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'spending_by_category': spending_by_category,
            'total_spent': total_spent,
            'top_categories': top_categories
        }
    
    @staticmethod
    def _get_budget_progress(spending_by_category, date_filter=None):
        """Get budget progress data with spending matched to budgets for specific period"""
        try:
            from services.financial_data_service import BudgetService
            
            # Get budget for specific period if provided
            if date_filter:
                start_date, _ = date_filter
                month = start_date.strftime('%m')
                year = start_date.year
                budgets = BudgetService.load_budget(month=month, year=year)
            else:
                budgets = BudgetService.load_budget()
            
            if not budgets:
                return []
            
            budget_progress = []
            
            # Check each budget category
            for category, budget_amount in budgets.items():
                category = str(category).strip()
                try:
                    budget_amount = float(budget_amount)
                except (ValueError, TypeError):
                    budget_amount = 0
                
                if budget_amount <= 0:
                    continue
                
                # Find matching spending (normalize category names)
                spent = 0
                for spend_cat, spend_amt in spending_by_category.items():
                    if str(spend_cat).strip().lower() == category.lower():
                        spent = spend_amt
                        break
                
                pct = (spent / budget_amount * 100) if budget_amount > 0 else 0
                
                budget_progress.append({
                    'category': category,
                    'spent': spent,
                    'budget': budget_amount,
                    'pct': pct
                })
            
            # Sort by percentage used
            budget_progress.sort(key=lambda x: x['pct'], reverse=True)
            return budget_progress
            
        except Exception as e:
            print(f"Budget progress error: {e}")
            return []
    
    @staticmethod
    def _get_spending_data(transactions):
        """Get spending data for current month"""
        current_month = datetime.now().strftime('%Y-%m')
        expense_transactions = [t for t in transactions if 
                              t.get('date', '').startswith(current_month) and 
                              t.get('type', '').lower() == 'expense']
        
        if not expense_transactions:
            return None
            
        category_spending = {}
        total_spent = 0
        for transaction in expense_transactions:
            category = transaction.get('category', 'Other')
            amount = abs(float(transaction.get('amount', 0)))
            category_spending[category] = category_spending.get(category, 0) + amount
            total_spent += amount
        
        return {
            'category_spending': category_spending,
            'total_spent': total_spent,
            'transaction_count': len(expense_transactions)
        }
    
    @staticmethod
    def _render_spending_content(spending_data):
        """Render spending content as HTML"""
        if not spending_data:
            return '''
            <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 8px; border: 2px dashed #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 16px;">📊</div>
                <h4 style="color: #64748b; margin-bottom: 8px;">No Spending Data</h4>
                <p style="color: #64748b; margin: 0;">Start tracking expenses to see breakdown</p>
            </div>
            '''
        
        category_spending = spending_data['category_spending']
        total_spent = spending_data['total_spent']
        
        # Create simple category list
        top_5 = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        category_html = ''
        for cat, amt in top_5:
            pct = amt/total_spent*100
            category_html += f'''
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                <span style="font-weight: 500;">{cat}</span>
                <span style="color: #64748b;">${amt:,.0f} ({pct:.1f}%)</span>
            </div>
            '''
        
        return f'''
        <div style="margin-bottom: 16px;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">${total_spent:,.0f}</div>
            <div style="color: #64748b;">Total spent this month</div>
        </div>
        <div>{category_html}</div>
        '''
    
    @staticmethod
    def _render_budget_content(budget_data):
        """Render budget content as HTML"""
        if budget_data.empty:
            return '''
            <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 8px; border: 2px dashed #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 16px;">🎯</div>
                <h4 style="color: #64748b; margin-bottom: 8px;">No Budget Set</h4>
                <p style="color: #64748b; margin: 0;">Go to Budget Planning to set limits</p>
            </div>
            '''
        
        # Filter active categories
        active_data = budget_data[(budget_data['Budget'] > 0) | (budget_data['Spent'] > 0)]
        
        if active_data.empty:
            return '''
            <div style="text-align: center; padding: 2rem;">
                <p style="color: #64748b;">No budget categories with activity</p>
            </div>
            '''
        
        budget_html = ''
        for _, row in active_data.iterrows():
            pct = row['Percentage']
            color = '#16a34a' if pct <= 100 else '#ef4444'
            budget_html += f'''
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 500;">{row['Category']}</span>
                    <span style="color: #64748b;">${row['Spent']:,.0f} / ${row['Budget']:,.0f}</span>
                </div>
                <div style="width: 100%; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;">
                    <div style="width: {min(pct, 100)}%; height: 100%; background: {color};"></div>
                </div>
            </div>
            '''
        
        return budget_html
    
    @staticmethod
    def _render_spending_section_old(transactions, active_period_label):
        """Render spending by category section with professional empty state"""
        # Filter for expenses in current period
        current_month = datetime.now().strftime('%Y-%m')
        expense_transactions = [t for t in transactions if 
                              t.get('date', '').startswith(current_month) and 
                              t.get('type', '').lower() == 'expense']
        
        if not expense_transactions:
            # Empty state with proper Streamlit components
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                        border: 2px dashed #e5e7eb; border-radius: 14px; padding: 32px; 
                        text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
                <h3 style="color: #0f172a; font-weight: 600; margin-bottom: 8px;">No Spending Data</h3>
                <p style="color: #64748b; margin-bottom: 24px;">Start tracking your expenses to see category breakdown</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Buttons using Streamlit components
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.button("Add Expense", type="primary", use_container_width=True)
                with btn_col2:
                    st.button("Import CSV", use_container_width=True)
            
            # Tips as markdown
            st.markdown("""
            <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 16px;">
                <span style="background: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 20px; font-size: 0.875rem;">Try: Groceries</span>
                <span style="background: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 20px; font-size: 0.875rem;">Rent</span>
                <span style="background: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 20px; font-size: 0.875rem;">Utilities</span>
                <span style="background: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 20px; font-size: 0.875rem;">Transportation</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Data state with KPIs and charts
            category_spending = {}
            total_spent = 0
            for transaction in expense_transactions:
                category = transaction.get('category', 'Other')
                amount = abs(float(transaction.get('amount', 0)))
                category_spending[category] = category_spending.get(category, 0) + amount
                total_spent += amount
            
            top_category = max(category_spending.items(), key=lambda x: x[1])[0] if category_spending else 'N/A'
            
            # KPI header
            st.markdown(f"""
            <div style="display: flex; gap: 24px; margin-bottom: 16px; padding: 16px; 
                        background: #f8fafc; border-radius: 8px;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">${total_spent:,.0f}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Total Spent</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">{len(expense_transactions)}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Transactions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; font-weight: 600; color: #0f172a;">{top_category}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Top Category</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show donut chart
            df = pd.DataFrame(list(category_spending.items()), columns=['Category', 'Amount'])
            fig = go.Figure(data=[go.Pie(
                labels=df['Category'], values=df['Amount'], hole=.5,
                marker_colors=['#4f46e5', '#16a34a', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            )])
            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            fig.add_annotation(text=f"${total_spent:,.0f}", x=0.5, y=0.5, font_size=20, showarrow=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Only show top categories bar if more than one category
            if len(category_spending) > 1:
                st.markdown("**Top Categories**")
                top_5 = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
                
                fig = go.Figure()
                for i, (cat, amt) in enumerate(top_5):
                    pct = amt/total_spent*100
                    fig.add_trace(go.Bar(
                        y=[cat], x=[pct], orientation='h',
                        marker_color=['#4f46e5', '#16a34a', '#f59e0b', '#ef4444', '#8b5cf6'][i],
                        text=f'${amt:,.0f}', textposition='auto', showlegend=False
                    ))
                
                fig.update_layout(
                    height=max(120, len(top_5) * 30),
                    margin=dict(l=0,r=0,t=0,b=0),
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
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
        # Filter to only categories with budget or spending
        active_data = data[(data['Budget'] > 0) | (data['Spent'] > 0)]
        
        if active_data.empty:
            return None
            
        fig = go.Figure()
        
        for i, row in active_data.iterrows():
            color = '#16a34a' if row['Percentage'] <= 100 else '#ef4444'
            
            fig.add_trace(go.Bar(
                x=[row['Percentage']],
                y=[row['Category']],
                orientation='h',
                showlegend=False,
                marker_color=color,
                text=f"${row['Spent']:,.0f} / ${row['Budget']:,.0f}",
                textposition='auto'
            ))
        
        fig.update_layout(
            height=max(120, len(active_data) * 40),
            margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(
                showgrid=False,
                showticklabels=len(active_data) > 1,
                ticksuffix='%' if len(active_data) > 1 else ''
            ),
            yaxis=dict(showgrid=False)
        )
        
        return fig
    
    @staticmethod
    def _get_real_recent_transactions(date_filter=None):
        """Get real recent transactions data with optional period filter"""
        try:
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                return []
            
            # Filter by date if provided
            if date_filter:
                start_date, end_date = date_filter
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                transactions = [t for t in transactions if start_str <= t.get('date', '') <= end_str]
            
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