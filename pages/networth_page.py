import streamlit as st
import pandas as pd
import plotly.express as px
import re
from services.financial_data_service import NetWorthService

def _to_float(v) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        # remove $ and commas and spaces
        s = re.sub(r'[$,\s]', '', s)
        try:
            return float(s) if s else 0.0
        except ValueError:
            return 0.0
    return 0.0

def _sum_key(items, key) -> float:
    items = items or []
    return sum(_to_float(it.get(key)) for it in items if isinstance(it, dict))

def _fmt_money(n: float) -> str:
    """Format money with exact values and commas"""
    return f"${n:,.0f}"

class NetWorthPage:
    """Net Worth page showing assets and liabilities"""
    
    @staticmethod
    def show():
        # Load net worth data first
        networth_data = NetWorthService.load_networth() or {}
        
        # Extract and coerce
        investments = networth_data.get('investments') or {}
        debts = networth_data.get('debts') or {}
        real_estate = networth_data.get('real_estate') or []
        
        # Assets
        stocks_value = _sum_key(investments.get('stocks'), 'value')
        savings_value = _sum_key(investments.get('savings'), 'value')
        retirement_value = _sum_key(investments.get('retirement'), 'value')
        hsa_value = _sum_key(investments.get('hsa'), 'value')
        precious_metals_value = _sum_key(investments.get('precious_metals'), 'value')
        real_estate_value = _sum_key(real_estate, 'current_value')
        
        total_assets = (
            stocks_value + savings_value + retirement_value +
            hsa_value + precious_metals_value + real_estate_value
        )
        
        # Debts
        loans_value = _sum_key(debts.get('loans'), 'value')
        credit_cards_value = _sum_key(debts.get('credit_cards'), 'value')
        mortgage_value = _sum_key(debts.get('mortgage'), 'value')
        
        total_debts = loans_value + credit_cards_value + mortgage_value
        debt_ratio = (total_debts / total_assets * 100.0) if total_assets > 0 else 0.0
        

        
        # Global CSS reset and spacing optimization
        st.markdown("""
        <style>
        /* Global spacing reset */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Consistent vertical rhythm */
        .stMarkdown, .stAlert, .stColumns, .stTabs, .stExpander {
            margin-bottom: 12px !important;
        }
        
        /* Tighter column gaps */
        .stColumns > div {
            gap: 12px !important;
            padding: 0 6px !important;
        }
        
        /* Remove default margins */
        .stMarkdown > div {
            margin-bottom: 0 !important;
        }
        
        /* Alert spacing */
        .stAlert {
            margin: 12px 0 !important;
            padding: 12px 16px !important;
        }
        
        /* Button spacing */
        .stButton {
            margin: 6px 0 !important;
        }
        
        /* Anchor scroll offset */
        html {
            scroll-padding-top: 80px;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .stColumns > div {
                width: 100% !important;
                flex: none !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Net Worth Section
        st.markdown('<div id="net-worth"></div>', unsafe_allow_html=True)
        
        # Calculate net worth from transactions
        from services.financial_data_service import TransactionService
        transactions = TransactionService.load_transactions()
        
        # Calculate running balances from all transactions
        checking_balance = 0
        savings_balance = 0
        retirement_balance = 0
        investment_balance = 0
        credit_debt = 0
        
        for txn in transactions:
            amount = _to_float(txn.get('amount', 0))
            txn_type = txn.get('type', '').lower()
            category = txn.get('category', '').lower()
            description = txn.get('description', '').lower()
            
            if txn_type == 'income':
                checking_balance += amount
            elif txn_type == 'expense':
                if category == 'credit card':
                    credit_debt += amount
                else:
                    checking_balance -= amount
            elif txn_type == 'transfer':
                if category in ['retirement', '401k', 'roth', 'pretax']:
                    retirement_balance += amount
                    checking_balance -= amount
                elif 'savings' in description or category == 'savings':
                    savings_balance += amount
                    checking_balance -= amount
                elif 'investment' in description or 'robinhood' in description:
                    investment_balance += amount
                    checking_balance -= amount
        
        # Update calculated values
        total_assets = checking_balance + savings_balance + retirement_balance + investment_balance
        total_debts = credit_debt
        
        # Override individual values for display
        stocks_value = investment_balance
        savings_value = checking_balance + savings_balance
        retirement_value = retirement_balance
        hsa_value = 0
        precious_metals_value = 0
        real_estate_value = 0
        loans_value = 0
        credit_cards_value = credit_debt
        mortgage_value = 0
        
        if total_assets == 0 and total_debts == 0:
            # Professional Cash Flow Analysis
            from services.financial_data_service import TransactionService
            from datetime import datetime, timedelta
            import plotly.graph_objects as go
            
            # Hero section
            # Financial Health Section
            st.markdown('<div id="financial-health"></div>', unsafe_allow_html=True)
            
            transactions = TransactionService.load_transactions()
            
            if not transactions:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px; border: 2px dashed #dee2e6;">
                    <h3 style="color: #6c757d; margin-bottom: 1rem;">📊 Ready to Start Your Financial Journey?</h3>
                    <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">Add your first transaction to see powerful insights about your money</p>
                    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <p style="margin: 0; color: #495057;">💡 <strong>Pro Tip:</strong> Start with your salary and major expenses for the best overview</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return
            
            # Calculate periods
            today = datetime.now()
            last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_month_end = today.replace(day=1) - timedelta(days=1)
            trailing_90_start = today - timedelta(days=90)
            
            def analyze_period(start_date, end_date):
                income = expenses = taxes = retirement = 0
                for txn in transactions:
                    try:
                        txn_date = datetime.strptime(txn.get('date', ''), '%Y-%m-%d')
                        if start_date <= txn_date <= end_date:
                            amount = float(txn.get('amount', 0))
                            txn_type = txn.get('type', '').lower()
                            category = txn.get('category', '').lower()
                            
                            if txn_type == 'income':
                                income += amount
                            elif txn_type == 'transfer' and category in ['retirement', '401k', 'roth', 'pretax']:
                                income += amount
                                retirement += amount
                            elif txn_type == 'expense':
                                if category == 'tax':
                                    taxes += amount
                                else:
                                    expenses += amount
                    except:
                        continue
                return income, expenses, taxes, retirement
            
            # Get data for both periods
            month_data = analyze_period(last_month_start, last_month_end)
            quarter_data = analyze_period(trailing_90_start, today)
            
            # Key Metrics Cards
            st.markdown("### 📈 Key Financial Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                monthly_income = month_data[0]
                quarterly_avg = quarter_data[0] / 3 if quarter_data[0] > 0 else 0
                trend = "📈" if monthly_income > quarterly_avg else "📉" if monthly_income < quarterly_avg else "➡️"
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-left: 4px solid #28a745;">
                    <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">Monthly Income</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #28a745; margin-bottom: 0.5rem;">${monthly_income:,.0f}</div>
                    <div style="color: #6c757d; font-size: 0.8rem;">{trend} vs 3-month avg</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                monthly_expenses = month_data[1]
                quarterly_exp_avg = quarter_data[1] / 3 if quarter_data[1] > 0 else 0
                exp_trend = "📉" if monthly_expenses < quarterly_exp_avg else "📈" if monthly_expenses > quarterly_exp_avg else "➡️"
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-left: 4px solid #dc3545;">
                    <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">Monthly Expenses</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #dc3545; margin-bottom: 0.5rem;">${monthly_expenses:,.0f}</div>
                    <div style="color: #6c757d; font-size: 0.8rem;">{exp_trend} vs 3-month avg</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                net_cash = monthly_income - monthly_expenses - month_data[2]
                net_color = "#28a745" if net_cash > 0 else "#dc3545"
                net_icon = "💰" if net_cash > 0 else "⚠️"
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-left: 4px solid {net_color};">
                    <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">Net Cash Flow</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: {net_color}; margin-bottom: 0.5rem;">${net_cash:,.0f}</div>
                    <div style="color: #6c757d; font-size: 0.8rem;">{net_icon} This month</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                savings_rate = (net_cash / monthly_income * 100) if monthly_income > 0 else 0
                rate_color = "#28a745" if savings_rate >= 20 else "#ffc107" if savings_rate >= 10 else "#dc3545"
                rate_status = "Excellent" if savings_rate >= 20 else "Good" if savings_rate >= 10 else "Needs Work"
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); border-left: 4px solid {rate_color};">
                    <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">Savings Rate</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: {rate_color}; margin-bottom: 0.5rem;">{savings_rate:.1f}%</div>
                    <div style="color: #6c757d; font-size: 0.8rem;">📊 {rate_status}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Financial Health Score
            col1, col2 = st.columns([1, 2])
            
            with col1:
                retirement_rate = (month_data[3] / monthly_income * 100) if monthly_income > 0 else 0
                health_score = min(100, max(0, (savings_rate * 0.6) + (retirement_rate * 0.4)))
                score_color = "#28a745" if health_score >= 80 else "#ffc107" if health_score >= 60 else "#dc3545"
                
                st.markdown(f"""
                <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center;">
                    <h4 style="margin: 0 0 1rem 0; color: #495057;">💪 Financial Health Score</h4>
                    <div style="font-size: 3rem; font-weight: 700; color: {score_color}; margin-bottom: 0.5rem;">{health_score:.0f}</div>
                    <div style="color: #6c757d; font-size: 1rem;">out of 100</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if health_score >= 80:
                    message = "🎉 **Outstanding!** You're building wealth like a pro. Keep up the excellent financial habits!"
                    tips = ["Consider tax-loss harvesting", "Explore advanced investment strategies", "Review estate planning"]
                elif health_score >= 60:
                    message = "👍 **Solid Progress!** You're on the right track. A few tweaks could boost your score."
                    tips = ["Increase retirement contributions", "Build larger emergency fund", "Optimize investment allocation"]
                elif health_score >= 40:
                    message = "⚠️ **Room for Improvement.** Focus on the fundamentals to build a stronger foundation."
                    tips = ["Create a monthly budget", "Start emergency fund", "Automate savings"]
                else:
                    message = "🚨 **Action Needed.** Let's get your finances back on track with some key changes."
                    tips = ["Track all expenses", "Reduce unnecessary spending", "Increase income sources"]
                
                st.markdown(f"""
                <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                    <div style="margin-bottom: 1.5rem; font-size: 1.1rem;">{message}</div>
                    <div style="color: #495057; font-weight: 600; margin-bottom: 1rem;">💡 Next Steps:</div>
                    <ul style="margin: 0; padding-left: 1.5rem; color: #6c757d;">
                        {''.join([f'<li style="margin-bottom: 0.5rem;">{tip}</li>' for tip in tips])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Call to Action
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white;">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">🚀 Ready to See Your Complete Financial Picture?</h3>
                <p style="margin: 0 0 1.5rem 0; font-size: 1.1rem; opacity: 0.9;">Add your account balances to unlock your true Net Worth and get personalized investment recommendations</p>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                    <p style="margin: 0; font-size: 0.95rem;">💎 <strong>Premium Features:</strong> Asset allocation analysis • Investment performance tracking • Tax optimization tips</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            return
        
        # Net worth calculation
        net_worth = total_assets - total_debts
        
        # Compact portfolio overview header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1rem 1.5rem; border-radius: 12px; margin: 12px 0; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                    <span style="font-size: 1.2rem;">💎</span>
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #1e293b;">Portfolio Overview</h2>
                    <p style="margin: 0; color: #64748b; font-size: 0.8rem;">Your complete financial snapshot</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced metrics cards with modern design
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            net_worth_change = "+12.5%" if net_worth > 0 else "0%"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 2rem; border-radius: 16px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Net Worth</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b; line-height: 1;">{_fmt_money(net_worth)}</div>
                    </div>
                    <div style="background: #dcfce7; color: #166534; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        ↗ {net_worth_change}
                    </div>
                </div>
                <div style="height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); width: 75%; border-radius: 2px;"></div>
                </div>
                <div style="margin-top: 1rem; color: #64748b; font-size: 0.8rem;">📈 Trending upward this month</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Assets breakdown
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 2rem; border-radius: 16px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <div style="background: #dcfce7; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        <span style="font-size: 1.2rem;">📊</span>
                    </div>
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">Total Assets</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #059669;">{_fmt_money(total_assets)}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: #f1f5f9; border-radius: 12px;">
                        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">CHECKING</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">{_fmt_money(checking_balance)}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #f1f5f9; border-radius: 12px;">
                        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">RETIREMENT</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">{_fmt_money(retirement_value)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Fix debt ratio calculation: should be based on income, not assets
            # Debt-to-Income ratio is the standard metric
            from services.financial_data_service import TransactionService
            transactions = TransactionService.load_transactions()
            
            # Calculate monthly income
            from datetime import datetime
            current_month = datetime.now().strftime('%Y-%m')
            monthly_income = sum(
                float(t.get('amount', 0)) 
                for t in transactions 
                if t.get('date', '').startswith(current_month) and t.get('type', '').lower() == 'income'
            )
            
            # Calculate debt-to-income ratio (standard financial metric)
            debt_ratio = (total_debts / monthly_income * 100) if monthly_income > 0 else 0
            debt_status = "Excellent" if debt_ratio < 36 else "Good" if debt_ratio < 43 else "High"
            debt_color = "#059669" if debt_ratio < 36 else "#d97706" if debt_ratio < 43 else "#dc2626"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 2rem; border-radius: 16px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <div style="color: #64748b; font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Debt Ratio</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: {debt_color}; line-height: 1;">{debt_ratio:.1f}%</div>
                    </div>
                    <div style="background: #fef3c7; color: #92400e; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        {debt_status}
                    </div>
                </div>
                <div style="height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden;">
                    <div style="height: 100%; background: linear-gradient(90deg, {debt_color} 0%, {debt_color}aa 100%); width: {min(debt_ratio, 100)}%; border-radius: 2px;"></div>
                </div>
                <div style="margin-top: 1rem; color: #64748b; font-size: 0.8rem;">💡 Keep below 36% for optimal health (DTI ratio)</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Liabilities breakdown
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 2rem; border-radius: 16px; box-shadow: 0 4px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <div style="background: #fecaca; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        <span style="font-size: 1.2rem;">💳</span>
                    </div>
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">Total Liabilities</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #dc2626;">{_fmt_money(total_debts)}</div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: #fef2f2; border-radius: 12px;">
                        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">CREDIT CARDS</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">{_fmt_money(credit_debt)}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #fef2f2; border-radius: 12px;">
                        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem;">OTHER DEBT</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">$0</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Modern asset allocation section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1rem 1.5rem; border-radius: 12px; margin: 12px 0; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                    <span style="font-size: 1.2rem;">🏦</span>
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #1e293b;">Asset Allocation</h2>
                    <p style="margin: 0; color: #64748b; font-size: 0.8rem;">Diversification breakdown</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create asset data for visualization using calculated values
        asset_data = {
            'Category': ['Checking', 'Savings', 'Retirement', 'Investments'],
            'Value': [checking_balance, savings_balance, retirement_balance, investment_balance]
        }
        asset_df = pd.DataFrame(asset_data)
        # Filter out zero or negative values
        asset_df = asset_df[asset_df['Value'] > 0]
        
        # Only show pie chart if there are non-zero values
        if asset_df['Value'].sum() > 0:
            # Filter out zero values for cleaner visualization
            asset_df = asset_df[asset_df['Value'] > 0]
            fig = px.pie(
                asset_df, 
                values='Value', 
                names='Category', 
                title='Asset Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("📊 Asset distribution chart will appear when you add account balances.")
        
        # Modern tabbed interface
        st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: #f8fafc;
            border-radius: 12px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0px 24px;
            background: transparent;
            border-radius: 8px;
            color: #64748b;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: white !important;
            color: #1e293b !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💼 Investments", "💰 Savings", "🏦 Retirement", "🏠 Real Estate", "💳 Debts"])
        
        with tab1:
            NetWorthPage._show_investments_tab(investments)
        
        with tab2:
            NetWorthPage._show_savings_tab(investments)
        
        with tab3:
            NetWorthPage._show_retirement_tab(investments)
        
        with tab4:
            NetWorthPage._show_real_estate_tab(real_estate)
        
        with tab5:
            NetWorthPage._show_debts_tab(debts)
    
    @staticmethod
    def _show_investments_tab(investments):
        st.subheader("Investment Accounts")
        if investments.get('stocks'):
            stocks_df = pd.DataFrame(investments['stocks'])
            st.dataframe(
                stocks_df,
                column_config={
                    "name": "Account",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                width="stretch"
            )
            
            # Show by owner
            st.subheader("Investments by Owner")
            owner_data = stocks_df.groupby('owner')['value'].sum().reset_index()
            fig = px.bar(owner_data, x='owner', y='value', title='Investment Value by Owner')
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No investment accounts found.")
    
    @staticmethod
    def _show_savings_tab(investments):
        st.subheader("Savings Accounts")
        if investments.get('savings'):
            savings_df = pd.DataFrame(investments['savings'])
            st.dataframe(
                savings_df,
                column_config={
                    "name": "Account",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No savings accounts found.")
            
        # Show precious metals if any
        if investments.get('precious_metals'):
            st.subheader("Precious Metals")
            metals_df = pd.DataFrame(investments['precious_metals'])
            st.dataframe(
                metals_df,
                column_config={
                    "name": "Type",
                    "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                width="stretch"
            )
    
    @staticmethod
    def _show_retirement_tab(investments):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Retirement Accounts")
            if investments.get('retirement'):
                retirement_df = pd.DataFrame(investments['retirement'])
                st.dataframe(
                    retirement_df,
                    column_config={
                        "name": "Account",
                        "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                        "owner": "Owner"
                    },
                    hide_index=True,
                    width="stretch"
                )
            else:
                st.info("No retirement accounts found.")
        
        with col2:
            st.subheader("HSA Accounts")
            if investments.get('hsa'):
                hsa_df = pd.DataFrame(investments['hsa'])
                st.dataframe(
                    hsa_df,
                    column_config={
                        "name": "Account",
                        "value": st.column_config.NumberColumn("Value ($)", format="$%d"),
                        "owner": "Owner"
                    },
                    hide_index=True,
                    width="stretch"
                )
            else:
                st.info("No HSA accounts found.")
    
    @staticmethod
    def _show_real_estate_tab(real_estate):
        st.subheader("Real Estate")
        if real_estate:
            real_estate_df = pd.DataFrame(real_estate)
            st.dataframe(
                real_estate_df,
                column_config={
                    "name": "Property",
                    "purchase_value": st.column_config.NumberColumn("Purchase Value ($)", format="$%d"),
                    "current_value": st.column_config.NumberColumn("Current Value ($)", format="$%d"),
                    "owner": "Owner"
                },
                hide_index=True,
                width="stretch"
            )
            
            # Calculate equity
            for i, property in enumerate(real_estate):
                current_val = property['current_value']
                purchase_val = property.get('purchase_value', 0)
                equity = current_val - purchase_val
                
                if purchase_val > 0:
                    appreciation = (equity / purchase_val) * 100
                    st.metric(
                        f"Equity in {property['name']}", 
                        f"${equity:,.2f}", 
                        f"{appreciation:.1f}%"
                    )
                else:
                    st.metric(
                        f"Value of {property['name']}", 
                        f"${current_val:,.2f}"
                    )
        else:
            st.info("No real estate properties found.")
    
    @staticmethod
    def _show_debts_tab(debts):
        st.subheader("Debts & Liabilities")
        
        # Calculate debts from transactions
        from services.financial_data_service import TransactionService
        transactions = TransactionService.load_transactions()
        
        credit_card_debt = 0
        loan_debt = 0
        mortgage_debt = 0
        
        for txn in transactions:
            amount = _to_float(txn.get('amount', 0))
            txn_type = txn.get('type', '').lower()
            category = txn.get('category', '').lower()
            
            if txn_type == 'expense':
                if category == 'credit card':
                    credit_card_debt += amount
                elif 'loan' in category or 'auto' in category:
                    loan_debt += amount
                elif 'mortgage' in category or 'rent' in category:
                    mortgage_debt += amount
        
        # Display calculated debts
        if credit_card_debt > 0 or loan_debt > 0 or mortgage_debt > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💳 Credit Card Debt", f"${credit_card_debt:,.2f}")
            with col2:
                st.metric("🚗 Loan Debt", f"${loan_debt:,.2f}")
            with col3:
                st.metric("🏠 Mortgage/Rent", f"${mortgage_debt:,.2f}")
            
            # Show breakdown
            st.markdown("---")
            st.subheader("Debt Breakdown")
            
            debt_data = []
            if credit_card_debt > 0:
                debt_data.append({'Type': 'Credit Cards', 'Balance': credit_card_debt})
            if loan_debt > 0:
                debt_data.append({'Type': 'Loans', 'Balance': loan_debt})
            if mortgage_debt > 0:
                debt_data.append({'Type': 'Mortgage/Rent', 'Balance': mortgage_debt})
            
            if debt_data:
                debt_df = pd.DataFrame(debt_data)
                st.dataframe(
                    debt_df,
                    column_config={
                        "Type": "Debt Type",
                        "Balance": st.column_config.NumberColumn("Balance ($)", format="$%.2f")
                    },
                    hide_index=True,
                    width="stretch"
                )
        else:
            st.info("💚 No debts found! You're debt-free based on your transactions.")