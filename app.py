import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. PREMIUM FULL-WIDESCREEN INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Mero App — Premium Management Suite", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Custom Premium SaaS Full-Width Styles
st.markdown("""
<style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Force elements to stretch completely horizontal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }
    
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    .metric-val {
        font-size: 30px;
        font-weight: 700;
        color: #38bdf8;
        margin-top: 8px;
    }
    .metric-lbl {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .main-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .alert-panel {
        background: #182235;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Storage Frameworks
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["title", "deadline", "client", "address", "priority", "status"])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame(columns=["date", "activity_type", "details"])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=["type", "person", "amount", "due_date", "status"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 2. LOGIN PROCESSOR
# ==========================================
if st.session_state.logged_in == False:
    st.markdown('<div style="text-align: center; margin-top: 80px;"><p class="main-title">MERO APP</p><p style="color:#64748b;">Premium Personal ERP & Finance Suite</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        email = st.text_input("Gmail Address")
        password = st.text_input("Security Password", type="password")
        st.write("")
        if st.button("Authenticate & Log In", type="primary", use_container_width=True):
            if email == "razumaharjan@gmail.com" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid security access credentials.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. SECURE PREMIUM SYSTEM WORKSPACE
# ==========================================
st.sidebar.markdown('<p class="main-title" style="font-size:24px; padding-left:10px;">Mero App</p>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="padding-left:10px; color:#94a3b8; font-size:14px; margin-bottom:20px;">🛡️ Account: <b>Raju Maharjan</b> (Admin)</div>', unsafe_allow_html=True)

# Set index=0 to ensure '💎 Executive Hub' opens automatically at start
active_tab = st.sidebar.radio("Dashboard Matrix", ["💎 Executive Hub", "💰 Financial Ledger", "🎯 Operations & Tasks", "🩺 Wellness & Health", "💳 Credit Counterparty"], index=0)

st.sidebar.write("")
if st.sidebar.button("Log Out / Terminate", type="secondary", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- MODULE 1: EXECUTIVE DASHBOARD ---
if active_tab == "💎 Executive Hub":
    st.markdown('<p class="main-title">Executive Hub</p>', unsafe_allow_html=True)
    st.write("Real-time summary analysis of your active modules.")
    st.write("")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        total_exp_val = f"NPR {st.session_state.expenses['amount'].sum():,.2f}"
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Expenses</div><div class="metric-val">{total_exp_val}</div></div>', unsafe_allow_html=True)
    with c2:
        pending_count = len(st.session_state.tasks[st.session_state.tasks["status"] == "Pending"])
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Pending Tasks</div><div class="metric-val" style="color:#f43f5e;">{pending_count} Tasks</div></div>', unsafe_allow_html=True)
    with c3:
        credit_lent_val = f"NPR {st.session_state.credit[st.session_state.credit['type'] == 'Money Lent (They Owe You)']['amount'].sum():,.2f}"
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Outstanding Receivables</div><div class="metric-val" style="color:#10b981;">{credit_lent_val}</div></div>', unsafe_allow_html=True)

# --- MODULE 2: FINANCIAL TRANSACTION LEDGER ---
if active_tab == "💰 Financial Ledger":
    st.markdown('<p class="main-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
    st.write("")
    
    col_f, col_c = st.columns([1, 1.4])
    with col_f:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        e_date = st.date_input("Accounting Date", datetime.today())
        e_shop = st.text_input("Merchant Entity Name")
        e_items = st.text_area("Itemization Details")
        e_amount = st.number_input("Transaction Volume (NPR)", min_value=0.0, step=50.0)
        e_method = st.selectbox("Execution Channel", ["QR Payment", "E-Wallet Transfer", "Cash Settlement", "Bank Cheque"])
        main_cat = st.selectbox("Primary Category", ["Food & Dining", "Logistics & Transport", "Subscriptions", "Medical/Health", "Groceries"])
        
        sub_opts = ["General Item"]
        if main_cat == "Food & Dining": sub_opts = ["Tea", "Coffee", "Breakfast", "Lunch", "Dinner"]
        if main_cat == "Logistics & Transport": sub_opts = ["Petrol", "Gas Cylinder", "Indrive Ride", "Pathao Delivery", "Uber", "Public Bus"]
        if main_cat == "Subscriptions": sub_opts = ["Netflix", "Internet Access", "Software Tools", "Gym Membership"]
        if main_cat == "Medical/Health": sub_opts = ["Medicine Purchase", "Hospital Checkup", "Doctor Consultation"]
        if main_cat == "Groceries": sub_opts = ["Kitchen Supplies", "Vegetables", "Fresh Meat", "Toiletries"]
        
        e_sub_cat = st.selectbox("Sub-Allocation", sub_opts)
        
        if st.button("Execute Ledger Log", type="primary", use_container_width=True):
            new_row = pd.DataFrame([{"date": pd.to_datetime(e_date), "shop": e_shop, "items": e_items, "amount": e_amount, "payment_method": e_method, "main_category": main_cat, "sub_category": e_sub_cat}])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success("Entry verified.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_c:
        if len(st.session_state.expenses) > 0:
            st.markdown('<p class="metric-lbl">📊 Resource Allocation Matrix</p>', unsafe_allow_html=True)
            c_data = st.session_state.expenses.groupby("main_category")["amount"].sum().reset_index()
            chart = alt.Chart(c_data).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                x=alt.X("main_category:N", title="Operational Segment"),
                y=alt.Y("amount:Q", title="Capital (NPR)"),
                color="main_category:N"
            ).properties(height=340)
            st.altair_chart(chart, use_container_width=True)
            
    if len(st.session_state.expenses) > 0:
        st.subheader("📋 Transaction History Ledger")
        st.dataframe(st.session_state.expenses, use_container_width=True)

# --- MODULE 3: WIDESCREEN WORK SCHEDULER & OPERATIONS ---
if active_tab == "🎯 Operations & Tasks":
    st.markdown('<p class="main-title">Operations Engine & To-Do Queue</p>', unsafe_allow_html=True)
    st.write("")
    
    # 2 Horizontal Columns filling the absolute whole screen width
    col_left_form, col_right_analytics = st.columns([1.1, 1.3])
    
    with col_left_form:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-lbl" style="color:#38bdf8;">💼 Dispatch New Task Objective</p>', unsafe_allow_html=True)
        t_title = st.text_input("Task Objective Name")
        t_deadline = st.date_input("Target Deadline", datetime.today() + timedelta(days=1))
        t_client = st.text_input("Client Corporate Profile")
        t_address = st.text_input("Site Location Address")
        t_priority = st.selectbox("Priority Urgency Tier", ["Critical", "High", "Medium", "Low"])
        
        if st.button("Commit Task to Queue", type="primary", use_container_width=True):
            new_t = pd.DataFrame([{"title": t_title, "deadline": t_deadline, "client": t_client, "address": t_address, "priority": t_priority, "status": "Pending"}])
            st.session_state.tasks = pd.concat([st.session_state.tasks, new_t], ignore_index=True)
