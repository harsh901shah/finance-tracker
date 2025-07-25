"""
User preferences and customization components - SECURE VERSION
"""
import streamlit as st
from services.database_service import DatabaseService
from config.app_config import AppConfig
from utils.logger import AppLogger
from utils.auth_middleware import AuthMiddleware

class UserPreferencesManager:
    """Manages user preferences and customization"""
    
    @staticmethod
    def render_settings_panel():
        """Render the settings and customization panel"""
        # Only show if at least one customization feature is enabled
        if not (AppConfig.FEATURES.get('custom_categories', True) or AppConfig.FEATURES.get('custom_payment_methods', True)):
            return
            
        with st.expander("⚙️ Settings & Customization"):
            col1, col2 = st.columns(2)
            
            with col1:
                if AppConfig.FEATURES.get('custom_categories', True):
                    UserPreferencesManager._render_category_settings()
                else:
                    st.info("📊 Custom categories are disabled")
            
            with col2:
                if AppConfig.FEATURES.get('custom_payment_methods', True):
                    UserPreferencesManager._render_payment_settings()
                else:
                    st.info("📊 Custom payment methods are disabled")
    
    @staticmethod
    def _render_category_settings():
        """Render custom category settings"""
        st.markdown("**Custom Categories**")
        new_category = st.text_input("Add Category", placeholder="e.g., Pet Care")
        if st.button("Add Category", key="add_category"):
            if new_category.strip():
                UserPreferencesManager.add_custom_category(new_category.strip())
                st.success(f"✅ Added category: {new_category}")
                st.rerun()
        
        # Show existing custom categories
        custom_categories = UserPreferencesManager.get_custom_categories()
        if custom_categories:
            st.markdown("**Your Categories:**")
            for cat in custom_categories:
                col_cat, col_del = st.columns([3, 1])
                with col_cat:
                    st.text(cat)
                with col_del:
                    if st.button("🗑️", key=f"del_cat_{cat}"):
                        UserPreferencesManager.remove_custom_category(cat)
                        st.rerun()
    
    @staticmethod
    def _render_payment_settings():
        """Render payment method settings"""
        st.markdown("**Custom Payment Methods**")
        new_payment = st.text_input("Add Payment Method", placeholder="e.g., PayPal")
        if st.button("Add Payment Method", key="add_payment"):
            if new_payment.strip():
                UserPreferencesManager.add_custom_payment_method(new_payment.strip())
                st.success(f"✅ Added payment method: {new_payment}")
                st.rerun()
        
        # Default payment method preference
        st.markdown("**Default Payment Method**")
        all_payment_methods = UserPreferencesManager.get_all_payment_methods()
        default_payment = st.selectbox(
            "Select default",
            all_payment_methods,
            index=0 if "Bank Transfer" in all_payment_methods else 0
        )
        if st.button("Save Default", key="save_default"):
            UserPreferencesManager.save_default_payment_method(default_payment)
            st.success(f"✅ Default payment method: {default_payment}")
    
    # Category management methods
    @staticmethod
    def add_custom_category(category):
        """Add custom category to user preferences"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                st.error("🔒 Please login to manage categories")
                return
                
            categories = UserPreferencesManager.get_custom_categories()
            if category not in categories:
                categories.append(category)
                DatabaseService.save_user_preference('custom_categories', categories, user_id)
        except Exception as e:
            AppLogger.log_error("Error adding custom category", e, show_user=True)
    
    @staticmethod
    def remove_custom_category(category):
        """Remove custom category from user preferences"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                st.error("🔒 Please login to manage categories")
                return
                
            categories = UserPreferencesManager.get_custom_categories()
            if category in categories:
                categories.remove(category)
                DatabaseService.save_user_preference('custom_categories', categories, user_id)
        except Exception as e:
            AppLogger.log_error("Error removing custom category", e, show_user=True)
    
    @staticmethod
    def get_custom_categories():
        """Get user's custom categories"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                return []
            return DatabaseService.get_user_preference('custom_categories', user_id, [])
        except Exception as e:
            AppLogger.log_error("Error getting custom categories", e, show_user=False)
            return []
    
    @staticmethod
    def get_all_categories():
        """Get all categories including custom ones"""
        custom_categories = UserPreferencesManager.get_custom_categories() or []
        return AppConfig.DEFAULT_CATEGORIES + custom_categories
    
    # Payment method management
    @staticmethod
    def add_custom_payment_method(payment_method):
        """Add custom payment method to user preferences"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                st.error("🔒 Please login to manage payment methods")
                return
                
            methods = UserPreferencesManager.get_custom_payment_methods()
            if payment_method not in methods:
                methods.append(payment_method)
                DatabaseService.save_user_preference('custom_payment_methods', methods, user_id)
        except Exception as e:
            AppLogger.log_error("Error adding custom payment method", e, show_user=True)
    
    @staticmethod
    def get_custom_payment_methods():
        """Get user's custom payment methods"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                return []
            return DatabaseService.get_user_preference('custom_payment_methods', user_id, [])
        except Exception as e:
            AppLogger.log_error("Error getting custom payment methods", e, show_user=False)
            return []
    
    @staticmethod
    def get_all_payment_methods():
        """Get all payment methods including custom ones"""
        custom_methods = UserPreferencesManager.get_custom_payment_methods() or []
        return AppConfig.DEFAULT_PAYMENT_METHODS + custom_methods
    
    @staticmethod
    def save_default_payment_method(payment_method):
        """Save user's default payment method"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                st.error("🔒 Please login to save preferences")
                return
            DatabaseService.save_user_preference('default_payment_method', payment_method, user_id)
        except Exception as e:
            AppLogger.log_error("Error saving default payment method", e, show_user=True)
    
    @staticmethod
    def get_default_payment_method():
        """Get user's default payment method"""
        try:
            user_id = AuthMiddleware.get_current_user_id()
            if not user_id:
                return 'Bank Transfer'
            return DatabaseService.get_user_preference('default_payment_method', user_id, 'Bank Transfer')
        except Exception as e:
            AppLogger.log_error("Error getting default payment method", e, show_user=False)
            return 'Bank Transfer'