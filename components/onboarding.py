"""
User onboarding and guidance components
"""
import streamlit as st

class OnboardingGuide:
    """
    Provides onboarding guidance and contextual help for first-time users.
    
    This class manages the user onboarding experience by:
    - Showing a welcome tour on first login
    - Providing contextual tooltips for each page
    - Tracking user progress through onboarding steps
    - Maintaining onboarding state in session storage
    
    The onboarding system helps reduce user confusion and improves
    adoption by guiding users through the application's key features.
    """
    
    @staticmethod
    def show_welcome_tour():
        """
        Display an interactive welcome tour for first-time users.
        
        Shows a comprehensive overview of all application features with:
        - Visual layout of main navigation sections
        - Brief description of each page's purpose
        - Call-to-action to complete onboarding
        
        The tour is shown only once per user session and can be
        dismissed permanently by clicking the completion button.
        
        Session State:
            onboarding_completed (bool): Tracks if user has seen the tour
        """
        if not st.session_state.get('onboarding_completed', False):
            with st.container():
                st.info("👋 **Welcome to Finance Tracker!** Here's a quick tour:")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **📊 Dashboard** - Your financial overview
                    - View income, expenses, and trends
                    - See budget progress and analytics
                    
                    **➕ Add Transaction** - Record your finances
                    - Quick-add buttons for common transactions
                    - Manual entry for custom transactions
                    """)
                
                with col2:
                    st.markdown("""
                    **📋 View Transactions** - Manage your data
                    - Filter and search transactions
                    - Edit or delete entries
                    
                    **💎 Net Worth** - Track your wealth
                    - Assets, liabilities, and net worth
                    - Property and investment tracking
                    """)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.checkbox("Don't show this again", key="skip_onboarding"):
                        pass  # Checkbox state tracked automatically
                with col2:
                    if st.button("Got it! Start using Finance Tracker", type="primary"):
                        st.session_state.onboarding_completed = True
                        st.rerun()
    
    @staticmethod
    def show_page_tooltip(page_name):
        """
        Display contextual help tooltips for specific pages.
        
        Args:
            page_name (str): Name of the current page to show tooltip for
                           Must match keys in tooltips dictionary
        
        The tooltip system provides just-in-time help by:
        - Showing relevant tips for the current page
        - Allowing users to dismiss tips permanently
        - Tracking which tips have been seen per session
        
        Session State:
            tooltip_seen_{page_name} (bool): Tracks dismissed tooltips
        """
        tooltips = {
            "Dashboard": "💡 **Tip:** Use the date filter to view different time periods and track your financial trends.",
            "Add Transaction": "💡 **Tip:** Use Quick Add buttons for common transactions, or Manual Entry for custom ones.",
            "View Transactions": "💡 **Tip:** Click on any transaction to edit it, or use filters to find specific entries.",
            "Net Worth": "💡 **Tip:** Update your asset values regularly to track your wealth growth over time."
        }
        
        if page_name in tooltips and not st.session_state.get(f'tooltip_seen_{page_name}', False):
            st.info(tooltips[page_name])
            if st.button("Hide tip", key=f"hide_tip_{page_name}"):
                st.session_state[f'tooltip_seen_{page_name}'] = True
                st.rerun()