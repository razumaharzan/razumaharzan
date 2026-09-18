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

# Standardize page formatting entirely to remove container overflow conflicts
st.markdown("""
<style>
    .block-container {
        padding: 2.5rem 4rem !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize User Database inside local system state
if "user_db" not in st.session_state:
    st.session_state.user_db = pd.DataFrame([
        {"email": "razumaharjan@gmail.com", "password": "admin123", "name": "Raju Maharjan", "role": "Admin"}
    ])

# Initialize Robust Local Storage Frameworks with dummy baseline values so columns are never empty
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "date": pd.to_datetime("2026-09-18"), "shop": "System Setup", "items": "Initial Ledger Configuration", "amount": 0.0, "payment_method": "Cash", "main_category": "Groceries", "sub_category": "General"}
    ])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["user", "title", "deadline", "client", "address", "priority", "status"])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "date": datetime.today().date(), "category": "System Initialized", "details": "Health monitor is ready to record data."}
    ])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame([
        {"user": "razumaharjan@gmail.com", "type": "Money Lent (People Owe Me)", "name": "System Ledger", "amount": 0.0, "due_date": datetime.today().date(), "status": "Initialized"}
    ])

# Temporary memory to build an invoice list before clicking the final save button
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_role" not in st.session_state:
    st.session_state.current_role = None
if "current_name" not in st.session_state:
    st.session_state.current_name = None

# ==========================================
# 2. APPLICATION GATEWAY (LOGIN & SIGN UP)
# ==========================================
if st.session_state.current_user is None:
    st.title("💼 Mero App")
    st.subheader("Your Personal Expense, Work & Family Dashboard")
    
    gate_mode = st.radio("Choose Action", ["Log In to My Account", "Register New Family Member (Sign Up)"], horizontal=True)
    st.write("---")
    
    if gate_mode == "Log In to My Account":
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔒 Secure Access Portal")
            login_email = st.text_input("Gmail Address")
            login_pass = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Log In", type="primary", use_container_width=True)
            
            if submit_login:
                db = st.session_state.user_db
                user_match = db[(db["email"] == login_email) & (db["password"] == login_pass)]
                if not user_match.empty:
                    st.session_state.current_user = login_email
                    st.session_state.current_role = user_match.iloc[0]["role"]
                    st.session_state.current_name = user_match.iloc[0]["name"]
                    st.success("Authorized.")
                    st.rerun()
                else:
                    st.error("Invalid email address or password sequence.")
                    
    elif gate_mode == "Register New Family Member (Sign Up)":
        with st.form("signup_form", clear_on_submit=True):
            st.markdown("### 📝 Family Registration Form")
            new_name = st.text_input("Full Name", placeholder="e.g. Sita Maharjan")
            new_email = st.text_input("Gmail Address", placeholder="username@gmail.com")
            new_pass = st.text_input("Create Security Password", type="password")
            submit_signup = st.form_submit_button("Create Account & Register", type="primary", use_container_width=True)
            
            if submit_signup:
                if new_name.strip() == "" or new_email.strip() == "" or new_pass.strip() == "":
                    st.error("All entry fields are mandatory to complete user registration profiles.")
                elif new_email in st.session_state.user_db["email"].values:
                    st.error("This email address is already registered inside Mero App database.")
                else:
                    new_profile = {"email": new_email, "password": new_pass, "name": new_name, "role": "Member"}
                    st.session_state.user_db = pd.concat([st.session_state.user_db, pd.DataFrame([new_profile])], ignore_index=True)
                    st.success(f"Success! Account for {new_name} created. You can now toggle to 'Log In' above.")
    st.stop()

# ==========================================
# 3. SECURE AUTHENTICATED SYSTEM WORKSPACE
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
    st.write(f"Hello {current_name}! Here are your quick operational performance statistics metrics.")
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

# --- MODULE 2: INVOICE-STYLE EXPENSE TRACKER ---
elif active_tab == "💰 Expense Tracker":
    st.title("💰 Personal Expense Tracker")
    st.write("Add multiple items to build your bill list below, then click save at the end.")
    st.write("")
    
    col_input, col_display = st.columns([1.2, 1.2])
    
    with col_input:
        st.subheader("I. Metadata Bill Details")
        e_date = st.date_input("Date Selection", datetime.today())
        e_shop = st.text_input("Shop / Merchant Name", placeholder="e.g. Bhat-Bhateni")
        e_method = st.selectbox("Payment Method", ["QR Payment", "E-Wallet (eSewa/Khalti)", "Cash", "Cheque"])
        
        st.write("---")
        st.subheader("II. Add Item Parameters")
        item_name = st.text_input("Item Name / Description", placeholder="e.g. Bread, Coffee, Petrol")
        item_price = st.number_input("Amount / Price (NPR)", min_value=0.0, step=10.0, value=0.0)
        main_cat = st.selectbox("Main Category", ["Food", "Transport", "Subscriptions", "Health", "Groceries"])
        
        sub_opts = ["General"]
        if main_cat == "Food": sub_opts = ["Tea", "Coffee", "Breakfast", "Lunch", "Dinner"]
        if main_cat == "Transport": sub_opts = ["Petrol", "Gas", "Indrive", "Pathao", "Uber", "Public Bus"]
        if main_cat == "Subscriptions": sub_opts = ["Netflix", "Internet", "Software", "Gym Membership"]
        if main_cat == "Health": sub_opts = ["Medicine", "Hospital Checkup", "Doctor Consultation"]
        if main_cat == "Groceries": sub_opts = ["Kitchen Supplies", "Vegetables", "Meat", "Toiletries"]
        
        e_sub_cat = st.selectbox("Sub-Category", sub_opts)
        st.write("")
        
        if st.button("➕ Add Item to Receipt List", type="secondary", use_container_width=True):
            st.session_state.invoice_items.append({
                "user": current_user, "date": pd.to_datetime(e_date), "shop": e_shop, "items": item_name, 
                "amount": item_price, "payment_method": e_method, "main_category": main_cat, "sub_category": e_sub_cat
            })
            st.toast(f"Added {item_name} to item list!")
            st.rerun()

    with col_display:
        st.subheader("III. Live Receipt Table Matrix")
        df_invoice = pd.DataFrame(st.session_state.invoice_items)
        st.dataframe(df_invoice, use_container_width=True)
        
        if st.button("💾 SAVE INVOICE ENTRY", type="primary", use_container_width=True):
            if len(df_invoice) > 0:
                st.session_state.expenses = pd.concat([st.session_state.expenses, df_invoice], ignore_index=True)
                st.session_state.invoice_items = [] 
                st.success("Invoice committed safely to your database!")
                st.rerun()
                
