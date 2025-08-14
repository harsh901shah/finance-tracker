import streamlit as st
import pandas as pd
from datetime import datetime
from services.financial_data_service import BudgetService, TransactionService

class BudgetPage:
    """Budget planning and tracking page"""
    
    @staticmethod
    def show():
        # Move header to very top to avoid phantom elements
        st.markdown("""
        <style>
        section.main > div.block-container{padding-top:24px;padding-bottom:12px;overflow:visible;}
        div[data-testid="stVerticalBlock"]{gap:.6rem;}
        .budget-header{background:linear-gradient(135deg,#e9eef7 0%,#e6ecf7 100%);border-radius:14px;
          padding:12px 16px;margin:6px 0 10px;min-height:56px;display:flex;align-items:center;gap:10px;
          box-shadow:0 4px 16px rgba(0,0,0,.06);}
        .budget-header .title{font-weight:800;font-size:1.1rem;color:#1f2937;}
        .budget-header .sub{font-size:.95rem;color:#4b5563;}
        .budget-card{background:white;padding:1.5rem;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:1px solid #e2e8f0;margin-bottom:12px;}
        .progress-item{background:white;padding:1.25rem;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:12px;border-left:4px solid #e2e8f0;}
        .progress-item.healthy{border-left-color:#10b981;}
        .progress-item.warning{border-left-color:#f59e0b;}
        .progress-item.danger{border-left-color:#ef4444;}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="budget-header">
          <div class="title">💰 Budget Planning</div>
          <div class="sub">Track your spending against monthly budgets</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kill-switch to hide phantom boxes before main content
        st.markdown("""
        <style>
        /* Hide any phantom elements before budget cards */
        .budget-card:first-of-type::before,
        div[data-testid="stHorizontalBlock"]:has(.budget-card) ~ div:empty,
        div[data-testid="stVerticalBlock"] > div:empty {
            display: none !important;
        }
        /* Nuclear option: hide first 2 empty horizontal blocks */
        div[data-testid="stHorizontalBlock"]:empty:nth-of-type(1),
        div[data-testid="stHorizontalBlock"]:empty:nth-of-type(2) {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Load data
        budget_data = BudgetService.load_budget()
        transactions = TransactionService.load_transactions()
        
        # Calculate spending
        current_month = datetime.now().strftime('%Y-%m')
        monthly_spending = {}
        total_budget = sum(budget_data.values()) if budget_data else 0
        total_spent = 0
        
        for txn in transactions:
            if txn.get('date', '').startswith(current_month) and txn.get('type') == 'expense':
                category = txn.get('category', 'Other')
                amount = float(txn.get('amount', 0))
                monthly_spending[category] = monthly_spending.get(category, 0) + amount
                total_spent += amount
        
        # Overview metrics
        if total_budget > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Budget", f"${total_budget:,.0f}")
            with col2:
                st.metric("Total Spent", f"${total_spent:,.0f}")
            with col3:
                remaining = max(total_budget - total_spent, 0)
                st.metric("Remaining", f"${remaining:,.0f}")
            with col4:
                progress_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0
                st.metric("Progress", f"{progress_pct:.0f}%")
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 Set Monthly Budget")
            
            categories = {
                "🍽️ Food & Dining": "Food & Dining",
                "🚗 Transportation": "Transportation", 
                "🛍️ Shopping": "Shopping",
                "🎬 Entertainment": "Entertainment",
                "💡 Bills & Utilities": "Bills & Utilities",
                "🏥 Healthcare": "Healthcare",
                "✈️ Travel": "Travel",
                "📚 Education": "Education",
                "📦 Other": "Other"
            }
            
            with st.form("budget_form"):
                budget_amounts = {}
                for display_name, category in categories.items():
                    current_budget = budget_data.get(category, 0)
                    budget_amounts[category] = st.number_input(
                        display_name,
                        min_value=0.0,
                        value=float(current_budget),
                        step=50.0,
                        help=f"Set your monthly budget for {category.lower()}"
                    )
                
                submitted = st.form_submit_button("💾 Save Budget", use_container_width=True, type="primary")
                if submitted:
                    # Filter out zero amounts
                    filtered_budget = {k: v for k, v in budget_amounts.items() if v > 0}
                    if filtered_budget:
                        if BudgetService.save_budget(filtered_budget):
                            st.success("✅ Budget saved successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to save budget")
                    else:
                        st.warning("⚠️ Please enter at least one budget amount")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Budget Progress")
            
            if budget_data:
                for display_name, category in categories.items():
                    if category in budget_data and budget_data[category] > 0:
                        budget_amount = budget_data[category]
                        spent_amount = monthly_spending.get(category, 0)
                        progress = spent_amount / budget_amount
                        remaining = max(budget_amount - spent_amount, 0)
                        
                        # Status styling
                        if progress >= 1.0:
                            status_class = "danger"
                            status_text = "Over Budget"
                        elif progress >= 0.8:
                            status_class = "warning" 
                            status_text = "Nearly There"
                        else:
                            status_class = "healthy"
                            status_text = "On Track"
                        
                        st.markdown(f"""
                        <div class="progress-item {status_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <div style="display: flex; align-items: center;">
                                    <span style="font-size: 1.1rem; font-weight: 600;">{display_name}</span>
                                </div>
                                <span style="font-size: 0.8rem; color: #64748b; font-weight: 500;">{status_text}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="font-weight: 600;">${spent_amount:,.0f}</span>
                                <span style="color: #64748b;">of ${budget_amount:,.0f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.progress(min(progress, 1.0))
                        
                        if remaining > 0:
                            st.caption(f"💰 ${remaining:,.0f} remaining")
                        else:
                            over_budget = spent_amount - budget_amount
                            st.caption(f"⚠️ ${over_budget:,.0f} over budget")
                        

            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #e2e8f0;">
                    <h3 style="color: #64748b; margin-bottom: 1rem;">🎯 Ready to Start Budgeting?</h3>
                    <p style="color: #64748b; margin-bottom: 0;">Set your monthly budget amounts to start tracking your spending progress</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)