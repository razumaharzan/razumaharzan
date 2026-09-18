import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. CORE SYSTEM CONFIGURATION & STYLE
# ==========================================
st.set_page_config(
    page_title="Mero App — Premium Management Suite", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Custom Premium SaaS Styles
st.markdown("""
<style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
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
</style>
""", unsafe_allow_html=True)

# Initialize Data Storage Tables
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
# 2. APP GATEWAY AUTHENTICATION
# ==========================================
if not st.session_state.logged_in:
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

# ==========================================
# 3. SECURE AUTHENTICATED SYSTEM LAYOUT
# ==========================================
else:
    st.sidebar.markdown('<p class="main-title" style="font-size:24px; padding-left:10px;">Mero App</p>', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="padding-left:10px; color:#94a3b8; font-size:14px; margin-bottom:20px;">🛡️ Account: <b>Raju Maharjan</b> (Admin)</div>', unsafe_allow_html=True)
    
    active_tab = st.sidebar.radio("Dashboard Matrix", ["💎 Executive Hub", "💰 Financial Ledger", "🎯 Operations & Tasks", "🩺 Wellness & Health", "💳 Credit Counterparty"])
    
    st.sidebar.write("")
    if st.sidebar.button("Log Out / Terminate", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- TAB 1: EXECUTIVE HUB ---
    if active_tab == "💎 Executive Hub":
        st.markdown('<p class="main-title">Executive Hub</p>', unsafe_allow_html=True)
        st.write("Real-time summary analysis of your system modules.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            val = f"NPR {st.session_state.expenses['amount'].sum():,.2f}"
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Expenses</div><div class="metric-val">{val}</div></div>', unsafe_allow_html=True)
        with c2:
            val = len(st.session_state.tasks[st.session_state.tasks["status"] == "Pending"])
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Pending Tasks</div><div class="metric-val" style="color:#f43f5e;">{val} Tasks</div></div>', unsafe_allow_html=True)
        with c3:
            val = f"NPR {st.session_state.credit[st.session_state.credit['type'] == 'Money Lent (They Owe You)']['amount'].sum():,.2f}"
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Outstanding Receivables</div><div class="metric-val" style="color:#10b981;">{val}</div></div>', unsafe_allow_html=True)

    # --- TAB 2: FINANCIAL LEDGER ---
    elif active_tab == "💰 Financial Ledger":
        st.markdown('<p class="main-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
        
        col_f, col_c = st.columns([1, 1.4])
        with col_f:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            e_date = st.date_input("Accounting Date", datetime.today())
            e_shop = st.text_input("Merchant Entity Name")
            e_items = st.text_area("Itemization Details")
            e_amount = st.number_input("Transaction Volume (NPR)", min_value=0.0, step=50.0)
            e_method = st.selectbox("Execution Channel", ["QR Payment", "E-Wallet Transfer", "Cash Settlement", "Bank Cheque"])
            
            main_cat = st.selectbox("Primary Category", ["Food & Dining", "Logistics & Transport", "Subscriptions", "Medical/Health", "Groceries"])
            
            # Simplified static selections to avoid nested branches
            sub_cat = "General"
            if main_cat == "Food & Dining":
                sub_cat = st.selectbox("Sub-Allocation", ["Tea", "Coffee", "Breakfast", "Lunch", "Dinner"])
            elif main_cat == "Logistics & Transport":
                sub_cat = st.selectbox("Sub-Allocation", ["Petrol", "Gas Cylinder", "Indrive Ride", "Pathao Delivery", "Uber", "Public Bus"])
            elif main_cat == "Subscriptions":
                sub_cat = st.selectbox("Sub-Allocation", ["Netflix", "Internet Access", "Software Tools", "Gym Membership"])
            elif main_cat == "Medical/Health":
                sub_cat = st.selectbox("Sub-Allocation", ["Medicine Purchase", "Hospital Checkup", "Doctor Consultation"])
            elif main_cat == "Groceries":
                sub_cat = st.selectbox("Sub-Allocation", ["Kitchen Supplies", "Vegetables", "Fresh Meat", "Toiletries"])
                
            if st.button("Execute Ledger Log", type="primary", use_container_width=True):
                new_row = pd.DataFrame([{"date": pd.to_datetime(e_date), "shop": e_shop, "items": e_items, "amount": e_amount, "payment_method": e_method, "main_category": main_cat, "sub_category": sub_cat}])
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
                st.success("Entry verified.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_c:
            if not st.session_state.expenses.empty:
                st.markdown('<p class="metric-lbl">📊 Resource Allocation Matrix</p>', unsafe_allow_html=True)
                c_data = st.session_state.expenses.groupby("main_category")["amount"].sum().reset_index()
                chart = alt.Chart(c_data).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                    x=alt.X("main_category:N", title="Operational Segment"),
                    y=alt.Y("amount:Q", title="Capital (NPR)"),
                    color="main_category:N"
                ).properties(height=340)
                st.altair_chart(chart, use_container_width=True)
                
        if not st.session_state.expenses.empty:
            st.subheader("📋 Transaction History Ledger")
            st.dataframe(st.session_state.expenses, use_container_width=True)

    # --- TAB 3: OPERATIONS & TASKS ---
    elif active_tab == "🎯 Operations & Tasks":
        st.markdown('<p class="main-title">Operations Engine & To-Do Queue</p>', unsafe_allow_html=True)
        
        with st.expander("💼 Dispatch New Task", expanded=False):
            t_title = st.text_input("Task Objective Name")
            t_deadline = st.date_input("Target Deadline", datetime.today() + timedelta(days=1))
            t_client = st.text_input("Client Corporate Profile")
            t_address = st.text_input("Site Location Address")
            t_priority = st.selectbox("Priority Urgency Tier", ["Critical", "High", "Medium", "Low"])
            
            if st.button("Commit Task to Queue", type="primary"):
                new_t = pd.DataFrame([{"title": t_title, "deadline": t_deadline, "client": t_client, "address": t_address, "priority": t_priority, "status": "Pending"}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_t], ignore_index=True)
                st.success("Task deployed.")
                st.rerun()
                
        ct1, ct2 = st.columns(2)
        with ct1:
            st.markdown('<p class="metric-lbl" style="color:#ef4444;">⚡ Active Tasks Pipeline</p>', unsafe_allow_html=True)
            p_tasks = st.session_state.tasks[st.session_state.tasks["status"] == "Pending"]
            
            if not p_tasks.empty:
