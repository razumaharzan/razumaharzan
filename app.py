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
    st.session_state.health = pd.DataFrame(columns=["date", "category", "details"])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=["type", "name", "amount", "due_date", "status"])

# Temporary memory to build an invoice list before clicking the final save button
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 2. APPLICATION LOGIN SECURITY GATEWAY
# ==========================================
if st.session_state.logged_in == False:
    st.title("💼 Mero App")
    st.subheader("Your Personal Expense & Work Dashboard")
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.write("---")
        email = st.text_input("Gmail Address")
        password = st.text_input("Password", type="password")
        st.write("")
        if st.button("Log In", type="primary", use_container_width=True):
            if email == "razumaharjan@gmail.com" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid email address or password.")
    st.stop()

# ==========================================
# 3. SECURE WORKSPACE HUB
# ==========================================
st.sidebar.title("Mero App")
st.sidebar.markdown("🛡️ **Raju Maharjan** (Admin)")
st.sidebar.write("---")

active_tab = st.sidebar.radio(
    "Menu", 
    ["💎 Home Overview", "💰 Expense Tracker", "🎯 My To-Do List", "🩺 Health Monitor", "💳 Credit & Payments"]
)

st.sidebar.write("---")
if st.sidebar.button("Log Out", type="secondary", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- MODULE 1: HOME OVERVIEW ---
if active_tab == "💎 Home Overview":
    st.title("💎 Summary Overview")
    st.write("Quick stats tracking your total spending, ongoing work tasks, and unpaid balances.")
    st.write("")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Total Expenses Registered", value=f"NPR {st.session_state.expenses['amount'].sum():,.2f}")
    with c2:
        st.metric(label="Pending Tasks Remaining", value=f"{len(st.session_state.tasks[st.session_state.tasks['status'] == 'Pending'])} Tasks Left")
    with c3:
        receivables = st.session_state.credit[st.session_state.credit['type'] == 'Money Lent (People Owe Me)']['amount'].sum()
        st.metric(label="Total Outstanding Receivables", value=f"NPR {receivables:,.2f}")

# --- MODULE 2: INVOICE-STYLE EXPENSE TRACKER ---
if active_tab == "💰 Expense Tracker":
    st.title("💰 Personal Expense Tracker")
    st.write("Add multiple items to build your bill list below, then click save at the end.")
    st.write("")
    
    col_input, col_display = st.columns([1.2, 1.2])
    
    with col_input:
        st.subheader("📝 1. Bill Details")
        e_date = st.date_input("Date Selection", datetime.today())
        e_shop = st.text_input("Shop / Merchant Name", placeholder="e.g. Bhat-Bhateni, Local Tea Shop")
        e_method = st.selectbox("Payment Method", ["QR Payment", "E-Wallet (eSewa/Khalti)", "Cash", "Cheque"])
        
        st.write("---")
        st.subheader("➕ 2. Add New Item")
        
        item_name = st.text_input("Item Name / Description", placeholder="e.g., Milk, Bread, Coffee, Petrol")
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
                "date": pd.to_datetime(e_date), "shop": e_shop, "items": item_name, "amount": item_price,
                "payment_method": e_method, "main_category": main_cat, "sub_category": e_sub_cat
            })
            st.toast(f"Added {item_name} to receipt list!")
            st.rerun()

    with col_display:
        st.subheader("🛒 3. Live Receipt View")
        
        df_invoice = pd.DataFrame(st.session_state.invoice_items)
        st.dataframe(df_invoice, use_container_width=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 SAVE INVOICE ENTRY", type="primary", use_container_width=True):
                st.session_state.expenses = pd.concat([st.session_state.expenses, df_invoice], ignore_index=True)
                st.session_state.invoice_items = [] 
                st.success("Invoice successfully saved into history log database!")
                st.rerun()
        with col_b2:
            if st.button("❌ Clear List", type="secondary", use_container_width=True):
                st.session_state.invoice_items = []
                st.warning("Current active list cleared.")
                st.rerun()
            
    st.write("---")
    st.subheader("📋 Expense History Logs")
    if len(st.session_state.expenses) > 0:
        c_data = st.session_state.expenses.groupby("main_category")["amount"].sum().reset_index()
        chart = alt.Chart(c_data).mark_bar(color="#38bdf8", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("main_category:N", title="Category"),
            y=alt.Y("amount:Q", title="Total Spent (NPR)")
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(st.session_state.expenses.sort_values(by="date", ascending=False), use_container_width=True)

# --- MODULE 3: DYNAMIC OPERATIONS TO-DO LIST ---
if active_tab == "🎯 My To-Do List":
    st.title("🎯 Work List & Tasks Management")
    st.write("Create work objectives, set client details, and log tasks securely for record evidence.")
    st.write("")
    
    col_task_form, col_task_logs = st.columns([1.1, 1.3])
    
    with col_task_form:
        st.subheader("➕ Add New Task")
        t_title = st.text_input("Task Name / Objective")
        t_deadline = st.date_input("Deadline Date", datetime.today() + timedelta(days=1))
        t_client = st.text_input("Company / Client Name")
        t_address = st.text_input("Work Address")
        t_priority = st.selectbox("Task Category Priority", ["Critical", "High", "Medium", "Low"])
        st.write("")
        
        if st.button("Save Task to List", type="primary", use_container_width=True):
            new_t = pd.DataFrame([{"title": t_title, "deadline": t_deadline, "client": t_client, "address": t_address, "priority": t_priority, "status": "Pending"}])
            st.session_state.tasks = pd.concat([st.session_state.tasks, new_t], ignore_index=True)
            st.success("New task created and saved to active list.")
            st.rerun()
            
    with col_task_logs:
        st.subheader("⚡ Active Tasks Pipeline")
        
        # Pull indexes of current active pending tasks
        p_tasks = st.session_state.tasks[st.session_state.tasks["status"] == "Pending"]
        st.dataframe(p_tasks[["title", "priority", "deadline", "client", "address"]], use_container_width=True)
        
        # Simple click options to close task directly without any typing errors
        st.markdown("**Click Done to Complete a Task:**")
        
        # Use single button lines mapped securely to row content to bypass index failures
        pending_titles = p_tasks["title"].tolist()
        
        # Generate target select box matching current list values cleanly
        task_selection = st.selectbox("Choose task to complete:", ["-- Select Task --"] + pending_titles)
        if st.button("Mark Selected Task as Done ✅", type="secondary", use_container_width=True):
            if task_selection != "-- Select Task --":
                # Safely update using content match selector query paths
                match_idx = st.session_state.tasks[st.session_state.tasks["title"] == task_selection].index
                st.session_state.tasks.at[match_idx[0], "status"] = "Done"
                st.success(f"Archived '{task_selection}' safely into historical records.")
                st.markdown('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
