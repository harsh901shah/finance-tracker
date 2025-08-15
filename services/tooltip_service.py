"""
Tooltip and Help Service for providing contextual guidance
"""
import streamlit as st
from typing import Dict, Any

class TooltipService:
    """Service for managing tooltips and contextual help"""
    
    TOOLTIPS = {
        # Transaction Types
        'income': "💰 Money you receive from salary, freelance work, investments, or other sources",
        'expense': "💸 Money you spend on goods, services, or bills",
        'tax': "🏛️ Tax payments to government (income tax, property tax, etc.)",
        'transfer': "🔄 Moving money between your own accounts (doesn't affect net worth)",
        'investment': "📈 Money invested in stocks, bonds, retirement accounts, etc.",
        
        # Categories
        'housing': "🏠 Rent, mortgage, utilities, home maintenance, insurance",
        'transportation': "🚗 Car payments, gas, insurance, public transit, rideshare",
        'food': "🍕 Groceries, restaurants, takeout, coffee",
        'healthcare': "🏥 Medical bills, insurance premiums, prescriptions, dental",
        'entertainment': "🎬 Movies, concerts, streaming services, hobbies",
        'shopping': "🛍️ Clothing, electronics, household items",
        'education': "📚 Tuition, books, courses, training",
        'travel': "✈️ Flights, hotels, vacation expenses",
        'debt_payment': "💳 Credit card payments, loan payments (principal + interest)",
        'savings': "🏦 Money moved to savings accounts or emergency funds",
        'retirement': "👴 401k contributions, IRA contributions, pension",
        'insurance': "🛡️ Life, disability, umbrella insurance premiums",
        'taxes': "📋 Income tax, property tax, sales tax payments",
        'gifts_donations': "🎁 Charitable donations, gifts to family/friends",
        'business': "💼 Business expenses, equipment, supplies",
        'other': "📝 Miscellaneous expenses that don't fit other categories",
        
        # Payment Methods
        'cash': "💵 Physical cash payments",
        'debit_card': "💳 Direct payment from checking account",
        'credit_card': "💳 Payment using credit card (creates debt)",
        'bank_transfer': "🏦 Electronic transfer between bank accounts",
        'check': "📝 Paper check payments",
        'digital_wallet': "📱 PayPal, Venmo, Apple Pay, Google Pay",
        'auto_pay': "🔄 Automatic recurring payments",
        
        # Financial Health
        'net_worth': "💎 Your total assets minus total liabilities - measures overall financial health",
        'emergency_fund': "🚨 3-6 months of expenses saved for unexpected situations",
        'debt_to_income': "📊 Percentage of monthly income going to debt payments (should be <36%)",
        'savings_rate': "📈 Percentage of income you save each month (aim for 20%+)",
        
        # Budget Planning
        'budget_category': "📋 Planned spending limit for each expense category",
        'budget_vs_actual': "⚖️ Comparison between what you planned to spend vs what you actually spent",
        'budget_variance': "📏 Difference between budgeted and actual amounts (positive = under budget)",
        
        # Account Types
        'checking': "🏦 Primary account for daily transactions and bill payments",
        'savings': "💰 Account for storing emergency funds and short-term goals",
        'investment': "📈 Brokerage accounts, retirement accounts (401k, IRA)",
        'credit': "💳 Credit cards and lines of credit (liabilities)",
        'loan': "🏠 Mortgages, auto loans, personal loans (liabilities)",
    }
    
    ONBOARDING_STEPS = {
        'welcome': {
            'title': "Welcome to Your Personal Finance Tracker! 🎉",
            'content': """
            This app helps you track expenses, manage budgets, and build wealth.
            
            **Getting Started:**
            1. Add your first transaction
            2. Set up monthly budgets
            3. Track your net worth growth
            4. Review financial insights
            """,
            'next_action': "Let's add your first transaction!"
        },
        'first_transaction': {
            'title': "Add Your First Transaction 💰",
            'content': """
            **Transaction Types:**
            - **Income**: Salary, freelance, investments
            - **Expense**: Bills, shopping, entertainment
            - **Tax**: Government tax payments
            - **Transfer**: Moving money between accounts
            - **Investment**: Retirement contributions, stocks
            
            **Pro Tip**: Start with recent transactions to see immediate results!
            """,
            'next_action': "Add a transaction to continue"
        },
        'budget_setup': {
            'title': "Set Your Monthly Budget 📊",
            'content': """
            **Why Budget?**
            - Track spending vs goals
            - Identify overspending areas
            - Build better financial habits
            
            **Popular Budget Rules:**
            - 50/30/20: 50% needs, 30% wants, 20% savings
            - Zero-based: Every dollar has a purpose
            """,
            'next_action': "Set up your first budget category"
        },
        'net_worth_explained': {
            'title': "Understanding Net Worth 💎",
            'content': """
            **Net Worth = Assets - Liabilities**
            
            **Assets**: What you own
            - Cash, investments, property
            
            **Liabilities**: What you owe
            - Credit cards, loans, mortgages
            
            **Goal**: Increase net worth over time by earning more, spending less, and investing wisely.
            """,
            'next_action': "View your net worth dashboard"
        }
    }
    
    @classmethod
    def show_tooltip(cls, key: str, icon: str = "ℹ️"):
        """Display tooltip for a given key with optional icon.
        
        Args:
            key: The tooltip key to look up
            icon: Icon to display with the tooltip
        """
        if key in cls.TOOLTIPS:
            st.info(f"{icon} {cls.TOOLTIPS[key]}")
    
    @classmethod
    def get_tooltip_text(cls, key: str) -> str:
        """Get tooltip text for a specific key.
        
        Args:
            key: The tooltip key to retrieve
            
        Returns:
            str: The tooltip text or default message if not found
        """
        return cls.TOOLTIPS.get(key, "No help available for this item")
    
    @classmethod
    def show_contextual_help(cls, context: str):
        """Show contextual help based on current page/context.
        
        Args:
            context: The current page or context identifier
        """
        if context == 'add_transaction':
            with st.expander("💡 Transaction Help", expanded=False):
                st.markdown("""
                **Quick Tips:**
                - Use clear descriptions (e.g., "Grocery shopping at Whole Foods")
                - Choose the most specific category
                - For split transactions, add separate entries
                - Transfers between your accounts don't affect net worth
                """)
        
        elif context == 'view_transactions':
            with st.expander("💡 Transaction Management Help", expanded=False):
                st.markdown("""
                **Features:**
                - **Filter**: Use date range and category filters
                - **Search**: Type in description to find specific transactions
                - **Delete**: Click trash icon to remove transactions
                - **Bulk Actions**: Select multiple transactions for bulk operations
                - **Export**: Download your data as CSV
                """)
        
        elif context == 'budget_planning':
            with st.expander("💡 Budget Planning Help", expanded=False):
                st.markdown("""
                **Budget Best Practices:**
                - Start with essential categories (housing, food, transportation)
                - Review and adjust monthly based on actual spending
                - Use the 50/30/20 rule as a starting point
                - Track progress with budget vs actual reports
                """)
        
        elif context == 'net_worth':
            with st.expander("💡 Net Worth Help", expanded=False):
                st.markdown("""
                **Understanding Your Financial Health:**
                - **Green trends**: You're building wealth
                - **Red trends**: Review spending and increase income
                - **Emergency Fund**: Aim for 3-6 months of expenses
                - **Debt-to-Income**: Keep below 36% for healthy finances
                """)
    
    @classmethod
    def show_onboarding_step(cls, step: str, user_progress: Dict[str, Any]):
        """Show onboarding step if user hasn't completed it"""
        if step not in user_progress.get('completed_steps', []):
            step_info = cls.ONBOARDING_STEPS.get(step)
            if step_info:
                st.info(f"""
                **{step_info['title']}**
                
                {step_info['content']}
                
                👉 {step_info['next_action']}
                """)
                
                if st.button(f"Mark '{step_info['title']}' as completed"):
                    # Update user progress
                    if 'completed_steps' not in user_progress:
                        user_progress['completed_steps'] = []
                    user_progress['completed_steps'].append(step)
                    return user_progress
        
        return user_progress
    
    @classmethod
    def get_feature_announcement(cls) -> str:
        """Get latest feature announcements for display to users.
        
        Returns:
            str: Formatted announcement text with new features
        """
        return """
        🎉 **New Features Available!**
        - **Bulk Actions**: Select and delete multiple transactions
        - **Undo Support**: Restore accidentally deleted transactions
        - **Audit Log**: Track all changes to your financial data
        - **Enhanced Tooltips**: Contextual help throughout the app
        """