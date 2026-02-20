"""
Authentication UI components for the Finance Tracker application.

This module provides reusable UI components for user authentication, including
login and registration forms, form handling, and authentication state management.

NOTE: All Streamlit session keys for Finance Tracker are now prefixed with 'ft_' 
for clarity and isolation (e.g., ft_user, ft_authenticated).
"""

import streamlit as st
from services.auth_service import AuthService

class AuthComponents:
    """
    Authentication UI components for login and registration.
    
    This class provides reusable UI components for rendering login and registration forms,
    handling form submissions, and managing authentication state in the application.
    """
    
    @staticmethod
    def login_form():
        """
        Render the login form with multiple authentication options.
        
        Displays a form with social login buttons, login method selection (email/phone/username),
        input fields for credentials, and a sign-in button.
        
        Returns:
            tuple: (login_button_clicked, identifier, password, login_method)
                - login_button_clicked: Boolean indicating if the login button was clicked
                - identifier: The entered username, email, or phone number
                - password: The entered password
                - login_method: The selected login method ("username", "email", or "phone")
        """
        # Login card with glassmorphism styling (no white box)
        st.markdown(
            '<div class="auth-card auth-form login-form">'
            '<div class="auth-header">'
            '<h2 class="auth-title"><span class="auth-heading-icon" aria-hidden="true">👋</span> Welcome Back</h2>'
            '<p class="auth-subtitle">Sign in to continue to your dashboard</p>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Social login buttons
        from components.ui_components import UIComponents
        UIComponents.social_login_buttons()
        
        # Login method selection
        login_type = st.radio("Login with:", ["Email", "Phone Number", "Username"], horizontal=True, label_visibility="collapsed")
        
        # Input field based on login type
        if login_type == "Username":
            identifier = st.text_input("Username", key="login_username", placeholder="Enter your username", label_visibility="visible")
            login_method = "username"
        elif login_type == "Email":
            identifier = st.text_input("Email", key="login_email", placeholder="Enter your email", label_visibility="visible")
            login_method = "email"
        else:  # Phone Number
            identifier = st.text_input("Phone Number", key="login_phone", placeholder="Enter your phone number", label_visibility="visible")
            login_method = "phone"
        
        # Password field - use native Streamlit with custom CSS to style the eye icon
        password = st.text_input(
            "Password",
            type="password",
            key="login_password_field",
            placeholder="Enter your password",
            autocomplete="current-password"
        )
        
        # Remember me checkbox
        col1, col2 = st.columns([1, 1])
        with col1:
            st.checkbox("Remember me", value=True)
        with col2:
            st.markdown('<div style="text-align: right; margin-top: 8px;"><a href="#" class="text-link">Forgot password?</a></div>', unsafe_allow_html=True)
        
        
        # Login button - full width
        login_button = st.button("Sign In", type="primary", width="stretch", key="login_button")
        st.markdown('<p class="auth-trust-copy">Secure and encrypted · We never share your data</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return login_button, identifier, password, login_method
    
    @staticmethod
    def registration_form():
        """
        Render the registration form with all required fields.
        
        Displays a form with personal information, account credentials, contact information,
        password fields with strength indicator, and terms & conditions checkbox.
        
        Returns:
            tuple: Form data and state
                - register_button_clicked: Boolean indicating if the register button was clicked
                - username: The entered username
                - password: The entered password
                - confirm_password: The entered password confirmation
                - email: The entered email address
                - phone_number: The entered phone number
                - full_name: The entered full name
                - terms_agreed: Boolean indicating if terms were accepted
        """
        st.markdown('<div class="auth-form register-form">', unsafe_allow_html=True)
        
        # Reduce spacing between elements
        st.markdown("""
        <style>
        .register-form h2 { margin-bottom: 6px !important; }
        .register-form p { margin-top: 0px !important; margin-bottom: 10px !important; }
        .register-form .stButton { margin-top: 6px !important; margin-bottom: 6px !important; }
        .register-form hr { margin: 10px 0 !important; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h2>Create Your Account</h2>', unsafe_allow_html=True)
        st.markdown('<p style="margin:0 0 8px 0;">Join thousands of users managing their finances</p>', unsafe_allow_html=True)
        
        # Personal information
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3>Personal Information</h3>', unsafe_allow_html=True)
        full_name = st.text_input("Full Name", key="reg_full_name", placeholder="Enter your full name")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Account credentials
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3>Account Credentials</h3>', unsafe_allow_html=True)
        new_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
        
        # Contact information
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
        with col2:
            phone_number = st.text_input("Phone Number", key="reg_phone", placeholder="Enter your phone number")
        
        # Password fields
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("Password", type="password", key="ft_reg_password", placeholder="Create password")
        with col2:
            confirm_password = st.text_input("Confirm Password", type="password", key="ft_reg_confirm_password", placeholder="Confirm password")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password requirements and strength indicator
        if new_password:
            from components.ui_components import UIComponents
            
            # Check password strength
            if len(new_password) < 8:
                strength = "weak"
            elif len(new_password) >= 12 and any(c.isdigit() for c in new_password) and any(not c.isalnum() for c in new_password):
                strength = "strong"
            else:
                strength = "medium"
                
            UIComponents.password_strength_indicator(strength)
            UIComponents.password_requirements()
        
        # Terms and conditions
        terms_agreed = AuthComponents.terms_modal()
        
        # Register button
        register_button = st.button(
            "Create Account", type="primary",
            width="stretch", key="ft_register_button",
            disabled=not terms_agreed
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return register_button, new_username, new_password, confirm_password, email, phone_number, full_name, terms_agreed
    
    @staticmethod
    def terms_modal():
        """Render Terms & Conditions with visible bullets and sticky accept controls."""
        import streamlit.components.v1 as components
        
        components.html("""
<div class="tc-wrap">
  <div class="tc-box">
    <h3 style="margin:0 0 12px 0;font-size:1.05rem;font-weight:600;color:#111827;">Terms & Conditions</h3>
    <p style="margin:0 0 10px 0;font-size:0.875rem;color:#4b5563;line-height:1.6;">By creating an account and using Finance Tracker, you agree to be bound by these Terms and Conditions.</p>
    
    <h4 style="margin:14px 0 6px 0;font-size:0.9rem;font-weight:600;color:#111827;">User Responsibilities</h4>
    <p style="margin:0 0 6px 0;font-size:0.875rem;color:#4b5563;"><strong>You are responsible for:</strong></p>
    <ul>
      <li>Maintaining confidentiality of your credentials</li>
      <li>Ensuring accuracy of information</li>
      <li>Complying with applicable laws</li>
    </ul>
    
    <h4 style="margin:14px 0 6px 0;font-size:0.9rem;font-weight:600;color:#111827;">Data Privacy</h4>
    <p style="margin:0 0 10px 0;font-size:0.875rem;color:#4b5563;line-height:1.6;">We collect: name, email, phone, and financial data you enter. All data is encrypted and stored locally. We do not sell your information.</p>
    
    <h4 style="margin:14px 0 6px 0;font-size:0.9rem;font-weight:600;color:#111827;">Financial Disclaimer</h4>
    <p style="margin:0 0 10px 0;font-size:0.875rem;color:#4b5563;line-height:1.6;">Finance Tracker does <strong>NOT</strong> provide financial, investment, tax, or legal advice. Consult qualified professionals.</p>
    
    <h4 style="margin:14px 0 6px 0;font-size:0.9rem;font-weight:600;color:#111827;">Limitation of Liability</h4>
    <p style="margin:0 0 10px 0;font-size:0.875rem;color:#4b5563;line-height:1.6;">Provided "as is" without warranties. Not liable for financial decisions, data loss, or damages.</p>
    
    <p style="margin:16px 0 0 0;padding-top:12px;border-top:1px solid #e5e7eb;font-size:0.8rem;color:#9ca3af;text-align:center;">Last updated: January 2026</p>
  </div>

  <div class="tc-footer">
    <div style="font-weight:600;font-size:0.9rem;color:#111827;margin-bottom:4px;">📋 Please review the terms above</div>
    <div style="color:#6b7280;font-size:0.8rem;">Accept below when ready — no need to scroll back up.</div>
  </div>
</div>

<style>
.tc-wrap { border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.tc-box  { height: 240px; overflow-y: auto; padding: 16px 18px; }
.tc-box ul { list-style: disc !important; padding-left: 1.25rem !important; margin: 10px 0 !important; }
.tc-box li { margin: 6px 0 !important; line-height: 1.5 !important; font-size: 0.875rem !important; color: #4b5563 !important; }
.tc-box::-webkit-scrollbar { width: 6px; }
.tc-box::-webkit-scrollbar-track { background: #f3f4f6; }
.tc-box::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.tc-box::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
.tc-footer {
  position: sticky; bottom: 0;
  background: linear-gradient(to bottom, rgba(255,255,255,0.95), #fff);
  border-top: 1px solid #e5e7eb;
  padding: 12px 18px;
  backdrop-filter: blur(4px);
}
</style>
        """, height=360, scrolling=False)
        
        # Checkbox always visible below the iframe
        terms_agreed = st.checkbox(
            "✓ I have read and agree to the Terms & Conditions",
            key="ft_terms"
        )
        
        return terms_agreed
    
    @staticmethod
    def handle_login(identifier, password, login_type):
        """
        Handle login form submission and authentication.
        
        Validates the form inputs, attempts to authenticate the user via the AuthService,
        and updates the session state upon successful login.
        
        Args:
            identifier: Username, email, or phone number
            password: User password
            login_type: Type of login identifier used ("username", "email", or "phone")
            
        Returns:
            bool: True if login was successful, False otherwise
        """
        logger = st.session_state.get('logger')
        
        try:
            # Validate required fields
            if not identifier or not password:
                if login_type == "email":
                    st.error("Please enter your email and password")
                elif login_type == "phone":
                    st.error("Please enter your phone number and password")
                else:
                    st.error("Please enter your username and password")
                return False
            
            # Show loading spinner during authentication
            with st.spinner("Signing in..."):
                # Attempt login via AuthService
                success, message, user_data = AuthService.login(identifier, password, login_type)
            
            if success:
                st.success(f"Welcome back, {user_data['full_name']}!")
                
                # Store user data in session state for persistent authentication
                st.session_state.ft_user = user_data
                st.session_state.ft_authenticated = True
                
                # Log success
                if logger:
                    logger.info(f"User logged in: {user_data['username']}")
                
                return True
            else:
                st.error(message)
                if logger:
                    logger.warning(f"Failed login attempt: {message}")
                return False
        except Exception as e:
            # Handle unexpected errors during login
            if logger:
                logger.error(f"Error during login: {str(e)}")
            st.error("An error occurred during login. Please try again.")
            return False
    
    @staticmethod
    def handle_registration(username, password, confirm_password, email, phone_number, full_name, terms_agreed):
        """Handle registration form submission and user creation."""
        logger = st.session_state.get('logger')
        
        try:
            username = (username or "").strip()
            password = (password or "").strip()
            confirm_password = (confirm_password or "").strip()
            email = (email or "").strip()
            phone_number = (phone_number or "").strip()
            full_name = (full_name or "").strip()
            
            missing = []
            if not full_name: missing.append("Full Name")
            if not username: missing.append("Username")
            if not email: missing.append("Email")
            if not password: missing.append("Password")
            
            if missing:
                st.error("Please fill: " + ", ".join(missing))
                return False
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return False
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters")
                return False
            
            if not terms_agreed:
                st.error("Please agree to the Terms and Conditions")
                return False
            
            with st.spinner("Creating your account..."):
                success, message = AuthService.register_user(
                    username, password, email, phone_number, full_name
                )
            
            if success:
                st.success(message)
                st.info("You can now login with your credentials")
                if logger:
                    logger.info(f"New user registered: {username}")
                return True
            
            st.error(message)
            if logger:
                logger.warning(f"Failed registration attempt: {message}")
            return False
            
        except Exception as e:
            if logger:
                logger.error(f"Error during registration: {str(e)}")
            st.error("An error occurred during registration. Please try again.")
            return False