import streamlit as st

class UIComponents:
    """UI components for the application"""
    
    @staticmethod
    def hero_section():
        """Render the hero section with features"""
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
        """Render the testimonials section"""
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
        """Render a finance quote section"""
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
        """Render the footer section"""
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
        """Render social login buttons"""
        st.markdown('''
        <div class="social-login">
            <button class="social-btn google-btn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google">
                Sign in with Google
            </button>
            <button class="social-btn apple-btn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" alt="Apple">
                Sign in with Apple
            </button>
        </div>
        <div class="divider">
            <span>or sign in with email</span>
        </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def password_requirements():
        """Render password requirements"""
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
        """Render password strength indicator"""
        if strength == "weak":
            st.markdown('<div class="password-strength weak">Password strength: Weak</div>', unsafe_allow_html=True)
        elif strength == "medium":
            st.markdown('<div class="password-strength medium">Password strength: Medium</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="password-strength strong">Password strength: Strong</div>', unsafe_allow_html=True)