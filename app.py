import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import hashlib
from datetime import datetime, date

# ==========================================
# 1. DATABASE & PERSISTENCE LAYER (SQLite)
# ==========================================
DB_FILE = "mero_app.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        # Expenses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                shop TEXT,
                items TEXT,
                amount REAL,
                payment_method TEXT,
                main_category TEXT,
                sub_category TEXT
            )
        """)
        # Tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                deadline TEXT,
                client TEXT,
                priority TEXT,
                status TEXT
            )
        """)
        # Health & Wellness
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                activity_type TEXT,
                details TEXT,
                calories INTEGER
            )
        """)
        # Daily Water Tracker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_water (
                date TEXT PRIMARY KEY,
                cups INTEGER
            )
        """)
        # Credit / Counterparty
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                person TEXT,
                amount REAL,
                due_date TEXT,
                status TEXT
            )
        """)
        conn.commit()

init_db()

# ==========================================
# 2. AUTHENTICATION & SECURITY
# ==========================================
def hash_password(password: str) -> str:
    salt = "mero_salt_secure_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Default admin hash for "admin123"
ADMIN_EMAIL = "razumaharjan@gmail.com"
ADMIN_PASSWORD_HASH = hash_password("admin123")

def verify_credentials(email: str, password: str) -> bool:
    return email == ADMIN_EMAIL and hash_password(password) == ADMIN_PASSWORD_HASH

# ==========================================
# 3. PAGE INITIALIZATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Mero App — Executive Management Suite", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #38bdf8;
        margin-top: 4px;
    }
    .metric-lbl {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .main-title {
        font-size: 30px;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

# ==========================================
# 4. LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; margin-top: 60px;"><p class="main-title">MERO APP</p><p style="color:#64748b;">Personal ERP & Executive Operating System</p></div>', unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.form("login_form"):
            st.markdown('<p style="font-weight:600; color:#cbd5e1;">Sign In to Executive Console</p>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="razumaharjan@gmail.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Authenticate & Enter", type="primary", use_container_width=True)
            
            if submit:
                if verify_credentials(email, password):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your email and password.")
    st.stop()

# ==========================================
# 5. SIDEBAR & NAVIGATION
# ==========================================
st.sidebar.markdown('<p class="main-title" style="font-size:22px; padding-left:5px;">Mero Suite</p>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="padding-left:5px; color:#94a3b8; font-size:13px; margin-bottom:15px;">🛡️ Operator: <b>Raju Maharjan</b></div>', unsafe_allow_html=True)

active_tab = st.sidebar.radio(
    "Control Matrix", 
    ["💎 Executive Hub", "💰 Financial Ledger", "🎯 Operations & Tasks", "🩺 Wellness & Health", "💳 Credit Counterparty"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Terminate Session", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

conn = get_db()

# ==========================================
# MODULE 1: EXECUTIVE HUB
# ==========================================
if active_tab == "💎 Executive Hub":
    st.markdown('<p class="main-title">Executive Hub</p>', unsafe_allow_html=True)
    st.caption("Consolidated real-time operational and financial telemetry.")
    
    # Query aggregations
    total_expenses = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
    pending_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
    money_lent = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM credit WHERE type = 'Money Lent' AND status = 'Pending'").fetchone()[0]
    money_owed = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM credit WHERE type = 'Money Borrowed' AND status = 'Pending'").fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Expenses</div><div class="metric-val">NPR {total_expenses:,.2f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Pending Operations</div><div class="metric-val" style="color:#f43f5e;">{pending_tasks} Tasks</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Receivables (Lent)</div><div class="metric-val" style="color:#10b981;">NPR {money_lent:,.2f}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Payables (Borrowed)</div><div class="metric-val" style="color:#fbbf24;">NPR {money_owed:,.2f}</div></div>', unsafe_allow_html=True)

    col_recent_left, col_recent_right = st.columns(2)
    with col_recent_left:
        st.subheader("📌 Urgent Pending Operations")
        urgent_tasks = pd.read_sql("SELECT title, priority, deadline, client FROM tasks WHERE status != 'Completed' ORDER BY deadline ASC LIMIT 5", conn)
        if len(urgent_tasks) > 0:
            st.dataframe(urgent_tasks, use_container_width=True, hide_index=True)
        else:
            st.info("No pending tasks. Operations are running smoothly!")

    with col_recent_right:
        st.subheader("📊 Recent Expenditure Stream")
        recent_exp = pd.read_sql("SELECT date, shop, items, amount, payment_method FROM expenses ORDER BY id DESC LIMIT 5", conn)
        if len(recent_exp) > 0:
            st.dataframe(recent_exp, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses logged yet.")

# ==========================================
# MODULE 2: FINANCIAL TRANSACTION LEDGER
# ==========================================
elif active_tab == "💰 Financial Ledger":
    st.markdown('<p class="main-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
    st.caption("Track daily spend, create multi-item receipts, and visualize category flows.")
    
    col_entry, col_staging = st.columns([1, 1.2])
    
    with col_entry:
        with st.container(border=True):
            st.markdown("##### ➕ Create Receipt Item")
            e_date = st.date_input("Accounting Date", date.today())
            e_shop = st.text_input("Merchant Entity Name", placeholder="e.g. Shell Mart, Coffee Lab")
            item_name = st.text_input("Item Description", placeholder="e.g. Petrol, Americano")
            item_price = st.number_input("Item Cost (NPR)", min_value=0.0, step=20.0, value=0.0)
            
            c_method, c_main = st.columns(2)
            with c_method:
                e_method = st.selectbox("Payment Channel", ["QR Payment", "E-Wallet", "Cash", "Bank Card / Transfer"])
            with c_main:
                main_cat = st.selectbox("Category", ["Food & Dining", "Logistics & Fuel", "Subscriptions", "Medical & Care", "Groceries & Supplies"])
                
            sub_category_map = {
                "Food & Dining": ["Coffee/Tea", "Breakfast", "Lunch", "Dinner", "Snacks"],
                "Logistics & Fuel": ["Petrol/Diesel", "Pathao/InDrive", "Bus/Transport", "Vehicle Service"],
                "Subscriptions": ["Internet", "Software/SaaS", "Gym Membership", "Streaming"],
                "Medical & Care": ["Pharmacy", "Doctor Consultation", "Dental", "Supplements"],
                "Groceries & Supplies": ["Supermarket", "Vegetables", "Meat", "Household"]
            }
            e_sub_cat = st.selectbox("Sub-Allocation", sub_category_map.get(main_cat, ["General"]))
            
            if st.button("➕ Queue Item to Receipt", use_container_width=True):
                if item_price > 0 and item_name.strip():
                    st.session_state.invoice_items.append({
                        "date": str(e_date),
                        "shop": e_shop.strip() or "Standard Retail",
                        "items": item_name.strip(),
                        "amount": float(item_price),
                        "payment_method": e_method,
                        "main_category": main_cat,
                        "sub_category": e_sub_cat
                    })
                    st.toast(f"Added {item_name} to current receipt staging queue!")
                    st.rerun()
                else:
                    st.warning("Please supply a valid item name and amount.")

    with col_staging:
        with st.container(border=True):
            st.markdown("##### 🛒 Pending Receipt Queue")
            if st.session_state.invoice_items:
                df_staging = pd.DataFrame(st.session_state.invoice_items)
                st.dataframe(df_staging[["items", "amount", "main_category", "sub_category"]], use_container_width=True, hide_index=True)
                
                total_receipt = df_staging["amount"].sum()
                st.markdown(f"**Total Batch Amount:** `NPR {total_receipt:,.2f}`")
                
                c_save, c_clear = st.columns(2)
                with c_save:
                    if st.button("💾 Commit Batch to Database", type="primary", use_container_width=True):
                        with conn:
                            for row in st.session_state.invoice_items:
                                conn.execute("""
                                    INSERT INTO expenses (date, shop, items, amount, payment_method, main_category, sub_category)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (row["date"], row["shop"], row["items"], row["amount"], row["payment_method"], row["main_category"], row["sub_category"]))
                        st.session_state.invoice_items = []
                        st.success("Batch successfully committed to database!")
                        st.rerun()
                with c_clear:
                    if st.button("🗑️ Clear Queue", use_container_width=True):
                        st.session_state.invoice_items = []
                        st.rerun()
            else:
                st.info("Receipt staging queue is empty. Add items using the left form.")

    st.markdown("---")
    
    # Financial Analytics
    df_expenses = pd.read_sql("SELECT * FROM expenses ORDER BY id DESC", conn)
    if not df_expenses.empty:
        st.subheader("📊 Category Expenditure Breakdown")
        cat_summary = df_expenses.groupby("main_category")["amount"].sum().reset_index()
        
        chart = alt.Chart(cat_summary).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("main_category:N", title="Budget Category", sort="-y"),
            y=alt.Y("amount:Q", title="Total Spent (NPR)"),
            color=alt.Color("main_category:N", legend=None)
        ).properties(height=260)
        
        st.altair_chart(chart, use_container_width=True)
        
        st.subheader("📋 Master Ledger")
        st.dataframe(df_expenses, use_container_width=True, hide_index=True)
        
        csv_data = df_expenses.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Ledger to CSV", data=csv_data, file_name="mero_expenses_ledger.csv", mime="text/csv")
    else:
        st.caption("No records available in database yet.")

