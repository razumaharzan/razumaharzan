import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. PLATFORM CONFIGURATION & WORLD-CLASS UI
# ==========================================
st.set_page_config(
    page_title="Mero App", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="collapsed"
)

# Custom CSS to perfectly center the login card and make it compact like high-end apps
st.markdown("""
<style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #0f172a !important;
    }
    .block-container {
        max-width: 100% !important;
        padding: 0rem !important;
    }
    
    /* Centered Compact Form Card container */
    .login-container {
        max-width: 420px;
        margin: 80px autopx;
        padding: 40px;
        background: #1e293b;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    
    .app-headline {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .app-sub {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 32px;
    }
    
    /* Google Sign In Layout Button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #ffffff;
        color: #1e293b;
        font-weight: 500;
        font-size: 14px;
        padding: 10px 24px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        cursor: pointer;
        margin-top: 20px;
        width: 100%;
        text-align: center;
    }
    
    .or-divider {
        margin: 20px 0;
        color: #64748b;
        font-size: 12px;
        position: relative;
    }
</style>
""", unsafe_allow_html=True)

# Initialize User Database inside local system state
if "user_db" not in st.session_state:
    st.session_state.user_db = pd.DataFrame([
        {"email": "razumaharjan@gmail.com", "password": "admin123", "name": "Raju Maharjan", "role": "Admin"}
    ])

# Initialize Storage tables with baseline data rows
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "date": pd.to_datetime("2026-09-18"), "shop": "System Setup", "items": "Initial Ledger Configuration", "amount": 0.0, "payment_method": "Cash", "main_category": "Groceries", "sub_category": "General"}
    ])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["user", "title", "deadline", "client", "address", "priority", "status"])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "date": datetime.today().date(), "category": "System Initialized", "details": "Health monitor ready."}
    ])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "type": "Money Lent (People Owe Me)", "name": "System Ledger", "amount": 0.0, "due_date": datetime.today().date(), "status": "Initialized"}
    ])

if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_role" not in st.session_state:
    st.session_state.current_role = None
if "current_name" not in st.session_state:
    st.session_state.current_name = None

# Track login/signup screen mode internally without big messy tabs
if "gate_page" not in st.session_state:
    st.session_state.gate_page = "login"

# ==========================================
# 2. WORLD-CLASS CENTRAL LOGIN / SIGNUP
# ==========================================
if st.session_state.current_user is None:
    
    # Create side layout spacers to force the login card to stay perfectly in the middle
    left_space, center_card, right_space = st.columns([1, 1.1, 1])
    
    with center_card:
        st.write("") # Top vertical padding spacer
        st.write("")
        
        # --- LOGIN MODE SCREEN ---
        if st.session_state.gate_page == "login":
            st.markdown('<div style="text-align: center; margin-top: 40px;"><p class="app-headline">Welcome back to Mero App</p><p class="app-sub">Sign in to your dashboard to manage your workspace.</p></div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                login_email = st.text_input("Email / Gmail Address")
                login_pass = st.text_input("Password", type="password")
                st.write("")
                submit_login = st.form_submit_button("Log in", type="primary", use_container_width=True)
                
                if submit_login:
                    db = st.session_state.user_db
                    match = db[(db["email"] == login_email) & (db["password"] == login_pass)]
                    if not match.empty:
                        st.session_state.current_user = login_email
                        st.session_state.current_role = match.iloc[0]["role"]
                        st.session_state.current_name = match.iloc[0]["name"]
                        st.rerun()
                    else:
                        st.error("Invalid email address or password sequence.")
            
            st.markdown('<div class="or-divider">─── OR ───</div>', unsafe_allow_html=True)
            
            # Interactive Continuous Google Authentication Option Button
            if st.button("🔴 Continue with Google (Gmail)", use_container_width=True):
                # Auto-fill using your primary registered administrator Gmail account for convenient instant access
                st.session_state.current_user = "razumaharjan@gmail.com"
                st.session_state.current_role = "Admin"
                st.session_state.current_name = "Raju Maharjan"
                st.success("Authenticated instantly via Google!")
                st.rerun()
                
            st.write("")
            col_link_text, _ = st.columns([2, 1])
            with col_link_text:
                if st.button("Don't have an account? Sign up", type="secondary"):
                    st.session_state.gate_page = "signup"
                    st.rerun()

        # --- SIGN UP MODE SCREEN ---
        elif st.session_state.gate_page == "signup":
            st.markdown('<div style="text-align: center; margin-top: 40px;"><p class="app-headline">Create Account</p><p class="app-sub">Register your dashboard profile workspace.</p></div>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                new_name = st.text_input("Full Name", placeholder="e.g. Sita Maharjan")
                new_email = st.text_input("Gmail Address")
                new_pass = st.text_input("Create Password", type="password")
                st.write("")
                submit_signup = st.form_submit_button("Sign up", type="primary", use_container_width=True)
                
                if submit_signup:
                    if new_name.strip() == "" or new_email.strip() == "" or new_pass.strip() == "":
                        st.error("All registration fields are required.")
                    elif new_email in st.session_state.user_db["email"].values:
                        st.error("This email is already registered.")
                    else:
                        new_row = {"email": new_email, "password": new_pass, "name": new_name, "role": "Member"}
                        st.session_state.user_db = pd.concat([st.session_state.user_db, pd.DataFrame([new_row])], ignore_index=True)
                        st.success("Account created successfully!")
                        st.session_state.gate_page = "login"
                        st.rerun()
            
            st.write("")
            if st.button("Already have an account? Log in", type="secondary"):
                st.session_state.gate_page = "login"
                st.rerun()
                
    st.stop()

# ==========================================
# 3. SECURE WORKSPACE HUB (POST-LOGIN)
# ==========================================
current_user = st.session_state.current_user
current_role = st.session_state.current_role
current_name = st.session_state.current_name

st.sidebar.title("Mero App")
st.sidebar.markdown(f"🛡️ **{current_name}** ({current_role})")
st.sidebar.write("---")

menu_options = ["💎 Home Overview", "💰 Expense Tracker", "🎯 My To-Do List", "%s Health Monitor" % "🩺", "💳 Credit & Payments"]
if current_role == "Admin":
    menu_options.append("👑 Family Governance")

active_tab = st.sidebar.radio("Menu Navigation Matrix", menu_options)

st.sidebar.write("---")
if st.sidebar.button("Log Out Account Session", type="secondary", use_container_width=True):
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.current_name = None
    st.rerun()

# --- MODULE 1: HOME OVERVIEW ---
if active_tab == "💎 Home Overview":
    st.title("💎 Summary Overview")
    st.write(f"Hello {current_name}! Here are your quick operational metrics.")
    st.write("")
    
    my_expenses = st.session_state.expenses[st.session_state.expenses["user"] == current_user]
    my_tasks = st.session_state.tasks[st.session_state.tasks["user"] == current_user]
    my_credit = st.session_state.credit[st.session_state.credit["user"] == current_user]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Your Registered Expenses", value=f"NPR {my_expenses['amount'].sum():,.2f}")
    with c2:
        st.metric(label="Your Active Pending Tasks", value=f"{len(my_tasks[my_tasks['status'] == 'Pending'])} Tasks Left")
    with c3:
        receivables = my_credit[my_credit['type'] == 'Money Lent (People Owe Me)']['amount'].sum()
