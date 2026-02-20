"""
Login page module for the Finance Tracker application.

This module provides the main authentication page with login and registration functionality,
inspirational finance quotes, and a visually appealing landing page experience.

NOTE: All Streamlit session keys for Finance Tracker are now prefixed with 'ft_' 
for clarity and isolation (e.g., ft_user, ft_authenticated).
"""

import streamlit as st
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
        {"quote": "It's not how much money you make, but how much money you keep, how hard it works for you, and how many generations you keep it for.", "author": "Robert Kiyosaki"},
        {"quote": "Risk comes from not knowing what you're doing.", "author": "Warren Buffett"},
        {"quote": "Investing should be more like watching paint dry or watching grass grow. If you want excitement, take $800 and go to Las Vegas.", "author": "Paul Samuelson"},
        {"quote": "The goal of the non-professional should not be to pick winners but to own a cross-section of businesses that in aggregate are bound to do well.", "author": "John Bogle"},
        {"quote": "Wide diversification is only required when investors do not understand what they are doing.", "author": "Warren Buffett"},
        {"quote": "The biggest risk of all is not taking one.", "author": "Mellody Hobson"},
        {"quote": "Know what you own, and know why you own it.", "author": "Peter Lynch"},
        {"quote": "The stock market is a device for transferring money from the impatient to the patient.", "author": "Warren Buffett"},
        {"quote": "Time in the market beats timing the market.", "author": "Ken Fisher"},
        {"quote": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin"},
        {"quote": "The secret to wealth is simple: Find a way to do more for others than anyone else does.", "author": "Tony Robbins"},
        {"quote": "Every once in a while, the market does something so stupid it takes your breath away.", "author": "Jim Cramer"},
        {"quote": "Price is what you pay. Value is what you get.", "author": "Warren Buffett"},
        {"quote": "The most contrarian thing of all is not to oppose the crowd but to think for yourself.", "author": "Peter Thiel"},
        {"quote": "Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it.", "author": "Albert Einstein"}
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
            
            # Select random quote on page load (only once per session)
            if 'selected_quote' not in st.session_state:
                import random
                st.session_state.selected_quote = random.choice(cls.FINANCE_QUOTES)
            
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
            
            # Layout and UX fixes: no mystery white box, no "Press enter to apply" on login inputs
            st.markdown("""
                <style>
                /* Hide Streamlit "Press Enter to apply" hint under ALL text inputs */
                div[data-testid="stTextInput"] div[data-testid="stMarkdownContainer"],
                div[data-testid="stTextInput"] ~ div[data-testid="stMarkdown"],
                div[data-testid="element-container"]:has([data-testid="stTextInput"]) > div > div[data-testid="stMarkdown"],
                div[data-testid="stForm"] div[data-testid="stTextInput"] + div[data-testid="stMarkdown"] {
                    display: none !important;
                    visibility: hidden !important;
                    height: 0 !important;
                    overflow: hidden !important;
                }
                
                /* Tighten Streamlit vertical spacing between blocks */
                div[data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
                div[data-testid="stVerticalBlock"] > div { margin: 0 !important; }
                
                /* Tighten the main columns row spacing */
                div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
                
                /* Reduce extra padding Streamlit adds to the main page container */
                section.main > div { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
                </style>
            """, unsafe_allow_html=True)
            
            # Subtle floating background shapes (fintech feel)
            st.markdown("""
                <div class="login-bg-shapes" aria-hidden="true">
                    <div class="shape shape-1"></div>
                    <div class="shape shape-2"></div>
                    <div class="shape shape-3"></div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<header class="landing-header"><div class="logo-container"><h1 class="logo">Finance<span>Tracker</span></h1></div></header>', unsafe_allow_html=True)
                
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
                        if st.button("Create Account", key="switch_to_register", width="stretch"):
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
                        if st.button("Sign In", key="switch_to_login", width="stretch"):
                            st.session_state.auth_view = "login"
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Handle registration button click
                        if register_button:
                            if AuthComponents.handle_registration(username, password, confirm_password, email, phone_number, full_name, terms_agreed):
                                st.session_state.auth_view = "login"
                                st.rerun()
                
                # Testimonials (rotating) and finance quotes (single random quote per session)
                UIComponents.testimonials_section()
                UIComponents.quote_section(st.session_state.selected_quote['quote'], st.session_state.selected_quote['author'])
                
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
        /* Modern SaaS / fintech login – gradient, glassmorphism, motion */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --primary-color: #6366F1;
            --primary-light: #818CF8;
            --primary-dark: #4F46E5;
            --secondary-color: #10B981;
            --accent-color: #F59E0B;
            --text-color: #1F2937;
            --text-light: #6B7280;
            --background-color: #F8FAFC;
            --card-background: #FFFFFF;
            --border-color: #E5E7EB;
            --error-color: #EF4444;
            --success-color: #10B981;
            --gradient-start: #EEF2FF;
            --gradient-mid: #E0E7FF;
            --gradient-end: #F5F3FF;
            --glass-bg: rgba(255, 255, 255, 0.82);
            --glass-border: rgba(255, 255, 255, 0.6);
            --shadow-soft: 0 4px 24px rgba(99, 102, 241, 0.08);
            --shadow-lift: 0 12px 40px rgba(99, 102, 241, 0.12);
        }
        
        body {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }
        
        .stApp {
            background: linear-gradient(145deg, var(--gradient-start) 0%, var(--gradient-mid) 45%, var(--gradient-end) 100%) !important;
            background-attachment: fixed !important;
        }
        
        /* Floating background shapes */
        .login-bg-shapes {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .login-bg-shapes .shape {
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.35;
        }
        .login-bg-shapes .shape-1 {
            width: 320px;
            height: 320px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.2) 100%);
            top: -80px;
            left: -80px;
            animation: float1 18s ease-in-out infinite;
        }
        .login-bg-shapes .shape-2 {
            width: 280px;
            height: 280px;
            background: linear-gradient(135deg, rgba(129, 140, 248, 0.2) 0%, rgba(99, 102, 241, 0.15) 100%);
            bottom: 15%;
            right: -60px;
            animation: float2 22s ease-in-out infinite;
        }
        .login-bg-shapes .shape-3 {
            width: 200px;
            height: 200px;
            background: rgba(196, 181, 253, 0.2);
            top: 50%;
            left: 30%;
            animation: float3 15s ease-in-out infinite;
        }
        @keyframes float1 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(20px, 25px); }
        }
        @keyframes float2 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(-15px, -20px); }
        }
        @keyframes float3 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(10px, -15px); }
        }
        
        /* Hide Streamlit chrome */
        #MainMenu, header, footer { visibility: hidden; }
        .stDeployButton { display: none; }
        
        .block-container {
            position: relative;
            z-index: 1;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 1200px !important;
        }
        
        /* Header */
        .landing-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            margin-bottom: 0.5rem;
        }
        .logo-container { display: flex; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: var(--primary-color); margin: 0; }
        .logo span { color: var(--text-color); }
        
        /* Hero – tighter, less empty space */
        .hero-content {
            padding: 0 0.5rem 0 0;
            margin-top: 0.5rem;
            max-width: 100%;
        }
        .hero-content h1 {
            font-size: 1.85rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            line-height: 1.25;
            color: var(--text-color);
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 0.9375rem;
            color: var(--text-light);
            margin-bottom: 0.75rem;
            line-height: 1.45;
        }
        
        /* Feature grid – smaller cards, aligned */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.6rem;
            margin-top: 0.75rem;
        }
        .feature-card {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            padding: 0.5rem 0.6rem;
            background: var(--glass-bg);
            backdrop-filter: blur(8px);
            border: 1px solid var(--glass-border);
            border-radius: 0.75rem;
            box-shadow: var(--shadow-soft);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.2s ease;
        }
        .feature-card:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-lift);
            border-color: rgba(99, 102, 241, 0.2);
        }
        .feature-icon {
            font-size: 1.35rem;
            line-height: 1;
            transition: transform 0.25s ease;
        }
        .feature-card:hover .feature-icon {
            transform: scale(1.12);
        }
        .feature-text h3 {
            font-size: 0.8125rem;
            font-weight: 600;
            margin: 0 0 0.2rem 0;
        }
        .feature-text p {
            font-size: 0.7rem;
            color: var(--text-light);
            margin: 0;
        }
        
        /* Auth card – glassmorphism, no harsh white box */
        .auth-card.auth-container {
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 1.25rem;
            box-shadow: var(--shadow-soft), 0 0 0 1px rgba(255,255,255,0.5) inset;
            padding: 1.5rem 1.35rem;
            max-width: 380px;
            margin: 0.5rem 0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .auth-card.auth-container:hover {
            box-shadow: var(--shadow-lift), 0 0 0 1px rgba(255,255,255,0.6) inset;
        }
        /* Same glass treatment for registration form */
        .auth-form.auth-container {
            padding: 1.5rem 1.35rem;
            max-width: 380px;
            margin: 0.5rem 0;
        }
        .auth-container {
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 1.25rem;
            box-shadow: var(--shadow-soft), 0 0 0 1px rgba(255,255,255,0.5) inset;
        }
        
        /* Welcome Back header – stronger, animated */
        .auth-header {
            margin-bottom: 1.25rem;
            animation: authHeaderFade 0.5s ease-out;
        }
        @keyframes authHeaderFade {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .auth-title {
            font-size: 2rem;
            font-weight: 800;
            margin: 0;
            color: var(--text-color);
            letter-spacing: -0.03em;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .auth-heading-icon {
            font-size: 1.5rem;
            opacity: 0.9;
        }
        .auth-subtitle {
            font-size: 0.9375rem;
            color: var(--text-light);
            margin: 0.4rem 0 0 0;
            font-weight: 400;
            letter-spacing: 0.01em;
            line-height: 1.4;
        }
        
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
        .auth-form p { color: var(--text-light); margin: 0.5rem 0 0 0; }
        .auth-form h3 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-color); }
        .form-section { margin-bottom: 1.5rem; }
        
        /* Social login – hover and press */
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
            padding: 0.7rem 1rem;
            border-radius: 0.75rem;
            border: 1px solid var(--border-color);
            background: rgba(255, 255, 255, 0.9);
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }
        .social-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
            background: #fff;
        }
        .social-btn:active {
            transform: translateY(0) scale(0.98);
        }
        .social-btn svg { width: 18px; height: 18px; }
        .google-btn:hover { border-color: rgba(234, 67, 53, 0.3); }
        .apple-btn:hover { border-color: rgba(0, 0, 0, 0.2); }
        
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
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }
        
        .auth-switch p {
            margin-bottom: 0.75rem;
            color: var(--text-light);
        }
        
        .auth-trust-copy {
            font-size: 0.75rem;
            color: var(--text-light);
            margin: 0.5rem 0 0 0;
            text-align: center;
            opacity: 0.85;
        }
        
        /* Testimonials – rotating carousel */
        .testimonials {
            padding: 1.75rem 1rem;
            margin: 0.75rem 0;
            border-radius: 1.25rem;
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            box-shadow: var(--shadow-soft);
        }
        
        .testimonials h2 {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            padding: 0 1rem;
            color: var(--text-color);
        }
        
        .testimonial-carousel {
            position: relative;
            min-height: 200px;
            overflow: hidden;
            padding: 0 1rem;
        }
        
        .testimonial-slide {
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.6s ease, visibility 0.6s ease;
            pointer-events: none;
        }
        
        .testimonial-slide.active {
            opacity: 1;
            visibility: visible;
            pointer-events: auto;
        }
        
        .testimonial-card {
            background: #fff;
            border-radius: 1rem;
            padding: 1.5rem 1.25rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 0 0 1px rgba(0,0,0,0.03);
            position: relative;
            max-width: 420px;
            margin: 0 auto;
            transition: box-shadow 0.3s ease;
        }
        
        .quote-mark {
            position: absolute;
            top: 1rem;
            left: 1rem;
            font-size: 2.5rem;
            color: var(--primary-light);
            opacity: 0.25;
            font-family: serif;
            line-height: 1;
        }
        
        .testimonial-card p {
            margin: 0 0 1.25rem 0;
            font-style: italic;
            color: var(--text-color);
            position: relative;
            z-index: 1;
            font-size: 0.9375rem;
            line-height: 1.5;
        }
        
        .testimonial-author {
            display: flex;
            flex-direction: column;
        }
        
        .testimonial-author strong {
            color: var(--text-color);
            font-size: 0.9375rem;
        }
        
        .testimonial-author span {
            color: var(--text-light);
            font-size: 0.8125rem;
        }
        
        .testimonial-dots {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .testimonial-dots .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--border-color);
            border: none;
            padding: 0;
            cursor: pointer;
            transition: all 0.3s ease;
            opacity: 0.4;
        }
        
        .testimonial-dots .dot:hover {
            opacity: 0.7;
            transform: scale(1.1);
        }
        
        .testimonial-dots .dot.active {
            opacity: 1;
            background: var(--primary-light);
            transform: scale(1.15);
        }
        
        /* Quote section – rotating */
        .quote-section {
            padding: 1.25rem 1rem;
            text-align: center;
            margin-top: 0.5rem;
            border-radius: 1rem;
            background: var(--glass-bg);
            backdrop-filter: blur(8px);
            border: 1px solid var(--glass-border);
        }
        
        .quote-section.quote-rotating {
            position: relative;
            min-height: 100px;
            overflow: hidden;
        }
        
        .quote-rotating-track {
            position: relative;
            min-height: 100px;
        }
        
        .quote-slide {
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.6s ease, visibility 0.6s ease;
            padding: 0 1rem;
        }
        
        .quote-slide.active {
            opacity: 1;
            visibility: visible;
        }
        
        .quote-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .quote-text {
            font-size: 1.05rem;
            font-style: italic;
            color: var(--text-color);
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }
        
        .quote-slide .quote-text {
            margin-bottom: 0.35rem;
        }
        
        .quote-author {
            font-size: 0.875rem;
            color: var(--text-light);
            font-weight: 500;
        }
        
        /* Footer */
        .landing-footer {
            background-color: #1F2937;
            color: white;
            padding: 1.5rem 0 1rem;
            margin-top: 0.75rem;
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
        
        /* Streamlit components – inputs and buttons */
        [data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 0.75rem !important;
            border-color: var(--border-color) !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }
        [data-baseweb="input"]:focus-within {
            border-color: var(--primary-light) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18) !important;
        }
        
        .stButton button {
            border-radius: 0.75rem !important;
            font-weight: 600 !important;
            height: 2.75rem !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease !important;
        }
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35) !important;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        }
        .stButton button[kind="primary"]:active {
            transform: translateY(0) scale(0.98) !important;
        }
        .stButton button[kind="secondary"] {
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
            background: rgba(255, 255, 255, 0.9) !important;
        }
        .stButton button[kind="secondary"]:hover {
            background: #fff !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
            transform: translateY(-1px) !important;
        }
        .stButton button[kind="secondary"]:active {
            transform: translateY(0) scale(0.98) !important;
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
            
            .testimonial-carousel {
                min-height: 220px;
                padding: 0 0.75rem;
            }
            
            .testimonials {
                padding: 1.25rem 0.75rem;
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
            
            .testimonial-carousel {
                min-height: 200px;
            }
        }
        </style>
        """, unsafe_allow_html=True)