# ==========================================
# MODULE 3: OPERATIONS & TASK ENGINE
# ==========================================
elif active_tab == "🎯 Operations & Tasks":
    st.markdown('<p class="main-title">Operations Engine & To-Do Queue</p>', unsafe_allow_html=True)
    st.caption("Manage workflows, client deadlines, operational priorities, and execution status.")

    col_t_form, col_t_list = st.columns([1, 1.4])
    
    with col_t_form:
        with st.container(border=True):
            st.markdown("##### ➕ Schedule New Task")
            with st.form("task_form", clear_on_submit=True):
                t_title = st.text_input("Task Objective / Name", placeholder="e.g. Review Q3 Tax Filings")
                t_client = st.text_input("Associated Client / Stakeholder", placeholder="e.g. Internal / ACME Corp")
                t_deadline = st.date_input("Target Completion Date", date.today())
                t_priority = st.selectbox("Priority Level", ["🔴 High", "🟡 Medium", "🔵 Low"])
                
                add_task_btn = st.form_submit_button("Create Objective", type="primary", use_container_width=True)
                if add_task_btn:
                    if t_title.strip():
                        with conn:
                            conn.execute("""
                                INSERT INTO tasks (title, deadline, client, priority, status)
                                VALUES (?, ?, ?, ?, ?)
                            """, (t_title.strip(), str(t_deadline), t_client.strip() or "General", t_priority, "Pending"))
                        st.success(f"Task '{t_title}' established!")
                        st.rerun()
                    else:
                        st.error("Task objective name is required.")

    with col_t_list:
        with st.container(border=True):
            st.markdown("##### 📋 Active Operations Queue")
            df_tasks = pd.read_sql("SELECT * FROM tasks ORDER BY id DESC", conn)
            
            if not df_tasks.empty:
                # Provide inline editor for statuses
                edited_tasks = st.data_editor(
                    df_tasks,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", disabled=True),
                        "status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pending", "In Progress", "Completed"],
                            required=True
                        ),
                        "priority": st.column_config.TextColumn("Priority", disabled=True),
                        "deadline": st.column_config.DateColumn("Target Date")
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="task_editor"
                )
                
                # Detect and persist edits
                if st.button("💾 Update Task Status Changes", use_container_width=True):
                    with conn:
                        for _, row in edited_tasks.iterrows():
                            conn.execute("UPDATE tasks SET status = ?, deadline = ? WHERE id = ?", 
                                         (row["status"], str(row["deadline"]), row["id"]))
                    st.success("All task states updated successfully!")
                    st.rerun()
            else:
                st.info("No active tasks found. Create one using the form on the left.")

