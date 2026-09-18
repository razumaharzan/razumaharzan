import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(page_title="Mero App", layout="wide", page_icon="💰")

# Simulate a simple user database in memory for testing
if "users" not in st.session_state:
    st.session_state.users = {
        "razumaharjan@gmail.com": {"password": "admin123", "role": "Admin"},
        "family1@gmail.com": {"password": "user123", "role": "Member"},
        "family2@gmail.com": {"password": "user456", "role": "Member"}
    }

# Initialize data stores in session state (acting as local cloud tables)
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "user", "date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"
    ])

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=[
        "user", "title", "deadline", "client", "address", "priority", "status"
    ])

if "health" not in st.session_state:
    st.session_state.health = pd.DataFrame(columns=[
        "user", "date", "activity_type", "details"
    ])

if "credit" not in st.session_state:
    st.session_state.credit = pd.DataFrame(columns=[
        "user", "type", "person", "amount", "due_date", "status"
    ])

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# ==========================================
# 2. AUTHENTICATION MODULE
# ==========================================
def login_screen():
    st.title("🔒 Mero App - Secure Login")
    st.write("Welcome back! Please sign in to manage your workspace.")
    
    email = st.text_input("Gmail Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", type="primary"):
        if email in st.session_state.users and st.session_state.users[email]["password"] == password:
            st.session_state.logged_in_user = email
            st.session_state.user_role = st.session_state.users[email]["role"]
            st.success(f"Logged in successfully as {st.session_state.user_role}!")
            st.rerun()
        else:
            st.error("Invalid email address or password. Please try again.")

if st.session_state.logged_in_user is None:
    login_screen()
