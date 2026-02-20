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
        """Render testimonials grid with scroll-triggered animations (Rocket Money inspired)."""
        import streamlit.components.v1 as components
        
        html_code = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:transparent;overflow-x:hidden;padding:40px 20px}.wrapper{max-width:1100px;margin:0 auto}.title{text-align:center;font-size:2rem;font-weight:800;margin-bottom:2.5rem;color:#1F2937;opacity:0;transform:translateY(20px);transition:all 0.6s ease}.title.visible{opacity:1;transform:translateY(0)}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}@media(max-width:768px){.grid{grid-template-columns:1fr}}.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px;opacity:0;transform:translateY(30px);transition:all 0.6s cubic-bezier(0.4,0,0.2,1);box-shadow:0 1px 3px rgba(0,0,0,0.05)}.card.visible{opacity:1;transform:translateY(0)}.card:hover{border-color:#8b5cf6;box-shadow:0 0 0 2px rgba(139,92,246,0.1),0 4px 12px rgba(0,0,0,0.08)}.stars{color:#fbbf24;font-size:0.9rem;margin-bottom:10px;letter-spacing:1px}.text{color:#374151;font-size:0.95rem;line-height:1.6;margin-bottom:14px}.author{display:flex;align-items:center;gap:10px}.avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#06b6d4);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.85rem}.info{display:flex;flex-direction:column}.name{font-weight:600;font-size:0.88rem;color:#1f2937}.role{font-size:0.78rem;color:#6b7280}</style>
</head><body><div class="wrapper"><h2 class="title" id="title">What Our Users Say</h2><div class="grid"><div class="card" style="transition-delay:0.05s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">Finance Tracker helped me separate personal and business expenses easily. I've saved hours on bookkeeping!</p><div class="author"><div class="avatar">SJ</div><div class="info"><div class="name">Sarah J.</div><div class="role">Small Business Owner</div></div></div></div><div class="card" style="transition-delay:0.15s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">The dashboard gives me a clear picture of my finances at a glance. I've finally started saving consistently.</p><div class="author"><div class="avatar">MT</div><div class="info"><div class="name">Michael T.</div><div class="role">Software Engineer</div></div></div></div><div class="card" style="transition-delay:0.25s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">I recommend Finance Tracker to all my clients. It's intuitive enough for beginners but powerful for pros.</p><div class="author"><div class="avatar">PK</div><div class="info"><div class="name">Priya K.</div><div class="role">Financial Advisor</div></div></div></div><div class="card" style="transition-delay:0.35s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">Tracking my investments and net worth has never been easier. The insights are incredibly valuable.</p><div class="author"><div class="avatar">DL</div><div class="info"><div class="name">David L.</div><div class="role">Investor</div></div></div></div><div class="card" style="transition-delay:0.45s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">The budget planning feature keeps me on track every month. I've reduced unnecessary spending by 30%.</p><div class="author"><div class="avatar">EM</div><div class="info"><div class="name">Emily M.</div><div class="role">Marketing Manager</div></div></div></div><div class="card" style="transition-delay:0.55s"><div class="stars">⭐⭐⭐⭐⭐</div><p class="text">Bank-level security with a beautiful interface. Finally, a finance app I actually enjoy using daily.</p><div class="author"><div class="avatar">RC</div><div class="info"><div class="name">Robert C.</div><div class="role">Tech Consultant</div></div></div></div></div></div>
<script>const observer=new IntersectionObserver((entries)=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible')}})},{threshold:0.1});document.querySelectorAll('.card,.title').forEach(el=>observer.observe(el));</script>
</body></html>'''
        
        components.html(html_code, height=720, scrolling=False)
    
    @staticmethod
    def quote_section(quote, author):
        """Render a single finance quote (used when not rotating)."""
        st.markdown(f'''<style>.qs-wrap{{text-align:center;padding:24px 1rem;position:relative;max-width:700px;margin:0 auto}}.qs-bg{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:8rem;font-family:Georgia,serif;color:rgba(0,0,0,0.03);line-height:1;pointer-events:none}}.qs-text{{font-size:1.15rem;font-style:italic;color:#1F2937;margin:0 0 0.75rem;line-height:1.6;position:relative;z-index:1}}.qs-author{{font-size:0.9rem;color:#6B7280;font-weight:500}}</style><div class="qs-wrap"><div class="qs-bg">"</div><p class="qs-text">"{quote}"</p><p class="qs-author">— {author}</p></div>''', unsafe_allow_html=True)
    
    @staticmethod
    def quote_rotating_section(quotes_list):
        """Render rotating quotes carousel with JavaScript control."""
        if not quotes_list:
            return
        slides_html = ""
        for i, q in enumerate(quotes_list):
            quote = q.get("quote", "")
            author = q.get("author", "")
            active = "active" if i == 0 else ""
            slides_html += f'''<div class="qr-slide {active}"><p class="qr-text">"{quote}"</p><p class="qr-author">— {author}</p></div>'''
        
        st.markdown(f'''<style>.qr-wrap{{text-align:center;padding:24px 1rem;position:relative;max-width:700px;margin:0 auto;min-height:120px}}.qr-bg{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:8rem;font-family:Georgia,serif;color:rgba(0,0,0,0.03);line-height:1;pointer-events:none}}.qr-track{{position:relative;min-height:100px}}.qr-slide{{position:absolute;left:0;right:0;top:0;opacity:0;visibility:hidden;transition:opacity 0.6s ease;padding:0 1rem}}.qr-slide.active{{opacity:1;visibility:visible}}.qr-text{{font-size:1.15rem;font-style:italic;color:#1F2937;margin:0 0 0.75rem;line-height:1.6;position:relative;z-index:1}}.qr-author{{font-size:0.9rem;color:#6B7280;font-weight:500}}</style><div class="qr-wrap"><div class="qr-bg">"</div><div class="qr-track">{slides_html}</div></div><script>(function(){{const slides=document.querySelectorAll('.qr-slide');if(!slides.length)return;let cur=0;function show(n){{slides.forEach(s=>s.classList.remove('active'));cur=(n+slides.length)%slides.length;slides[cur].classList.add('active')}}setInterval(()=>show(cur+1),6000)}})();</script>''', unsafe_allow_html=True)
    
    @staticmethod
    def footer():
        """Render dark fintech-style footer with social icons."""
        st.markdown('''<footer style="background:#0f172a;color:#f1f5f9;padding:48px 24px 24px;margin-top:60px;border-radius:0;"><div style="max-width:1200px;margin:0 auto;"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:32px;margin-bottom:32px;"><div><h2 style="font-size:1.4rem;font-weight:800;margin:0 0 12px;color:#f1f5f9;">Finance<span style="color:#8b5cf6;">Tracker</span></h2><p style="font-size:0.85rem;color:#64748b;line-height:1.6;margin:0;">Take control of your financial future with powerful tracking tools.</p></div><div><h3 style="font-size:0.78rem;font-weight:700;color:#f1f5f9;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Product</h3><ul style="list-style:none;display:flex;flex-direction:column;gap:9px;"><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Dashboard</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Net Worth</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Investments</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Security</a></li></ul></div><div><h3 style="font-size:0.78rem;font-weight:700;color:#f1f5f9;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Company</h3><ul style="list-style:none;display:flex;flex-direction:column;gap:9px;"><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">About Us</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Careers</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Press</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Contact</a></li></ul></div><div><h3 style="font-size:0.78rem;font-weight:700;color:#f1f5f9;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Support</h3><ul style="list-style:none;display:flex;flex-direction:column;gap:9px;"><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Help Center</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Community</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Privacy Policy</a></li><li><a href="#" style="color:#94a3b8;text-decoration:none;font-size:0.86rem;" onmouseover="this.style.color='#f1f5f9'" onmouseout="this.style.color='#94a3b8'">Terms of Service</a></li></ul></div><div><h3 style="font-size:0.78rem;font-weight:700;color:#f1f5f9;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Get the App</h3><div style="display:flex;flex-direction:column;gap:10px;"><a href="#" style="display:flex;align-items:center;gap:10px;background:#1e293b;border:1px solid #334155;border-radius:10px;padding:9px 14px;text-decoration:none;" onmouseover="this.style.borderColor='#8b5cf6'" onmouseout="this.style.borderColor='#334155'"><span style="font-size:1.3rem;color:#f1f5f9;">&#63743;</span><div><div style="font-size:0.62rem;color:#94a3b8;">Download on the</div><div style="font-size:0.84rem;font-weight:700;color:#f1f5f9;">App Store</div></div></a><a href="#" style="display:flex;align-items:center;gap:10px;background:#1e293b;border:1px solid #334155;border-radius:10px;padding:9px 14px;text-decoration:none;" onmouseover="this.style.borderColor='#8b5cf6'" onmouseout="this.style.borderColor='#334155'"><span style="font-size:1.1rem;color:#34a853;">&#9654;</span><div><div style="font-size:0.62rem;color:#94a3b8;">Get it on</div><div style="font-size:0.84rem;font-weight:700;color:#f1f5f9;">Google Play</div></div></a></div></div></div><div style="height:1px;background:#1e293b;margin-bottom:20px;"></div><div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:16px;"><div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;"><p style="font-size:0.8rem;color:#475569;margin:0;">© 2024 Finance Tracker. All rights reserved.</p><div style="display:flex;gap:14px;"><a href="#" style="color:#64748b;transition:color 0.2s;" onmouseover="this.style.color='#8b5cf6'" onmouseout="this.style.color='#64748b'"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a><a href="#" style="color:#64748b;transition:color 0.2s;" onmouseover="this.style.color='#8b5cf6'" onmouseout="this.style.color='#64748b'"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg></a><a href="#" style="color:#64748b;transition:color 0.2s;" onmouseover="this.style.color='#8b5cf6'" onmouseout="this.style.color='#64748b'"><svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a></div></div><p style="font-size:0.78rem;color:#334155;max-width:520px;line-height:1.5;margin:0;">Your data is encrypted and never sold. Finance Tracker is not a bank. See our <a href="#" style="color:#6366f1;text-decoration:none;">Privacy Policy</a> for full details.</p></div></div></footer>''', unsafe_allow_html=True)
    
    @staticmethod
    def social_login_buttons():
        """Render social login buttons (disabled for now)."""
        import streamlit.components.v1 as components
        
        components.html('''
        <div class="social-login">
            <button class="social-btn google-btn" disabled style="opacity:0.5;cursor:not-allowed;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Sign in with Google (Coming Soon)
            </button>
            <button class="social-btn apple-btn" disabled style="opacity:0.5;cursor:not-allowed;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 384 512">
                    <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/>
                </svg>
                Sign in with Apple (Coming Soon)
            </button>
        </div>
        <div class="divider">
            <span>or sign in with email</span>
        </div>
        <style>
        .social-login { display:flex; flex-direction:column; gap:12px; margin-bottom:20px; }
        .social-btn { padding:12px 20px; border:1px solid #e5e7eb; border-radius:10px; background:#fff; cursor:pointer; transition:all 0.2s; font-size:0.95rem; font-weight:500; color:#374151; }
        .social-btn:hover:not(:disabled) { border-color:#6366f1; box-shadow:0 2px 8px rgba(99,102,241,0.15); }
        .divider { text-align:center; margin:20px 0; position:relative; }
        .divider::before { content:''; position:absolute; left:0; right:0; top:50%; height:1px; background:#e5e7eb; }
        .divider span { background:#fff; padding:0 12px; position:relative; font-size:0.85rem; color:#6b7280; }
        </style>
        ''', height=180, scrolling=False)
    
    @staticmethod
    def password_requirements():
        """Render password requirements information."""
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
        """Render password strength indicator."""
        if strength == "weak":
            st.markdown('<div class="password-strength weak">Password strength: Weak</div>', unsafe_allow_html=True)
        elif strength == "medium":
            st.markdown('<div class="password-strength medium">Password strength: Medium</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="password-strength strong">Password strength: Strong</div>', unsafe_allow_html=True)