# ==========================================
# MODULE 4: WELLNESS & HEALTH
# ==========================================
elif active_tab == "🩺 Wellness & Health":
    st.markdown('<p class="main-title">Wellness & Vitality Matrix</p>', unsafe_allow_html=True)
    st.caption("Sustain high executive performance with daily hydration, workout routines, and energy logs.")
    
    today_str = str(date.today())
    
    # Fetch today's water
    water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
    current_water = water_row[0] if water_row else 0

    col_water, col_vitality = st.columns([1, 1.4])
    
    with col_water:
        with st.container(border=True):
            st.markdown("##### 💧 Daily Hydration Tracker")
            st.caption("Recommended target: 8-10 glasses (2.5L)")
            
            st.metric("Glasses Consumed Today", f"{current_water} / 8 Glasses")
            st.progress(min(current_water / 8.0, 1.0))
            
            cw1, cw2 = st.columns(2)
            with cw1:
                if st.button("➕ Drink Glass", use_container_width=True):
                    with conn:
                        conn.execute("""
                            INSERT INTO daily_water (date, cups) VALUES (?, 1)
                            ON CONFLICT(date) DO UPDATE SET cups = cups + 1
                        """, (today_str,))
                    st.rerun()
            with cw2:
                if st.button("➖ Remove Glass", use_container_width=True):
                    if current_water > 0:
                        with conn:
                            conn.execute("UPDATE daily_water SET cups = cups - 1 WHERE date = ?", (today_str,))
                        st.rerun()

    with col_vitality:
        with st.container(border=True):
            st.markdown("##### 🏃 Record Workout or Vitality Log")
            with st.form("health_form", clear_on_submit=True):
                activity = st.selectbox("Activity Type", ["Weight Training", "Running / Cardio", "Yoga / Mobility", "High Intensity Walking", "Meditation"])
                details = st.text_input("Session Notes", placeholder="e.g. Chest & Triceps (Heavy), 5km Morning Run")
                calories = st.number_input("Estimated Calories Burned (kcal)", min_value=0, step=25, value=250)
                
                submit_health = st.form_submit_button("Log Wellness Session", type="primary", use_container_width=True)
                if submit_health:
                    with conn:
                        conn.execute("""
                            INSERT INTO health (date, activity_type, details, calories)
                            VALUES (?, ?, ?, ?)
                        """, (today_str, activity, details, calories))
                    st.success("Session documented successfully!")
                    st.rerun()

    st.markdown("---")
    st.subheader("📈 Health & Workout History")
    df_health = pd.read_sql("SELECT * FROM health ORDER BY id DESC LIMIT 15", conn)
    if not df_health.empty:
        st.dataframe(df_health[["date", "activity_type", "details", "calories"]], use_container_width=True, hide_index=True)
    else:
        st.info("No workout sessions logged yet.")

