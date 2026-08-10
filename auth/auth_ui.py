import streamlit as st
import time
from auth.auth_handler import create_user, authenticate_user

# ============================================================
# CSS INJECTION FOR AUTH SCREENS
# ============================================================
def inject_auth_css():
    st.markdown("""
        <style>
        /* Hide the default Streamlit sidebar and top bar on auth screens */
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        header { display: none; }
        
        .stApp {
            background-color: #F7F8FA !important;
            color: #172033 !important;
        }

        /* Clean SaaS Container */
        .auth-container {
            border-radius: 16px;
            background-color: #FFFFFF;
            border: 1px solid #D9DEE7;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
            padding: 36px;
            margin: 10px auto;
            max-width: 500px;
        }

        .auth-branding {
            text-align: left;
            padding: 20px;
            height: 100%;
        }

        .auth-logo-text {
            font-size: 32px;
            font-weight: 800;
            color: #172033;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
        }

        .auth-subtitle {
            font-size: 16px;
            color: #5B6472;
            margin-bottom: 35px;
        }
        
        .auth-feature {
            display: flex;
            align-items: center;
            margin-bottom: 22px;
        }
        .auth-feature-icon {
            font-size: 22px;
            margin-right: 15px;
            background: #F0F2F5;
            border: 1px solid #E8ECF1;
            border-radius: 10px;
            padding: 8px 10px;
        }
        .auth-feature-text h4 {
            margin: 0;
            font-size: 15px;
            color: #172033;
            font-weight: 600;
        }
        .auth-feature-text p {
            margin: 0;
            font-size: 13px;
            color: #5B6472;
        }

        /* Input styling overrides for Auth */
        .auth-container .stTextInput input {
            background-color: #FFFFFF !important;
            color: #172033 !important;
            border: 1px solid #D9DEE7 !important;
            border-radius: 8px !important;
        }
        .auth-container .stTextInput label,
        .auth-container .stCheckbox label {
            color: #172033 !important;
        }

        /* Google Button */
        .google-btn {
            background-color: #FFFFFF;
            color: #172033;
            border: 1px solid #D9DEE7;
            padding: 10px 20px;
            border-radius: 8px;
            width: 100%;
            text-align: center;
            font-weight: 600;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .google-btn:hover {
            background-color: #F7F8FA;
            border-color: #C5CBD5;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================
# LEFT SIDE: BRANDING
# ============================================================
def render_branding_column():
    st.markdown("""<div class="auth-branding">
    <div style="font-size: 40px; margin-bottom: 10px;">🛒</div>
    <div class="auth-logo-text">AI Commerce<br>Copilot</div>
    <div class="auth-subtitle">Your AI Employee for Online Commerce</div>
    <div class="auth-feature">
        <div class="auth-feature-icon">🤖</div>
        <div class="auth-feature-text">
            <h4>Intelligent Commerce</h4>
            <p>AI-powered product and order assistance</p>
        </div>
    </div>
    <div class="auth-feature">
        <div class="auth-feature-icon">🎙️</div>
        <div class="auth-feature-text">
            <h4>Voice Conversations</h4>
            <p>Talk naturally with your AI assistant</p>
        </div>
    </div>
    <div class="auth-feature">
        <div class="auth-feature-icon">📞</div>
        <div class="auth-feature-text">
            <h4>AI Calling Agent</h4>
            <p>Customers can call and interact with AI</p>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ============================================================
# RIGHT SIDE: AUTH SCREENS
# ============================================================

def handle_google_login():
    st.warning("Google Authentication is not configured. Please check `.env` for OAuth placeholders.")

def render_login():
    st.markdown("### Welcome back 👋")
    st.markdown("Sign in to continue to AI Commerce Copilot")
    st.write("")
    
    email = st.text_input("Email", placeholder="you@email.com")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        show_pwd = st.checkbox("👁️ Show")
    with col1:
        password = st.text_input("Password", type="default" if show_pwd else "password", placeholder="•••••••••••")
    
    col3, col4 = st.columns([1, 1])
    with col3:
        st.checkbox("Remember me")
    with col4:
        if st.button("Forgot password?", use_container_width=True, type="tertiary"):
            st.session_state.auth_view = "forgot_password"
            st.rerun()

    st.write("")
    
    if st.button("Sign In", type="primary", use_container_width=True):
        if not email or not password:
            st.error("Please enter email and password.")
        else:
            success, result = authenticate_user(email, password)
            if success:
                st.session_state.is_authenticated = True
                st.session_state.user_info = {"name": result, "email": email}
                st.session_state.is_first_login = True
                st.rerun()
            else:
                st.error(result)

    st.markdown("<div style='text-align: center; color: #94A3B8; margin: 15px 0;'>───── OR ─────────</div>", unsafe_allow_html=True)
    
    if st.button("G  Continue with Google", use_container_width=True):
        handle_google_login()
        
    st.write("")
    st.markdown("<div style='text-align: center;'>Don't have an account?</div>", unsafe_allow_html=True)
    if st.button("Sign up", use_container_width=True, type="secondary"):
        st.session_state.auth_view = "signup"
        st.rerun()

def render_signup():
    st.markdown("### Create your account")
    st.write("")
    
    name = st.text_input("Full Name", placeholder="Enter your name")
    email = st.text_input("Email", placeholder="Enter your email")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        show_pwd = st.checkbox("👁️ Show")
    with col1:
        password = st.text_input("Password", type="default" if show_pwd else "password", placeholder="Create password")
        confirm_password = st.text_input("Confirm Password", type="default" if show_pwd else "password", placeholder="Confirm password")
    
    st.write("")
    
    if st.button("Create Account", type="primary", use_container_width=True):
        if not name or not email or not password:
            st.error("Please fill all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, msg = create_user(name, email, password)
            if success:
                st.success("Account created successfully! Redirecting...")
                time.sleep(1.5)
                # Auto login after signup
                st.session_state.is_authenticated = True
                st.session_state.user_info = {"name": name, "email": email}
                st.session_state.is_first_login = True
                st.rerun()
            else:
                st.error(msg)
                
    st.markdown("<div style='text-align: center; color: #94A3B8; margin: 15px 0;'>───── OR ─────────</div>", unsafe_allow_html=True)
    if st.button("G  Continue with Google", use_container_width=True, key="google_signup"):
        handle_google_login()
        
    st.write("")
    if st.button("← Back to Login", use_container_width=True, type="tertiary"):
        st.session_state.auth_view = "login"
        st.rerun()

def render_forgot_password():
    st.markdown("### Reset your password")
    st.markdown("Enter your email address and we'll help you reset your password.")
    st.write("")
    
    email = st.text_input("Email", placeholder="your@email.com")
    
    if st.button("Send Reset Link", type="primary", use_container_width=True):
        if not email:
            st.error("Please enter your email.")
        else:
            # Mock email sending
            st.success(f"If an account exists for {email}, a reset link has been sent.")
            
    st.write("")
    if st.button("← Back to Login", use_container_width=True, type="tertiary"):
        st.session_state.auth_view = "login"
        st.rerun()

# ============================================================
# MAIN AUTH ROUTER
# ============================================================
def render_auth_screens():
    inject_auth_css()
    
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
        
    # Create the split screen layout
    # Center vertically using empty containers
    st.write("")
    st.write("")
    
    col_left, col_mid, col_right = st.columns([1, 0.1, 1])
    
    with col_left:
        render_branding_column()
        
    with col_right:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        if st.session_state.auth_view == "login":
            render_login()
        elif st.session_state.auth_view == "signup":
            render_signup()
        elif st.session_state.auth_view == "forgot_password":
            render_forgot_password()
        st.markdown('</div>', unsafe_allow_html=True)