else:
    # Top bar navigation & logout button
    current_user = st.session_state.logged_in_user
    current_role = st.session_state.user_role
    
    col_nav, col_logo = st.columns([8, 2])
    with col_logo:
        st.write(f"👤 **{current_user}** ({current_role})")
        if st.button("Log Out"):
            st.session_state.logged_in_user = None
            st.session_state.user_role = None
            st.rerun()
            
    # Main Application Navigation Tabs
    tabs = ["💰 Expenses", "📋 Work & Tasks", "🏋️ Health", "💳 Credit Ledger"]
    if current_role == "Admin":
        tabs.append("👑 Family Overview")
        
    active_tab = st.sidebar.radio("Navigation Menu", tabs)
    
    # ==========================================
    # 3. EXPENSE TRACKER MODULE
    # ==========================================
    if "Expenses" in active_tab:
        st.header("💰 Personal Expense Tracker")
        
        # Expense Form Input
        with st.expander("➕ Log New Expense", expanded=True):
            exp_date = st.date_input("Date Selection", datetime.today())
            exp_shop = st.text_input("Shop / Merchant Name", placeholder="e.g. Bhat-Bhateni, Local Tea Shop")
            exp_items = st.text_area("Items Purchased", placeholder="e.g. Tea, Coffee, Groceries, Petrol")
            exp_amount = st.number_input("Total Amount (NPR)", min_value=0.0, step=10.0)
            exp_method = st.selectbox("Payment Method", ["Cash", "Cheque", "QR", "E-Wallet"])
            
            # Cascading categories logic
            main_cat = st.selectbox("Main Category", ["Food", "Transport", "Subscriptions", "Health", "Groceries"])
            if main_cat == "Food":
                sub_cat = st.selectbox("Sub-Category", ["Tea", "Coffee", "Breakfast", "Lunch", "Dinner"])
            elif main_cat == "Transport":
                sub_cat = st.selectbox("Sub-Category", ["Petrol", "Gas", "Indrive", "Pathao", "Uber", "Public Bus"])
            elif main_cat == "Subscriptions":
                sub_cat = st.selectbox("Sub-Category", ["Netflix", "Internet", "Software", "Gym Membership"])
            elif main_cat == "Health":
                sub_cat = st.selectbox("Sub-Category", ["Medicine", "Hospital Checkup", "Doctor Consultation"])
            else:
                sub_cat = st.selectbox("Sub-Category", ["Kitchen Supplies", "Vegetables", "Meat", "Toiletries"])
                
            if st.button("Save Expense Entry"):
                new_exp = pd.DataFrame([{
                    "user": current_user, "date": exp_date, "shop": exp_shop, "items": exp_items,
                    "amount": exp_amount, "payment_method": exp_method, "main_category": main_cat, "sub_category": sub_cat
                }])
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_exp], ignore_index=True)
                st.success("Expense successfully logged in cloud storage system!")
                
        # Filter personal data
        my_expenses = st.session_state.expenses[st.session_state.expenses["user"] == current_user]
        
        if not my_expenses.empty:
            st.subheader("📊 Your Expense Reports")
            report_type = st.radio("Select Report Range", ["Weekly", "Monthly", "Yearly"], horizontal=True)
            
            # Simple reactive graph aggregation
            chart_data = my_expenses.groupby("main_category")["amount"].sum().reset_index()
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X("main_category:N", title="Category"),
                y=alt.Y("amount:Q", title="Total Amount spent"),
                color="main_category:N"
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
            
            st.subheader("📋 Expense Log History")
            st.dataframe(my_expenses[["date", "shop", "items", "amount", "payment_method", "main_category", "sub_category"]], use_container_width=True)
        else:
            st.info("No expense items found. Start logging above to see metrics reports.")

    # ==========================================
    # 4. WORK TO-DO BOARD MODULE
    # ==========================================
    elif "Work & Tasks" in active_tab:
        st.header("📋 Advanced Work Tasks & To-Do List")
        
        with st.expander("➕ Add New Task", expanded=False):
            t_title = st.text_input("Task Title")
            t_deadline = st.date_input("Deadline Date", datetime.today() + timedelta(days=1))
            t_client = st.text_input("Client / Company Name")
            t_address = st.text_input("Work Site Address")
            t_priority = st.selectbox("Priority Tier", ["Critical", "High", "Medium", "Low"])
            
            if st.button("Add Task to Board"):
                new_task = pd.DataFrame([{
                    "user": current_user, "title": t_title, "deadline": t_deadline, 
                    "client": t_client, "address": t_address, "priority": t_priority, "status": "Pending"
                }])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                st.success("Task created with tracking reminder parameters!")
                st.rerun()

        my_tasks = st.session_state.tasks[st.session_state.tasks["user"] == current_user]
        
        if not my_tasks.empty:
            st.subheader("⚡ Active Tasks Queue")
            pending_tasks = my_tasks[my_tasks["status"] == "Pending"]
            
            if not pending_tasks.empty:
                for idx, row in pending_tasks.iterrows():
                    col1, col2 = st.columns([8, 2])
                    with col1:
                        st.markdown(f"**{row['title']}** | Priority: `{row['priority']}` | Due: {row['deadline']}")
                        st.caption(f"Client: {row['client']} | Address: {row['address']}")
                    with col2:
                        if st.button("Mark Done", key=f"done_{idx}"):
                            st.session_state.tasks.at[idx, "status"] = "Done"
                            st.rerun()
                    st.divider()
            else:
                st.info("No active pending tasks on your list right now.")

            st.subheader("🗄️ Completed Evidence Ledger (Read-Only History)")
            done_tasks = my_tasks[my_tasks["status"] == "Done"]
            if not done_tasks.empty:
                st.dataframe(done_tasks[["title", "deadline", "client", "address", "priority"]], use_container_width=True)
            else:
                st.caption("No archived records found.")

    # ==========================================
    # 5. HEALTH & AUXILIARY MODULES
    # ==========================================
    elif "Health" in active_tab:
        st.header("🏋️ Workout & Health Monitor")
        h_type = st.selectbox("Log Type", ["Workout Routine", "Medicine Intake", "Hospital Checkup / Consultation"])
        h_details = st.text_area("Details & Notes")
        
        if st.button("Save Health Log Entry"):
            new_h = pd.DataFrame([{"user": current_user, "date": datetime.today().date(), "activity_type": h_type, "details": h_details}])
            st.session_state.health = pd.concat([st.session_state.health, new_h], ignore_index=True)
            st.success("Health log successfully saved.")
            
        my_health = st.session_state.health[st.session_state.health["user"] == current_user]
