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
        st.markdown('<div class="auth-form login-form auth-container">', unsafe_allow_html=True)
        st.markdown('<h2>Welcome Back</h2>', unsafe_allow_html=True)
        st.markdown('<p>Sign in to continue to your dashboard</p>', unsafe_allow_html=True)
        
        # Social login buttons
        from components.ui_components import UIComponents
        UIComponents.social_login_buttons()
        
        # Login method selection
        login_type = st.radio("Login with:", ["Email", "Phone Number", "Username"], horizontal=True, label_visibility="collapsed")
        
        # Input field based on login type
        if login_type == "Username":
            identifier = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_method = "username"
        elif login_type == "Email":
            identifier = st.text_input("Email", key="login_email", placeholder="Enter your email")
            login_method = "email"
        else:  # Phone Number
            identifier = st.text_input("Phone Number", key="login_phone", placeholder="Enter your phone number")
            login_method = "phone"
            
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        # Remember me checkbox
        col1, col2 = st.columns([1, 1])
        with col1:
            st.checkbox("Remember me", value=True)
        with col2:
            st.markdown('<div style="text-align: right; margin-top: 8px;"><a href="#" class="text-link">Forgot password?</a></div>', unsafe_allow_html=True)
        
        
        # Login button - full width
        login_button = st.button("Sign In", type="primary", use_container_width=True, key="login_button")
        
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
        st.markdown('<div class="auth-form register-form auth-container">', unsafe_allow_html=True)
        st.markdown('<h2>Create Your Account</h2>', unsafe_allow_html=True)
        st.markdown('<p>Join thousands of users managing their finances</p>', unsafe_allow_html=True)
        
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
            new_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create password")
        with col2:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
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
        terms_agreed = st.checkbox("I agree to the Terms and Conditions and Privacy Policy", key="terms")
        
        # Register button - full width
        register_button = st.button("Create Account", type="primary", use_container_width=True, key="register_button")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return register_button, new_username, new_password, confirm_password, email, phone_number, full_name, terms_agreed
    
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
        """
        Handle registration form submission and user creation.
        
        Validates all form inputs, checks password requirements, ensures terms are accepted,
        and creates a new user account via the AuthService.
        
        Args:
            username: Chosen username
            password: Chosen password
            confirm_password: Password confirmation
            email: User's email address
            phone_number: User's phone number
            full_name: User's full name
            terms_agreed: Whether user accepted terms and conditions
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        logger = st.session_state.get('logger')
        
        try:
            # Validate all required fields
            if not username or not password or not email or not phone_number or not full_name or \
               not username.strip() or not password.strip() or not email.strip() or not phone_number.strip() or not full_name.strip():
                st.error("All fields are required")
                return False
            elif password != confirm_password:
                st.error("Passwords do not match")
                return False
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
                return False
            elif not terms_agreed:
                st.error("Please agree to the Terms and Conditions")
                return False
            
            # Show loading spinner during registration
            with st.spinner("Creating your account..."):
                # Attempt registration via AuthService
                success, message = AuthService.register_user(
                    username, password, email, phone_number, full_name
                )
            
            if success:
                st.success(message)
                st.info("You can now login with your credentials")
                if logger:
                    logger.info(f"New user registered: {username}")
                return True
            else:
                st.error(message)
                if logger:
                    logger.warning(f"Failed registration attempt: {message}")
                return False
        except Exception as e:
            # Handle unexpected errors during registration
            if logger:
                logger.error(f"Error during registration: {str(e)}")
            st.error("An error occurred during registration. Please try again.")
            return False