# ==========================================
# MODULE 5: CREDIT & COUNTERPARTY
# ==========================================
elif active_tab == "💳 Credit Counterparty":
    st.markdown('<p class="main-title">Credit & Counterparty Book</p>', unsafe_allow_html=True)
    st.caption("Manage receivables (money lent to others) and payables (money borrowed) with zero ambiguity.")
    
    col_credit_entry, col_credit_list = st.columns([1, 1.4])
    
    with col_credit_entry:
        with st.container(border=True):
            st.markdown("##### ➕ Create Counterparty Position")
            with st.form("credit_form", clear_on_submit=True):
                c_type = st.selectbox("Position Type", ["Money Lent", "Money Borrowed"])
                person = st.text_input("Counterparty Person / Entity", placeholder="e.g. Sunil Shrestha")
                amount = st.number_input("Capital Amount (NPR)", min_value=1.0, step=500.0, value=1000.0)
                due_date = st.date_input("Settlement Due Date", date.today() + pd.Timedelta(days=14))
                
                submit_credit = st.form_submit_button("Record Counterparty Entry", type="primary", use_container_width=True)
                if submit_credit:
                    if person.strip():
                        with conn:
                            conn.execute("""
                                INSERT INTO credit (type, person, amount, due_date, status)
                                VALUES (?, ?, ?, ?, ?)
                            """, (c_type, person.strip(), amount, str(due_date), "Pending"))
                        st.success(f"Position for {person} logged!")
                        st.rerun()
                    else:
                        st.error("Please specify counterparty person or entity.")

    with col_credit_list:
        with st.container(border=True):
            st.markdown("##### 📜 Outstanding Counterparty Ledger")
            df_credit = pd.read_sql("SELECT * FROM credit WHERE status = 'Pending' ORDER BY due_date ASC", conn)
            
            if not df_credit.empty:
                st.dataframe(df_credit[["id", "type", "person", "amount", "due_date"]], use_container_width=True, hide_index=True)
                
                # Quick settlement selector
                st.markdown("###### 🤝 Settle Position")
                settle_id = st.selectbox("Select ID to Mark as Settled", df_credit["id"].tolist())
                if st.button("Mark Selected Position as Settled / Paid", use_container_width=True):
                    with conn:
                        conn.execute("UPDATE credit SET status = 'Settled' WHERE id = ?", (settle_id,))
                    st.success(f"Position #{settle_id} marked as fully settled!")
                    st.rerun()
            else:
                st.info("No active outstanding counterparty credit obligations.")

    # Settled History
    df_settled = pd.read_sql("SELECT * FROM credit WHERE status = 'Settled' ORDER BY id DESC LIMIT 5", conn)
    if not df_settled.empty:
        st.markdown("---")
        st.subheader("✅ Settled Archive")
        st.dataframe(df_settled[["type", "person", "amount", "due_date", "status"]], use_container_width=True, hide_index=True)
