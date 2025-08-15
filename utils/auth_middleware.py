"""
Authentication middleware for user data isolation
"""
import streamlit as st
from functools import wraps

class AuthMiddleware:
    """Authentication and authorization utilities"""
    
    @staticmethod
    def require_auth(func):
        """Decorator to require authentication for page access"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not AuthMiddleware.is_authenticated():
                st.error("🔒 Please login to access this page")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return (st.session_state.get('ft_authenticated', False) and 
                ('ft_user_id' in st.session_state or 'ft_user' in st.session_state))
    
    @staticmethod
    def get_current_user_id():
        """Get current authenticated user ID"""
        if AuthMiddleware.is_authenticated():
            # Check for ft_user_id first, then fallback to ft_user
            if 'ft_user_id' in st.session_state:
                return st.session_state.ft_user_id
            elif 'ft_user' in st.session_state:
                user_data = st.session_state.ft_user
                # If ft_user is a dict, extract user_id
                if isinstance(user_data, dict) and 'user_id' in user_data:
                    return user_data['user_id']
                # Otherwise return the whole object
                return user_data
        return None
    
    @staticmethod
    def set_user_session(user_id, username=None):
        """Set user session after successful login"""
        st.session_state.ft_user_id = user_id
        st.session_state.ft_username = username or user_id
    
    @staticmethod
    def clear_user_session():
        """Clear user session on logout"""
        # Clear all app data except safe UI preferences
        safe_keys = {'theme', 'language', 'ui_preferences'}
        keys_to_remove = [key for key in st.session_state.keys() 
                        if not key.startswith('st.') and key not in safe_keys]
        for key in keys_to_remove:
            del st.session_state[key]