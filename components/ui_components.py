"""
UI components for the Finance Tracker application.

This module provides reusable UI elements for the application interface,
including hero sections, testimonials, quotes, and other visual components.
"""

import streamlit as st

class UIComponents:
    """
    Reusable UI components for the application interface.
    
    This class provides static methods for rendering common UI elements
    that can be reused across different pages of the application.
    """
    
    @staticmethod
    def hero_section():
        """
        Render the hero section with features.
        
        Displays a headline, subtitle, and a grid of feature cards highlighting
        the main capabilities of the Finance Tracker application.
        """
        st.markdown('''
        <div class="hero-content">
            <h1>Take Control of Your Financial Future</h1>
            <p class="hero-subtitle">Track expenses, monitor investments, and achieve your financial goals with our powerful yet simple finance tracker.</p>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-text">
                        <h3>Dashboard Analytics</h3>
                        <p>Visual insights into your finances</p>
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <div class="feature-text">
                        <h3>Net Worth Tracking</h3>
                        <p>Monitor your financial growth</p>
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <div class="feature-text">
                        <h3>Bank-Level Security</h3>
                        <p>Your data stays private and secure</p>
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <div class="feature-text">
                        <h3>Access Anywhere</h3>
                        <p>Web, mobile, and desktop access</p>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def testimonials_section():
        """
        Render the testimonials section.
        
        Displays a grid of user testimonials with quotes, names, and roles
        to build trust and showcase user experiences with the application.
        """
        testimonials = [
            {"name": "Sarah J.", "role": "Small Business Owner", "text": "Finance Tracker helped me separate personal and business expenses easily. I've saved hours on bookkeeping!"},
            {"name": "Michael T.", "role": "Software Engineer", "text": "The dashboard gives me a clear picture of my finances at a glance. I've finally started saving consistently."},
            {"name": "Priya K.", "role": "Financial Advisor", "text": "I recommend Finance Tracker to all my clients. It's intuitive enough for beginners but powerful for pros."}
        ]
        
        st.markdown(f'''
        <section class="testimonials">
            <h2>What Our Users Say</h2>
            <div class="testimonial-grid">
                <div class="testimonial-card">
                    <div class="quote-mark">"</div>
                    <p>{testimonials[0]["text"]}</p>
                    <div class="testimonial-author">
                        <strong>{testimonials[0]["name"]}</strong>
                        <span>{testimonials[0]["role"]}</span>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="quote-mark">"</div>
                    <p>{testimonials[1]["text"]}</p>
                    <div class="testimonial-author">
                        <strong>{testimonials[1]["name"]}</strong>
                        <span>{testimonials[1]["role"]}</span>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="quote-mark">"</div>
                    <p>{testimonials[2]["text"]}</p>
                    <div class="testimonial-author">
                        <strong>{testimonials[2]["name"]}</strong>
                        <span>{testimonials[2]["role"]}</span>
                    </div>
                </div>
            </div>
        </section>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def quote_section(quote, author):
        """
        Render a finance quote section.
        
        Displays an inspirational finance quote with attribution in a
        visually appealing format.
        
        Args:
            quote: The quote text to display
            author: The author of the quote
        """
        st.markdown(f'''
        <div class="quote-section">
            <div class="quote-container">
                <p class="quote-text">"{quote}"</p>
                <p class="quote-author">— {author}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def footer():
        """
        Render the footer section.
        
        Displays the application footer with logo, navigation links organized
        by category, and copyright information.
        """
        st.markdown('''
        <footer class="landing-footer">
            <div class="footer-content">
                <div class="footer-logo">
                    <h2>Finance<span>Tracker</span></h2>
                </div>
                <div class="footer-links">
                    <div class="footer-column">
                        <h3>Product</h3>
                        <ul>
                            <li><a href="#">Features</a></li>
                            <li><a href="#">Pricing</a></li>
                            <li><a href="#">Security</a></li>
                        </ul>
                    </div>
                    <div class="footer-column">
                        <h3>Company</h3>
                        <ul>
                            <li><a href="#">About Us</a></li>
                            <li><a href="#">Careers</a></li>
                            <li><a href="#">Contact</a></li>
                        </ul>
                    </div>
                    <div class="footer-column">
                        <h3>Resources</h3>
                        <ul>
                            <li><a href="#">Blog</a></li>
                            <li><a href="#">Help Center</a></li>
                            <li><a href="#">Community</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2023 Finance Tracker. All rights reserved.</p>
            </div>
        </footer>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def social_login_buttons():
        """
        Render social login buttons.
        
        Displays buttons for authentication with Google and Apple accounts,
        along with a divider for the email login option.
        """
        st.markdown('''
        <div class="social-login">
            <button class="social-btn google-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Sign in with Google
            </button>
            <button class="social-btn apple-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 384 512">
                    <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/>
                </svg>
                Sign in with Apple
            </button>
        </div>
        <div class="divider">
            <span>or sign in with email</span>
        </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def password_requirements():
        """
        Render password requirements information.
        
        Displays a box with password requirements to guide users
        in creating secure passwords during registration.
        """
        st.markdown('''
        <div class="password-requirements">
            <p>Password must:</p>
            <ul>
                <li class="requirement">Be at least 8 characters long</li>
                <li class="requirement">Include at least one number</li>
                <li class="requirement">Include at least one special character</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def password_strength_indicator(strength):
        """
        Render password strength indicator.
        
        Displays a visual indicator of password strength (weak, medium, or strong)
        with appropriate color coding.
        
        Args:
            strength: Password strength level ("weak", "medium", or "strong")
        """
        if strength == "weak":
            st.markdown('<div class="password-strength weak">Password strength: Weak</div>', unsafe_allow_html=True)
        elif strength == "medium":
            st.markdown('<div class="password-strength medium">Password strength: Medium</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="password-strength strong">Password strength: Strong</div>', unsafe_allow_html=True)