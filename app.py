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

# Initialize Robust Local Storage Frameworks
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["title", "deadline", "client", "address", "priority", "status"])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame(columns=["date", "segment", "details"])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=["type", "entity", "volume", "deadline", "status"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 2. APPLICATION LOGIN SECURITY GATEWAY
# ==========================================
if not st.session_state.logged_in:
    st.title("💼 Mero App")
    st.subheader("Premium Personal Management Suite")
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.write("---")
        email = st.text_input("Gmail Address")
        password = st.text_input("Security Password", type="password")
        st.write("")
        if st.button("Authenticate & Log In", type="primary", use_container_width=True):
            if email == "razumaharjan@gmail.com" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid security access credentials.")
    st.stop()

# ==========================================
# 3. SECURE WORKSPACE HUB
# ==========================================
st.sidebar.title("Mero App")
st.sidebar.markdown("🛡️ **Raju Maharjan** (Admin)")
st.sidebar.write("---")

active_tab = st.sidebar.radio(
    "Dashboard Navigation", 
    ["💎 Executive Hub", "💰 Financial Ledger", "🎯 Operations & Tasks", "🩺 Wellness & Health", "💳 Credit Counterparty"]
)

st.sidebar.write("---")
if st.sidebar.button("Log Out / Terminate", type="secondary", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- MODULE 1: EXECUTIVE HUB (HOME OVERVIEW) ---
if active_tab == "💎 Executive Hub":
    st.title("💎 Executive Overview Hub")
    st.write("Real-time summary analytics matching your system activity indicators.")
    st.write("")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Cumulative Financial Expenses", value=f"NPR {st.session_state.expenses['amount'].sum():,.2f}")
    with c2:
        st.metric(label="Active Pipeline Backlog", value=f"{len(st.session_state.tasks[st.session_state.tasks['status'] == 'Pending'])} Pending Tasks")
    with c3:
        receivables = st.session_state.credit[st.session_state.credit['type'] == 'Money Lent (They Owe You)']['volume'].sum()
        st.metric(label="Outstanding Family Receivables", value=f"NPR {receivables:,.2f}")

# --- MODULE 2: SPLIT-SCREEN FINANCIAL LEDGER ---
elif active_tab == "💰 Financial Ledger":
    st.title("💰 Financial Transaction Ledger")
    st.write("Process transaction metrics and audit historical expense data pipelines.")
    st.write("")
    
    col_input, col_display = st.columns([1.1, 1.3])
    
    with col_input:
        st.subheader("📝 Record Entry Form")
        e_date = st.date_input("Accounting Date", datetime.today())
        e_shop = st.text_input("Merchant Entity Name", placeholder="e.g. Bhat-Bhateni")
        e_items = st.text_area("Itemization Details", placeholder="List products purchased")
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
        st.write("")
        
        if st.button("Execute Ledger Log", type="primary", use_container_width=True):
            new_exp = pd.DataFrame([{"date": pd.to_datetime(e_date), "shop": e_shop, "items": e_items, "amount": e_amount, "payment_method": e_method, "main_category": main_cat, "sub_category": e_sub_cat}])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_exp], ignore_index=True)
            st.success("Transaction successfully authorized and stored.")
            st.rerun()
            
    with col_display:
        st.subheader("📊 Dynamic Financial Monitor")
        if not st.session_state.expenses.empty:
            c_data = st.session_state.expenses.groupby("main_category")["amount"].sum().reset_index()
            chart = alt.Chart(c_data).mark_bar(color="#38bdf8", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("main_category:N", title="Segment"),
                y=alt.Y("amount:Q", title="Capital spent (NPR)")
            ).properties(height=260)
            st.altair_chart(chart, use_container_width=True)
            
            st.write("---")
            st.subheader("📋 Saved Transaction Ledger Feed")
            st.dataframe(st.session_state.expenses.sort_values(by="date", ascending=False), use_container_width=True)
        else:
            st.info("No recorded activity available. Submit the input form to generate records.")

# --- MODULE 3: PERFECT SPLIT SCREEN OPERATIONS & TASKS ---
elif active_tab == "🎯 Operations & Tasks":
    st.title("🎯 Operations Engine & Task Pipelines")
    st.write("Track corporate obligations, set client project parameters, and archive secure billing history logs.")
    st.write("")
    
    col_task_form, col_task_logs = st.columns([1.1, 1.3])
    
    with col_task_form:
        st.subheader("💼 Create Objective Parameters")
        t_title = st.text_input("Task Objective Name")
        t_deadline = st.date_input("Target Close Deadline", datetime.today() + timedelta(days=1))
        t_client = st.text_input("Client Corporate Profile")
        t_address = st.text_input("Site Location Address")
        t_priority = st.selectbox("Priority Urgency Tier", ["Critical", "High", "Medium", "Low"])
        st.write("")
        
        if st.button("Commit Task to Queue", type="primary", use_container_width=True):
            new_t = pd.DataFrame([{"title": t_title, "deadline": t_deadline, "client": t_client, "address": t_address, "priority": t_priority, "status": "Pending"}])
            st.session_state.tasks = pd.concat([st.session_state.tasks, new_t], ignore_index=True)
            st.success("Target workflow successfully deployed.")
            st.rerun()
            
    with col_task_logs:
        st.subheader("⚡ Live Operations Pipeline Monitor")
        p_tasks = st.session_state.tasks[st.session_state.tasks["status"] == "Pending"]
        
        if not p_tasks.empty:
            st.dataframe(p_tasks[["title", "priority", "deadline", "client", "address"]], use_container_width=True)
            
            task_to_close = st.selectbox("Select Target Objective to Finalize", p_tasks["title"].tolist())
            if st.button("Execute Close Protocol & Archive", type="secondary", use_container_width=True):
                target_idx = st.session_state.tasks[st.session_state.tasks["title"] == task_to_close].index
                st.session_state.tasks.at[target_idx, "status"] = "Done"
                st.success("Task verified and committed to historical records.")
                st.rerun()
        else:
            st.info("No active operations tracked. Your backlog schedule is clear.")
            
        st.write("---")
        st.subheader("🗄️ Completed Evidence Logs (Read-Only History)")
        d_tasks = st.session_state.tasks[st.session_state.tasks["status"] == "Done"]
        if not d_tasks.empty:
            st.dataframe(d_tasks[["title", "priority", "deadline", "client", "address"]], use_container_width=True)
        else:
            st.caption("No historical records archived in the evidence line yet.")

# --- MODULE 4: PREMIUM HEALTH DESIGN (WELLNESS CONSOLE) ---
elif active_tab == "🩺 Wellness & Health":
    st.title("🩺 Biometric & Health Monitoring Console")
    st.write("Track training consistency, check prescription status logs, and monitor consultant schedules.")
    st.write("")
    
    col_h_form, col_h_history = st.columns([1.1, 1.3])
    with col_h_form:
        st.subheader("📝 Log Wellness Metrics")
        h_segment = st.selectbox("Segment Filter", ["Workout Routine Execution", "Prescription / Medicine Log", "Hospital Checkup Consultation"])
