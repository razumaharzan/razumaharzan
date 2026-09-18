import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# PREMIUM CORE CONFIGURATION & CLASSIC STYLING
# ==========================================
st.set_page_config(
    page_title="Mero App — Enterprise Dashboard", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection for sleek UI cards, typography, and borders
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Dashboard Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    .metric-val {
        font-size: 32px;
        font-weight: 700;
        color: #38bdf8;
        margin-top: 8px;
    }
    .metric-lbl {
        font-size: 13px;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Custom Badges for Priorities */
    .badge {
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-critical { background-color: #ef4444; color: white; }
    .badge-high { background-color: #f97316; color: white; }
    .badge-medium { background-color: #eab308; color: black; }
    .badge-low { background-color: #3b82f6; color: white; }
    .badge-done { background-color: #10b981; color: white; }
    
    /* Clean Header Lines */
    .main-title {
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .sub-title {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 32px;
    }
</style>
""", unsafe_allow_html=True)

# Persistent Session Memory
if "users" not in st.session_state:
    st.session_state.users = {
        "razumaharjan@gmail.com": {"password": "admin123", "role": "Admin", "name": "Raju Maharjan"},
        "family1@gmail.com": {"password": "user123", "role": "Member", "name": "Sita Maharjan"}
    }

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "user", "date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"
    ])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=[
        "user", "title", "deadline", "client", "address", "priority", "status"
    ])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame(columns=["user", "date", "activity_type", "details"])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=["user", "type", "person", "amount", "due_date", "status"])

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# ==========================================
# 2. PREMIUM SIGN IN GATEWAY
# ==========================================
if st.session_state.logged_in_user is None:
    st.markdown('<div style="text-align: center; margin-top: 80px;"><p class="main-title">MERO APP</p><p class="sub-title">Enterprise Personal Management Suite</p></div>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-lbl" style="text-align:center;">Secure Gateway Access</p>', unsafe_allow_html=True)
        email = st.text_input("Gmail Address")
        password = st.text_input("Security Access Code", type="password")
        st.write("")
        if st.button("Authenticate Session", type="primary", use_container_width=True):
            if email in st.session_state.users and st.session_state.users[email]["password"] == password:
                st.session_state.logged_in_user = email
                st.session_state.user_role = st.session_state.users[email]["role"]
                st.rerun()
            else:
                st.error("Authentication credentials failed.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    current_user = st.session_state.logged_in_user
    current_role = st.session_state.user_role
    user_display_name = st.session_state.users[current_user]["name"]
    
    # Premium Navigation Sidebar Layout
    st.sidebar.markdown(f'<p class="main-title" style="font-size:24px; padding-left:10px;">Mero App</p>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="padding-left:10px; color:#94a3b8; font-size:14px; margin-bottom:20px;">🛡️ Welcome, <b>{user_display_name}</b></div>', unsafe_allow_html=True)
    
    tabs = ["💎 Executive Hub", "💰 Financial Ledger", "🎯 Operations & Tasks", "🩺 Wellness & Health", "💳 Credit Counterparty"]
    if current_role == "Admin":
        tabs.append("👑 Family Governance")
        
    active_tab = st.sidebar.radio("Application Matrix", tabs)
    
    st.sidebar.write("")
    if st.sidebar.button("Terminate Session", type="secondary", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()

    # ==========================================
    # 3. EXECUTIVE HUB (SUMMARY DASHBOARD)
    # ==========================================
    if "Executive Hub" in active_tab:
        st.markdown(f'<p class="main-title">Executive Overview Dashboard</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-title">Real-time macro statistics for {user_display_name}</p>', unsafe_allow_html=True)
        
        # Calculate dynamic live data summaries
        my_exp = st.session_state.expenses[st.session_state.expenses["user"] == current_user]
        my_tsk = st.session_state.tasks[st.session_state.tasks["user"] == current_user]
        my_crd = st.session_state.credit[st.session_state.credit["user"] == current_user]
        
        total_spent = f"NPR {my_exp['amount'].sum():,.2f}" if not my_exp.empty else "NPR 0.00"
        active_tasks = len(my_tsk[my_tsk["status"] == "Pending"])
        total_credit = f"NPR {my_crd[my_crd['type'] == 'Money Lent (They Owe You)']['amount'].sum():,.2f}" if not my_crd.empty else "NPR 0.00"
        
        # Premium Row Card Grid Layout
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Cumulative Expenses</div><div class="metric-val">{total_spent}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Operations Queue</div><div class="metric-val" style="color:#f43f5e;">{active_tasks} Open Tasks</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Outstanding Receivables</div><div class="metric-val" style="color:#10b981;">{total_credit}</div></div>', unsafe_allow_html=True)
            
        st.subheader("🗓️ Today's Action Guidelines")
        if active_tasks == 0:
            st.info("Your operations schedule is clean for today. No high-priority deadlines tracked.")
        else:
            st.dataframe(my_tsk[my_tsk["status"] == "Pending"][["title", "deadline", "priority"]], use_container_width=True)

    # ==========================================
    # 4. EXPENSE TRACKER
    # ==========================================
    elif "Financial Ledger" in active_tab:
        st.markdown('<p class="main-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Track allocations, process operational costs, and evaluate visual graphs</p>', unsafe_allow_html=True)
        
        col_form, col_chart = st.columns([1, 1.4])
        
        with col_form:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<p class="metric-lbl" style="margin-bottom:15px; color:#38bdf8;">📝 Create Entry Record</p>', unsafe_allow_html=True)
            
            exp_date = st.date_input("Accounting Date", datetime.today())
            exp_shop = st.text_input("Merchant Entity", placeholder="e.g., Bhat-Bhateni, Local Tea Shop")
            exp_items = st.text_area("Itemization Details", placeholder="Separate items cleanly")
            exp_amount = st.number_input("Transaction Volume (NPR)", min_value=0.0, step=50.0)
            exp_method = st.selectbox("Execution Channel", ["QR Payment", "E-Wallet Transfer", "Cash Settlement", "Bank Cheque"])
            
            main_cat = st.selectbox("Primary Category Asset", ["Food & Dining", "Logistics & Transport", "Subscriptions", "Medical/Health", "Groceries"])
            if main_cat == "Food & Dining":
                sub_cat = st.selectbox("Sub-Allocation", ["Tea", "Coffee", "Breakfast", "Lunch", "Dinner"])
            elif main_cat == "Logistics & Transport":
                sub_cat = st.selectbox("Sub-Allocation", ["Petrol", "Gas Cylinder", "Indrive Ride", "Pathao Delivery", "Uber", "Public Bus"])
            elif main_cat == "Subscriptions":
                sub_cat = st.selectbox("Sub-Allocation", ["Netflix", "Internet Access", "Software Tools", "Gym Membership"])
            elif main_cat == "Medical/Health":
                sub_cat = st.selectbox("Sub-Allocation", ["Medicine Purchase", "Hospital Checkup", "Doctor Consultation"])
            else:
