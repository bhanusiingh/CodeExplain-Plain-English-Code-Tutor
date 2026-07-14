import streamlit as st
import base64
from pathlib import Path
from services.firebase_service import (
    sign_in_with_email_and_password,
    create_user_with_email_and_password,
    send_password_reset_email
)
from utils.history_manager import sync_cloud_history

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_auth_screen():
    """Renders the fullscreen centered authentication card (Login / Signup / Forgot Password)."""
    
    # Check if we should render login, signup, or reset
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"

    # Background setup
    asset_dir = Path(__file__).parent.parent / "assets"
    bg_img_path = asset_dir / "login.png"
    
    if bg_img_path.exists():
        img_base64 = get_base64_of_bin_file(bg_img_path)
        bg_css = f"""
        <style>
        /* Apply background to the absolute root container */
        [data-testid="stAppViewContainer"], .stApp {{
            background-image: linear-gradient(rgba(13, 17, 23, 0.7), rgba(13, 17, 23, 0.7)), url("data:image/png;base64,{img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)
        
    # Inject Custom CSS for Auth Card
    st.markdown("""
        <style>
        /* Hide the header and sidebar completely on the auth screen */
        [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* Center the main block on the screen */
        [data-testid="stAppViewBlockContainer"], .block-container {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-height: 100vh !important;
            padding: 2rem !important;
            max-width: 480px !important;
            margin: 0 auto !important;
        }

        /* The glassmorphism effect applied directly to a form or container inside the block */
        /* Actually, in Streamlit, we can just style the block container itself as the card! */
        [data-testid="stAppViewBlockContainer"], .block-container {
            background: rgba(13, 17, 23, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            /* Adjust margins to center it vertically like a card, not full height */
            min-height: auto !important;
            margin-top: 10vh !important;
            margin-bottom: 10vh !important;
        }
        
        .auth-logo {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .auth-subtitle {
            text-align: center;
            color: #8b949e;
            font-size: 0.95rem;
            margin-bottom: 2rem;
        }

        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            color: #8b949e;
            font-size: 0.8rem;
            margin: 1.5rem 0;
        }
        
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #30363d;
        }
        
        .divider:not(:empty)::before { margin-right: .5em; }
        .divider:not(:empty)::after { margin-left: .5em; }
        
        /* Disable normal top padding for this screen */
        .stAppHeader { display: none; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="auth-logo">🧑‍🏫 CodeExplain</div>
    """, unsafe_allow_html=True)
    
    mode = st.session_state["auth_mode"]
    
    if mode == "login":
        st.markdown('<div class="auth-subtitle">Welcome Back<br>Sign in to continue learning.</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        col1, col2 = st.columns([1, 1])
        with col2:
            st.markdown('<div style="text-align:right;">', unsafe_allow_html=True)
            if st.button("Forgot Password?", key="forgot_link", help="Reset your password"):
                st.session_state["auth_mode"] = "reset"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        if st.button("Sign In", type="primary", use_container_width=True):
            if email and password:
                with st.spinner("Signing in..."):
                    result = sign_in_with_email_and_password(email, password)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state["user"] = result
                        # Sync history on login
                        sync_cloud_history(result["uid"])
                        st.rerun()
            else:
                st.warning("Please enter email and password.")
                
        st.markdown('<div class="divider">OR</div>', unsafe_allow_html=True)
        
        if st.button("Create Account", use_container_width=True):
            st.session_state["auth_mode"] = "signup"
            st.rerun()
            
    elif mode == "signup":
        st.markdown('<div class="auth-subtitle">Create Account<br>Join CodeExplain today.</div>', unsafe_allow_html=True)
        
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        
        if st.button("Sign Up", type="primary", use_container_width=True):
            if not all([name, email, password, confirm]):
                st.warning("Please fill out all fields.")
            elif password != confirm:
                st.warning("Passwords do not match.")
            else:
                with st.spinner("Creating account..."):
                    result = create_user_with_email_and_password(email, password, name)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("Account created! Logging in...")
                        st.session_state["user"] = result
                        sync_cloud_history(result["uid"])
                        st.rerun()
                        
        st.markdown('<div class="divider">OR</div>', unsafe_allow_html=True)
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.rerun()
            
    elif mode == "reset":
        st.markdown('<div class="auth-subtitle">Reset Password<br>Enter your email to receive a reset link.</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="you@example.com")
        
        if st.button("Send Reset Link", type="primary", use_container_width=True):
            if email:
                with st.spinner("Sending link..."):
                    result = send_password_reset_email(email)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("Reset link sent! Please check your email.")
            else:
                st.warning("Please enter your email address.")
                
        st.markdown('<br>', unsafe_allow_html=True)
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.rerun()

    # We removed the closing </div> because the glassmorphism is now applied to the native Streamlit container.
