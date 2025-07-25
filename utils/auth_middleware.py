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
        return (st.session_state.get('authenticated', False) and 
                ('user_id' in st.session_state or 'user' in st.session_state))
    
    @staticmethod
    def get_current_user_id():
        """Get current authenticated user ID"""
        if AuthMiddleware.is_authenticated():
            # Check for user_id first, then fallback to user
            if 'user_id' in st.session_state:
                return st.session_state.user_id
            elif 'user' in st.session_state:
                return st.session_state.user
        return None
    
    @staticmethod
    def set_user_session(user_id, username=None):
        """Set user session after successful login"""
        st.session_state.user_id = user_id
        st.session_state.username = username or user_id
    
    @staticmethod
    def clear_user_session():
        """Clear user session on logout"""
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        if 'username' in st.session_state:
            del st.session_state.username