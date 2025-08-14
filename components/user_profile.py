"""
User profile and customization components
"""
import streamlit as st
from utils.auth_middleware import AuthMiddleware
from services.database_service import DatabaseService
from utils.logger import AppLogger

class UserProfile:
    """
    Manages user profile customization and personalization features.
    
    This class provides functionality for:
    - User profile information management
    - Theme and appearance customization
    - Personal preferences and settings
    - Profile picture and display options
    
    Future enhancements planned:
    - Custom dashboard layouts
    - Personalized financial goals
    - Notification preferences
    - Data export preferences
    """
    
    @staticmethod
    def show_profile_section():
        """
        Display user profile customization section in sidebar or settings.
        
        Provides options for:
        - Display name customization
        - Theme preferences
        - Dashboard layout preferences
        - Notification settings
        
        This creates a more personalized experience for each user.
        """
        if not AuthMiddleware.is_authenticated():
            return
            
        user_id = AuthMiddleware.get_current_user_id()
        if not user_id:
            return
            
        with st.expander("👤 Profile Settings"):
            # Display name customization
            current_name = st.session_state.get('user', {}).get('full_name', 'User')
            display_name = st.text_input(
                "Display Name", 
                value=current_name,
                help="This name appears in the sidebar welcome message"
            )
            
            # Theme preferences (future feature)
            theme_preference = st.selectbox(
                "Theme Preference",
                ["Auto", "Light", "Dark", "High Contrast"],
                help="Theme customization coming in future update"
            )
            
            # Dashboard layout (future feature)
            layout_preference = st.selectbox(
                "Dashboard Layout",
                ["Standard", "Compact", "Detailed"],
                help="Custom dashboard layouts coming soon"
            )
            
            # Save preferences
            if st.button("Save Profile Settings", type="primary"):
                try:
                    profile_data = {
                        'display_name': display_name,
                        'theme_preference': theme_preference,
                        'layout_preference': layout_preference
                    }
                    
                    DatabaseService.save_user_preference('user_profile', profile_data, str(user_id))
                    
                    # Update session state
                    if 'user' in st.session_state and st.session_state.user:
                        st.session_state.user['full_name'] = display_name
                    
                    st.success("✅ Profile settings saved!")
                    st.rerun()
                    
                except Exception as e:
                    AppLogger.log_error("Error saving profile settings", e, show_user=True)
    
    @staticmethod
    def get_user_display_name():
        """
        Get the user's preferred display name.
        
        Returns:
            str: User's display name or fallback to session username
            
        This method provides a consistent way to get the user's
        display name throughout the application.
        """
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                return "User"
                
            profile_data = DatabaseService.get_user_preference('user_profile', str(user_id), {})
            display_name = profile_data.get('display_name')
            
            if display_name:
                return display_name
                
            # Fallback to session data
            if 'user' in st.session_state and st.session_state.user:
                return st.session_state.user.get('full_name', 'User')
                
            return "User"
            
        except Exception as e:
            AppLogger.log_error("Error getting user display name", e, show_user=False)
            return "User"
    
    @staticmethod
    def get_user_preferences():
        """
        Get all user preferences for customization.
        
        Returns:
            dict: User preferences including theme, layout, etc.
            
        This method centralizes access to user customization preferences
        and provides defaults for new users.
        """
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                return UserProfile._get_default_preferences()
                
            preferences = DatabaseService.get_user_preference('user_profile', str(user_id), {})
            
            # Merge with defaults for any missing keys
            defaults = UserProfile._get_default_preferences()
            return {**defaults, **preferences}
            
        except Exception as e:
            AppLogger.log_error("Error getting user preferences", e, show_user=False)
            return UserProfile._get_default_preferences()
    
    @staticmethod
    def _get_default_preferences():
        """
        Get default user preferences for new users.
        
        Returns:
            dict: Default preference values
            
        These defaults provide a good starting experience while
        allowing users to customize as needed.
        """
        return {
            'theme_preference': 'Auto',
            'layout_preference': 'Standard',
            'display_name': 'User',
            'show_onboarding': True,
            'show_tooltips': True
        }