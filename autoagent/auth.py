"""
AutoAgent Auth — Login, Register, Session helpers for Streamlit
"""
import streamlit as st
from autoagent.database import (
    authenticate_user, create_user, validate_session,
    create_session, destroy_session, init_db
)

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#F8F9FC;}
#MainMenu,footer,.stDeployButton{display:none!important;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding:2rem 1.5rem;max-width:480px;margin:0 auto;}
.stTextInput input{border-radius:8px;border:1.5px solid #E2E8F0;font-size:0.9rem;}
.stTextInput input:focus{border-color:#6366F1;box-shadow:0 0 0 3px rgba(99,102,241,0.1);}
.stButton>button{border-radius:10px;font-weight:600;width:100%;}
</style>
"""


def get_current_user():
    """Return user dict if logged in, else None."""
    token = st.session_state.get("auth_token")
    if not token:
        return None
    user = validate_session(token)
    if not user:
        st.session_state.pop("auth_token", None)
    return user


def require_auth():
    """Call at top of any protected page. Returns user or stops."""
    init_db()
    user = get_current_user()
    if not user:
        st.warning("🔒 Please log in to access this page.")
        st.stop()
    return user


def logout():
    token = st.session_state.pop("auth_token", None)
    if token:
        destroy_session(token)
    st.rerun()


def show_auth_page():
    """Full login/register page shown when not authenticated."""
    init_db()
    st.markdown(SHARED_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1.5rem;">
        <div style="font-size:2.5rem;margin-bottom:0.5rem;">⚡</div>
        <h1 style="font-size:1.8rem;font-weight:700;color:#1a1a2e;margin:0;">AutoAgent</h1>
        <p style="color:#94A3B8;font-size:0.9rem;margin:0.3rem 0 0;">Multi-tool AI Agent Platform</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user", placeholder="your username")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")

        if st.button("Sign In →", key="login_btn", type="primary"):
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                user = authenticate_user(username, password)
                if user:
                    token = create_session(user["id"])
                    st.session_state["auth_token"] = token
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("""
        <div style="background:#F0FDF4;border-radius:8px;padding:0.75rem;font-size:0.78rem;color:#166534;margin-top:1rem;">
            <b>Demo account:</b> username <code>demo</code> · password <code>demo1234</code>
        </div>
        """, unsafe_allow_html=True)

    with tab_register:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        new_user = st.text_input("Username", key="reg_user", placeholder="choose a username")
        new_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
        new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="min 8 characters")
        new_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="repeat password")

        if st.button("Create Account →", key="reg_btn", type="primary"):
            if not all([new_user, new_email, new_pass, new_pass2]):
                st.error("Please fill in all fields.")
            elif len(new_pass) < 8:
                st.error("Password must be at least 8 characters.")
            elif new_pass != new_pass2:
                st.error("Passwords do not match.")
            elif "@" not in new_email:
                st.error("Please enter a valid email.")
            else:
                ok, msg = create_user(new_user, new_email, new_pass)
                if ok:
                    user = authenticate_user(new_user, new_pass)
                    token = create_session(user["id"])
                    st.session_state["auth_token"] = token
                    st.success("Account created! Welcome to AutoAgent.")
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("""
    <div style="text-align:center;margin-top:2rem;font-size:0.75rem;color:#CBD5E1;">
        Powered by Groq · LLaMA 3.3 70B · Streamlit
    </div>
    """, unsafe_allow_html=True)
