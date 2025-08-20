"""
User Onboarding Service for guiding new users through the application
"""
import streamlit as st
import logging
from typing import Dict, Any, List
from services.database_service import DatabaseService
from services.tooltip_service import TooltipService

logger = logging.getLogger(__name__)

class OnboardingService:
    """Service for managing user onboarding experience"""
    
    @classmethod
    def get_user_progress(cls, user_id: str) -> Dict[str, Any]:
        """Get user's onboarding progress from database.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict containing progress data with completed steps and current status
        """
        progress = DatabaseService.get_user_preference('onboarding_progress', user_id, {
            'completed_steps': [],
            'current_step': 'welcome',
            'started_at': None,
            'completed_at': None,
            'skip_onboarding': False
        })
        return progress
    
    @classmethod
    def update_user_progress(cls, user_id: str, progress: Dict[str, Any]) -> bool:
        """Update user's onboarding progress"""
        return DatabaseService.save_user_preference('onboarding_progress', progress, user_id)
    
    @classmethod
    def should_show_onboarding(cls, user_id: str) -> bool:
        """Check if onboarding should be shown to user based on progress and activity.
        
        Args:
            user_id: The user identifier
            
        Returns:
            bool: True if onboarding should be displayed
        """
        progress = cls.get_user_progress(user_id)
        
        # Don't show if user has skipped or completed onboarding
        if progress.get('skip_onboarding') or progress.get('completed_at'):
            return False
        
        # Show if user has no transactions and hasn't completed onboarding
        try:
            from services.financial_data_service import TransactionService
            transactions = TransactionService.load_transactions(user_id)
            return len(transactions) < 3  # Show onboarding if user has fewer than 3 transactions
        except Exception as e:
            # If transaction count cannot be determined, default to showing onboarding to avoid missing new user setup
            logger.warning(f"Could not check transaction count for onboarding: {str(e)}")
            return True  # Show onboarding if we can't determine transaction count
    
    @classmethod
    def show_onboarding_flow(cls, user_id: str, current_page: str = None):
        """Show appropriate onboarding step based on current page and progress.
        
        Args:
            user_id: The user identifier
            current_page: Current page name for contextual onboarding
        """
        progress = cls.get_user_progress(user_id)
        
        if not cls.should_show_onboarding(user_id):
            return
        
        # Determine which step to show based on current page
        if current_page == 'add_transaction' and 'first_transaction' not in progress['completed_steps']:
            updated_progress = TooltipService.show_onboarding_step('first_transaction', progress)
            if updated_progress != progress:
                cls.update_user_progress(user_id, updated_progress)
        
        elif current_page == 'budget' and 'budget_setup' not in progress['completed_steps']:
            updated_progress = TooltipService.show_onboarding_step('budget_setup', progress)
            if updated_progress != progress:
                cls.update_user_progress(user_id, updated_progress)
        
        elif current_page == 'net_worth' and 'net_worth_explained' not in progress['completed_steps']:
            updated_progress = TooltipService.show_onboarding_step('net_worth_explained', progress)
            if updated_progress != progress:
                cls.update_user_progress(user_id, updated_progress)
        
        elif 'welcome' not in progress['completed_steps']:
            updated_progress = TooltipService.show_onboarding_step('welcome', progress)
            if updated_progress != progress:
                cls.update_user_progress(user_id, updated_progress)
    
    @classmethod
    def show_onboarding_checklist(cls, user_id: str):
        """Show onboarding progress checklist"""
        progress = cls.get_user_progress(user_id)
        completed_steps = progress.get('completed_steps', [])
        
        st.subheader("🚀 Getting Started Checklist")
        
        # Define checklist items
        checklist_items = [
            ('welcome', '👋 Welcome Tour', 'Learn about the app features'),
            ('first_transaction', '💰 Add First Transaction', 'Record your first income or expense'),
            ('budget_setup', '📊 Set Up Budget', 'Create your monthly spending plan'),
            ('net_worth_explained', '💎 Understand Net Worth', 'Learn how we calculate your financial health')
        ]
        
        for step_key, title, description in checklist_items:
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if step_key in completed_steps:
                    st.success("✅")
                else:
                    st.info("⏳")
            
            with col2:
                if step_key in completed_steps:
                    st.write(f"~~{title}~~")
                    st.caption(f"✅ {description}")
                else:
                    st.write(f"**{title}**")
                    st.caption(description)
        
        # Progress bar
        completion_percentage = len(completed_steps) / len(checklist_items) * 100
        st.progress(completion_percentage / 100)
        st.caption(f"Progress: {completion_percentage:.0f}% complete ({len(completed_steps)}/{len(checklist_items)} steps)")
        
        # Skip onboarding option
        if st.button("Skip Onboarding", help="You can always access help from the sidebar"):
            progress['skip_onboarding'] = True
            cls.update_user_progress(user_id, progress)
            st.rerun()
    
    @classmethod
    def show_quick_start_guide(cls):
        """Show quick start guide for new users"""
        st.info("""
        **🚀 Quick Start Guide**
        
        1. **Add Transactions**: Start by adding your recent income and expenses
        2. **Set Budgets**: Create monthly spending limits for different categories  
        3. **Track Net Worth**: Monitor your overall financial health
        4. **Review Reports**: Use the dashboard to analyze your spending patterns
        
        💡 **Pro Tip**: Use the quick-add buttons for common transactions to save time!
        """)
    
    @classmethod
    def show_feature_highlights(cls, features: List[str]):
        """Show highlights of specific features"""
        feature_descriptions = {
            'bulk_actions': "🔧 **Bulk Actions**: Select multiple transactions to delete or export at once",
            'undo_support': "↩️ **Undo Support**: Accidentally deleted something? Use the undo feature to restore it",
            'audit_log': "📋 **Audit Log**: Track all changes to your financial data for security",
            'smart_tooltips': "💡 **Smart Tooltips**: Hover over any field for contextual help and guidance",
            'performance': "⚡ **Performance**: Optimized queries and caching for faster loading",
            'mobile_friendly': "📱 **Mobile Friendly**: Responsive design works great on all devices"
        }
        
        st.subheader("✨ New Features")
        
        for feature in features:
            if feature in feature_descriptions:
                st.markdown(feature_descriptions[feature])
        
        st.info("💡 **Need Help?** Look for the ℹ️ icons throughout the app for contextual guidance!")
    
    @classmethod
    def check_onboarding_triggers(cls, user_id: str, action: str, context: Dict[str, Any] = None):
        """Check if an action should trigger onboarding steps"""
        progress = cls.get_user_progress(user_id)
        
        # Mark steps as completed based on user actions
        if action == 'transaction_added' and 'first_transaction' not in progress['completed_steps']:
            progress['completed_steps'].append('first_transaction')
            cls.update_user_progress(user_id, progress)
            
            # Show congratulations
            st.success("🎉 Great! You've added your first transaction. Check out the Budget Planning next!")
        
        elif action == 'budget_created' and 'budget_setup' not in progress['completed_steps']:
            progress['completed_steps'].append('budget_setup')
            cls.update_user_progress(user_id, progress)
            
            st.success("🎉 Excellent! Your budget is set up. Now explore your Net Worth dashboard!")
        
        elif action == 'net_worth_viewed' and 'net_worth_explained' not in progress['completed_steps']:
            progress['completed_steps'].append('net_worth_explained')
            cls.update_user_progress(user_id, progress)
            
            # Check if onboarding is complete
            if len(progress['completed_steps']) >= 4:
                from datetime import datetime
                progress['completed_at'] = str(datetime.now())
                cls.update_user_progress(user_id, progress)
                
                st.balloons()
                st.success("🎉 Congratulations! You've completed the onboarding. You're ready to take control of your finances!")
    
    @classmethod
    def get_contextual_tips(cls, page: str, user_progress: Dict[str, Any]) -> List[str]:
        """Get contextual tips based on current page and user progress"""
        tips = []
        
        if page == 'dashboard':
            tips.extend([
                "💡 Use the date filters to analyze specific time periods",
                "📊 Click on chart elements to drill down into details",
                "🔄 Data refreshes automatically when you add new transactions"
            ])
        
        elif page == 'add_transaction':
            tips.extend([
                "⚡ Use quick-add buttons for common transactions",
                "📝 Add detailed descriptions for better tracking",
                "🏷️ Choose specific categories for accurate reporting"
            ])
        
        elif page == 'transactions':
            tips.extend([
                "🔍 Use search and filters to find specific transactions",
                "✅ Select multiple transactions for bulk operations",
                "📤 Export your data anytime as CSV"
            ])
        
        elif page == 'net_worth':
            tips.extend([
                "📈 Track your progress over time with the trend charts",
                "🎯 Aim to increase net worth by 10-20% annually",
                "💰 Emergency fund should cover 3-6 months of expenses"
            ])
        
        return tips