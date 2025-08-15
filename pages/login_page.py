"""
Login page module for the Finance Tracker application.

This module provides the main authentication page with login and registration functionality,
inspirational finance quotes, and a visually appealing landing page experience.
"""

import streamlit as st
import random
from services.auth_service import AuthService
from services.logger_service import LoggerService
from components.ui_components import UIComponents
from components.auth_components import AuthComponents

class LoginPage:
    """
    Login page for the Finance Tracker application.
    
    This class handles the rendering and functionality of the authentication page,
    including login, registration, session management, and page layout.
    """
    
    logger = LoggerService.get_logger('login_page')
    
    # Collection of finance quotes to display randomly
    FINANCE_QUOTES = [
        {"quote": "The stock market is filled with individuals who know the price of everything, but the value of nothing.", "author": "Philip Fisher"},
        {"quote": "The four most dangerous words in investing are: 'This time it's different.'", "author": "Sir John Templeton"},
        {"quote": "In investing, what is comfortable is rarely profitable.", "author": "Robert Arnott"},
        {"quote": "The individual investor should act consistently as an investor and not as a speculator.", "author": "Benjamin Graham"},
        {"quote": "The best investment you can make is in yourself.", "author": "Warren Buffett"},
        {"quote": "It's not how much money you make, but how much money you keep.", "author": "Robert Kiyosaki"},
        {"quote": "Risk comes from not knowing what you're doing.", "author": "Warren Buffett"},
        {"quote": "The most important investment you can make is in yourself.", "author": "Warren Buffett"},
        {"quote": "Investing should be more like watching paint dry or watching grass grow.", "author": "Paul Samuelson"},
        {"quote": "The goal of the non-professional should not be to pick winners but to own a cross-section of businesses.", "author": "John Bogle"}
    ]
    
    @classmethod
    def show(cls):
        """
        Display the login page with authentication forms and landing page content.
        
        Renders the complete login page with header, hero section, authentication forms,
        testimonials, quotes, and footer. Handles authentication state and form submissions.
        
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        try:
            # Store logger in session state for components to use
            st.session_state['logger'] = cls.logger
            
            # Initialize auth database if needed
            AuthService.initialize_auth_database()
            
            # Check if user is already logged in
            if "ft_user" in st.session_state and st.session_state.ft_user:
                # Display welcome message for logged-in users
                st.success(f"Welcome back, {st.session_state.ft_user['full_name']}!")
                
                # Logout button
                if st.button("Logout", type="primary"):
                    cls._handle_logout()
                
                return True
            
            # Apply custom CSS for styling
            cls._apply_custom_css()
            
            # Override Streamlit default container padding for full-width layout
            st.markdown("""
                <style>
                .block-container {
                    padding-top: 0;
                    padding-bottom: 0;
                    max-width: 100%;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Use Streamlit container and columns for responsive layout
            with st.container():
                # Header with logo - compact design
                st.markdown('<header class="landing-header"><div class="logo-container"><h1 class="logo">Finance<span>Tracker</span></h1></div></header>', unsafe_allow_html=True)
                
                # Main content with two columns - no gap between columns
                cols = st.columns([1, 1], gap="small")
                
                # Left column - Hero section with features
                with cols[0]:
                    UIComponents.hero_section()
                
                # Right column - Auth form (login or registration)
                with cols[1]:
                    # Default to login view if not set
                    if "auth_view" not in st.session_state:
                        st.session_state.auth_view = "login"
                    
                    if st.session_state.auth_view == "login":
                        # Show login form
                        login_button, identifier, password, login_method = AuthComponents.login_form()
                        
                        # Link to switch to register view
                        st.markdown('<div class="auth-switch"><p>Don\'t have an account?</p>', unsafe_allow_html=True)
                        if st.button("Create Account", key="switch_to_register", use_container_width=True):
                            st.session_state.auth_view = "register"
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Handle login button click
                        if login_button:
                            if AuthComponents.handle_login(identifier, password, login_method):
                                st.rerun()
                    else:
                        # Show registration form
                        register_button, username, password, confirm_password, email, phone_number, full_name, terms_agreed = AuthComponents.registration_form()
                        
                        # Link to switch to login view
                        st.markdown('<div class="auth-switch"><p>Already have an account?</p>', unsafe_allow_html=True)
                        if st.button("Sign In", key="switch_to_login", use_container_width=True):
                            st.session_state.auth_view = "login"
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Handle registration button click
                        if register_button:
                            if AuthComponents.handle_registration(username, password, confirm_password, email, phone_number, full_name, terms_agreed):
                                st.session_state.auth_view = "login"
                                st.rerun()
                
                # Place testimonials/quote after main content for better visual flow
                UIComponents.testimonials_section()
                
                # Random finance quote
                quote = random.choice(cls.FINANCE_QUOTES)
                UIComponents.quote_section(quote['quote'], quote['author'])
                
                # Footer
                UIComponents.footer()
            
            return False
        except Exception as e:
            # Log and display any unexpected errors
            cls.logger.error(f"Error in login page: {str(e)}")
            st.error(f"An unexpected error occurred. Please try again later.")
            return False
    
    @classmethod
    def _handle_logout(cls):
        """
        Handle logout button click.
        
        Invalidates the user's session token, clears session state,
        and redirects to the login page.
        """
        try:
            # Logout user via AuthService
            if "ft_user" in st.session_state and st.session_state.ft_user and "session_token" in st.session_state.ft_user:
                username = st.session_state.ft_user.get("username", "Unknown")
                AuthService.logout(st.session_state.ft_user["session_token"])
                cls.logger.info(f"User logged out: {username}")
            
            # Clear session state
            st.session_state.ft_user = None
            st.session_state.ft_authenticated = False
            st.rerun()
        except Exception as e:
            cls.logger.error(f"Error during logout: {str(e)}")
            st.error("An error occurred during logout. Please try again.")
    
    @classmethod
    def verify_authentication(cls):
        """
        Verify if user is authenticated via session token.
        
        Checks if the user has a valid session token and updates
        the session state accordingly.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            if "ft_user" in st.session_state and st.session_state.ft_user and "session_token" in st.session_state.ft_user:
                # Verify session token via AuthService
                valid, user_data = AuthService.verify_session(st.session_state.ft_user["session_token"])
                
                if valid:
                    # Update user data in session state
                    st.session_state.ft_user = user_data
                    st.session_state.ft_authenticated = True
                    return True
                else:
                    # Clear invalid session
                    st.session_state.ft_user = None
                    st.session_state.ft_authenticated = False
                    cls.logger.info("Session verification failed")
            
            return False
        except Exception as e:
            cls.logger.error(f"Error verifying authentication: {str(e)}")
            # Clear session on error
            st.session_state.ft_user = None
            st.session_state.ft_authenticated = False
            return False
    
    @staticmethod
    def _apply_custom_css():
        """
        Apply custom CSS for styling the login page.
        
        Adds custom styles for the page layout, components, forms,
        and responsive design.
        """
        st.markdown("""
        <style>
        /* Custom styles for layout optimization and mobile responsiveness */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary-color: #6366F1;
            --primary-light: #818CF8;
            --primary-dark: #4F46E5;
            --secondary-color: #10B981;
            --accent-color: #F59E0B;
            --text-color: #1F2937;
            --text-light: #6B7280;
            --background-color: #F9FAFB;
            --card-background: #FFFFFF;
            --border-color: #E5E7EB;
            --error-color: #EF4444;
            --success-color: #10B981;
        }
        
        /* Reset and base styles */
        body {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 0;
        }
        
        .stApp {
            background-color: var(--background-color);
        }
        
        /* Hide Streamlit elements */
        #MainMenu, header, footer {
            visibility: hidden;
        }
        
        .stDeployButton {
            display: none;
        }
        
        /* Remove default padding */
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 1200px !important;
        }
        
        /* Remove whitespace */
        .st-emotion-cache-1kyxreq {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        .st-emotion-cache-16txtl3 {
            padding: 0 !important;
        }
        
        /* Header */
        .landing-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            margin-bottom: 0;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }
        
        .logo span {
            color: var(--text-color);
        }
        
        /* Hero section */
        .hero-content {
            padding: 0;
        }
        
        .hero-content h1 {
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            line-height: 1.2;
            color: var(--text-color);
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
            color: var(--text-light);
            margin-bottom: 1.25rem;
            line-height: 1.4;
        }
        
        /* Feature grid */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-top: 1.25rem;
        }
        
        .feature-card {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 0.75rem;
            background-color: var(--card-background);
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        
        .feature-icon {
            font-size: 2rem;
            line-height: 1;
        }
        
        .feature-text h3 {
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
        }
        
        .feature-text p {
            font-size: 0.875rem;
            color: var(--text-light);
            margin: 0;
        }
        
        /* Auth container */
        .auth-container {
            background-color: var(--card-background);
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            max-width: 420px;
            margin: 0;
        }
        
        /* Auth form */
        .auth-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .auth-form h2 {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-color);
        }
        
        .auth-form p {
            color: var(--text-light);
            margin: 0.5rem 0 0 0;
        }
        
        .auth-form h3 {
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 1rem 0;
            color: var(--text-color);
        }
        
        /* Form section */
        .form-section {
            margin-bottom: 1.5rem;
        }
        
        /* Social login */
        .social-login {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .social-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border-color);
            background-color: var(--card-background);
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .social-btn svg {
            width: 18px;
            height: 18px;
        }
        
        .google-btn:hover {
            background-color: #f8f9fa;
        }
        
        .apple-btn:hover {
            background-color: #f8f9fa;
        }
        
        /* Divider */
        .divider {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            color: var(--text-light);
            font-size: 0.875rem;
        }
        
        .divider::before,
        .divider::after {
            content: "";
            flex: 1;
            border-bottom: 1px solid var(--border-color);
        }
        
        .divider span {
            padding: 0 1rem;
        }
        
        /* Password strength */
        .password-strength {
            font-size: 0.875rem;
            font-weight: 500;
            padding: 0.5rem 0;
        }
        
        .password-strength.weak {
            color: var(--error-color);
        }
        
        .password-strength.medium {
            color: var(--accent-color);
        }
        
        .password-strength.strong {
            color: var(--success-color);
        }
        
        /* Password requirements */
        .password-requirements {
            background-color: #F3F4F6;
            border-radius: 0.5rem;
            padding: 1rem;
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }
        
        .password-requirements p {
            margin: 0 0 0.5rem 0;
            font-weight: 500;
        }
        
        .password-requirements ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        
        .password-requirements li {
            margin-bottom: 0.25rem;
        }
        
        /* Auth switch */
        .auth-switch {
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
        }
        
        .auth-switch p {
            margin-bottom: 0.75rem;
            color: var(--text-light);
        }
        
        /* Testimonials */
        .testimonials {
            padding: 2rem 0;
            background-color: #F3F4F6;
            margin: 1rem 0;
            border-radius: 1rem;
        }
        
        .testimonials h2 {
            text-align: center;
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        
        .testimonial-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            padding: 0 1.5rem;
        }
        
        .testimonial-card {
            background-color: var(--card-background);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            position: relative;
        }
        
        .quote-mark {
            position: absolute;
            top: 1rem;
            left: 1rem;
            font-size: 3rem;
            color: var(--primary-light);
            opacity: 0.2;
            font-family: serif;
            line-height: 1;
        }
        
        .testimonial-card p {
            margin: 0 0 1.5rem 0;
            font-style: italic;
            color: var(--text-color);
            position: relative;
            z-index: 1;
        }
        
        .testimonial-author {
            display: flex;
            flex-direction: column;
        }
        
        .testimonial-author strong {
            color: var(--text-color);
        }
        
        .testimonial-author span {
            color: var(--text-light);
            font-size: 0.875rem;
        }
        
        /* Quote section */
        .quote-section {
            padding: 1rem 0;
            text-align: center;
            margin-top: 0;
        }
        
        .quote-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .quote-text {
            font-size: 1.5rem;
            font-style: italic;
            color: var(--text-color);
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .quote-author {
            font-size: 1rem;
            color: var(--text-light);
            font-weight: 500;
        }
        
        /* Footer */
        .landing-footer {
            background-color: #1F2937;
            color: white;
            padding: 2rem 0 1rem;
            margin-top: 1rem;
            border-radius: 1rem 1rem 0 0;
        }
        
        .footer-content {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .footer-logo h2 {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
            color: white;
        }
        
        .footer-logo h2 span {
            color: var(--primary-light);
        }
        
        .footer-links {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
        }
        
        .footer-column h3 {
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 1rem 0;
            color: white;
        }
        
        .footer-column ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .footer-column li {
            margin-bottom: 0.5rem;
        }
        
        .footer-column a {
            color: #D1D5DB;
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .footer-column a:hover {
            color: white;
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .footer-bottom p {
            margin: 0;
            color: #9CA3AF;
            font-size: 0.875rem;
        }
        
        /* Text link */
        .text-link {
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .text-link:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }
        
        /* Streamlit components styling */
        /* Input fields */
        [data-baseweb="input"] {
            background-color: #F9FAFB !important;
            border-radius: 0.5rem !important;
        }
        
        [data-baseweb="input"]:focus-within {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            height: 2.75rem !important;
            transition: all 0.2s !important;
        }
        
        .stButton button[kind="primary"] {
            background-color: var(--primary-color) !important;
            border: none !important;
        }
        
        .stButton button[kind="primary"]:hover {
            background-color: var(--primary-dark) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stButton button[kind="secondary"] {
            border-color: var(--border-color) !important;
            color: var(--text-color) !important;
        }
        
        .stButton button[kind="secondary"]:hover {
            background-color: #F3F4F6 !important;
        }
        
        /* Checkbox */
        [data-testid="stCheckbox"] {
            margin-bottom: 0.5rem !important;
        }
        
        /* Radio buttons */
        [data-testid="stRadio"] > div {
            gap: 0.5rem !important;
        }
        
        [data-testid="stRadio"] label {
            background-color: #F3F4F6 !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }
        
        [data-testid="stRadio"] label:hover {
            background-color: #E5E7EB !important;
        }
        
        [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.875rem !important;
        }
        
        /* Fix column gaps */
        .row-widget.stHorizontal {
            gap: 0 !important;
        }
        
        /* Remove empty containers */
        .element-container:empty {
            display: none !important;
        }
        
        /* Responsive styles */
        @media (max-width: 768px) {
            .auth-container {
                margin: 0 auto;
                max-width: 100%;
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
            }
            
            .testimonial-grid {
                grid-template-columns: 1fr;
                padding: 0 1rem;
            }
            
            .testimonials {
                padding: 1.5rem 0;
                margin: 1rem 0;
            }
            
            .footer-content {
                flex-direction: column;
                gap: 1.5rem;
            }
            
            .footer-links {
                flex-direction: column;
                gap: 1.5rem;
            }
        }
        
        @media (min-width: 769px) and (max-width: 1024px) {
            .auth-container {
                padding: 1.25rem;
            }
            
            .testimonial-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)