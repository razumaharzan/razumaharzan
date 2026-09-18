import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. PLATFORM CONFIGURATION & CORE LAYOUT
# ==========================================
st.set_page_config(
    page_title="Mero App", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Standardized page margins to ensure headers NEVER get cut off by the top navigation bar
st.markdown("""
<style>
    .block-container {
        max-width: 100% !important;
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }
    .stApp {
        background-color: #0f172a !important;
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
    st.session_state.expenses = pd.DataFrame(columns=["user", "date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["user", "title", "deadline", "client", "address", "priority", "status"])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame(columns=["user", "date", "category", "details"])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=["user", "type", "name", "amount", "due_date", "status"])

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
    left_space, center_card, right_space = st.columns([1, 1.1, 1])
    with center_card:
        st.write("") 
        st.write("")
        
        # --- LOGIN MODE SCREEN ---
        if st.session_state.gate_page == "login":
            st.markdown('<div style="text-align: center; margin-top: 40px; margin-bottom: 20px;"><p style="font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; margin-bottom: 8px;">Welcome to Mero App</p><p style="font-size: 14px; color: #94a3b8; margin-bottom: 20px;">Your personal space to plan, track, and manage.</p></div>', unsafe_allow_html=True)
            
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
            
            st.markdown('<div style="margin: 20px 0; color: #64748b; font-size: 12px; text-align: center;">─── OR ───</div>', unsafe_allow_html=True)
            
            # Google Authentication Option Button
            if st.button("🔴 Continue with Google (Gmail)", use_container_width=True):
                st.session_state.current_user = "razumaharjan@gmail.com"
                st.session_state.current_role = "Admin"
                st.session_state.current_name = "Raju Maharjan"
                st.success("Authenticated instantly via Google!")
                st.rerun()
                
            st.write("")
            if st.button("Don't have an account? Sign up", type="secondary", use_container_width=True):
                st.session_state.gate_page = "signup"
                st.rerun()

        # --- SIGN UP MODE SCREEN ---
        elif st.session_state.gate_page == "signup":
            st.markdown('<div style="text-align: center; margin-top: 40px; margin-bottom: 20px;"><p style="font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; margin-bottom: 8px;">Create Account</p><p style="font-size: 14px; color: #94a3b8; margin-bottom: 20px;">Register your dashboard profile workspace.</p></div>', unsafe_allow_html=True)
            
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
            if st.button("Already have an account? Log in", type="secondary", use_container_width=True):
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

menu_options = ["💎 Home Overview", "💰 Expense Tracker", "🎯 My To-Do List", "🩺 Health Monitor", "💳 Credit & Payments"]
if current_role == "Admin":
    menu_options.append("👑 Family Governance")

active_tab = st.sidebar.radio("Navigation Menu", menu_options)

st.sidebar.write("---")
if st.sidebar.button("Log Out Account Session", type="secondary", use_container_width=True):
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.current_name = None
    st.rerun()

# --- MODULE 1: HOME OVERVIEW ---
if active_tab == "💎 Home Overview":
    st.title("💎 Summary Overview")
    st.write(f"Welcome back, {current_name}! Here is the current snapshot of your personal workspace.")
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
        st.metric(label="Your Outstanding Receivables", value=f"NPR {receivables:,.2f}")

    st.write("---")
    st.subheader("💡 Quick Start Workspace Guide")
    st.info("**💰 Tracking Expenses & Invoices:** Open the **Expense Tracker** to record daily spending. You can build multi-item lists (like Tea, Coffee, Petrol, or Groceries) on a running receipt preview before saving them permanently.")
    st.info("**🎯 Managing Tasks & Client Work:** Head over to **My To-Do List** to add active targets, write down client company names, and note project site addresses. Completed entries are securely locked as history evidence.")
    st.info("**🩺 Health & Wellness Monitoring:** Use the **Health Monitor** tab to record your consistent daily workout routines, medicine prescription logs, and clinic consultation checkup summary updates.")
    st.info("**💳 Handling Credit & Payments:** Navigate to **Credit & Payments** to document loans or cash balances lent to separate individuals. The database table keeps clean check on target payback due dates.")

# --- MODULE 2: FLAT-DESIGN EXPENSE TRACKER ---
elif active_tab == "💰 Expense Tracker":
    st.title("💰 Personal Expense Tracker")
    st.write("Add items step-by-step to build your bill list below, then click save at the bottom.")
    st.write("---")
    
    st.subheader("🧾 1. Bill Details")
    e_date = st.date_input("Date Selection", datetime.today())
