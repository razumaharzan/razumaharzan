import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from datetime import datetime, date, timedelta

# ==============================================================================
# 1. DATABASE & AUTOMATIC MIGRATION LAYER (SQLite)
# ==============================================================================
DB_FILE = "mero_app.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        
        # 1. Unified Transactions Table (Income & Expenses)
        c.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT, -- 'Income' or 'Expense'
                entity TEXT,
                description TEXT,
                amount REAL,
                category TEXT,
                payment_method TEXT,
                notes TEXT
            )
        """)
        
        # Backward compatibility migration from legacy 'expenses'
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        if c.fetchone():
            tx_count = c.execute("SELECT count(*) FROM transactions").fetchone()[0]
            if tx_count == 0:
                c.execute("""
                    INSERT INTO transactions (date, type, entity, description, amount, category, payment_method, notes)
                    SELECT date, 'Expense', shop, items, amount, main_category, payment_method, sub_category FROM expenses
                """)
        
        # 2. Rich Operations & Daily Tasks Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                priority TEXT,
                deadline TEXT,
                status TEXT,
                created_date TEXT
            )
        """)
        # Ensure new columns exist on legacy tables
        task_cols = [row[1] for row in c.execute("PRAGMA table_info(tasks)").fetchall()]
        if 'category' not in task_cols:
            c.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'Work & Career'")
        if 'created_date' not in task_cols:
            c.execute("ALTER TABLE tasks ADD COLUMN created_date TEXT DEFAULT ''")

        # 3. Daily Hydration Table
        c.execute("CREATE TABLE IF NOT EXISTS daily_water (date TEXT PRIMARY KEY, cups INTEGER)")
        
        # 4. Exercise Performance Logs
        c.execute("""
            CREATE TABLE IF NOT EXISTS exercise_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise_name TEXT,
                tier TEXT,
                target_sets INTEGER,
                completed_sets INTEGER,
                target_reps INTEGER,
                completed_reps INTEGER,
                duration_min INTEGER,
                rest_sec INTEGER,
                weight_added REAL,
                status TEXT,
                notes TEXT
            )
        """)
        
        # 5. Challenge Adaptive State & Attempts
        c.execute("""
            CREATE TABLE IF NOT EXISTS challenge_state (
                challenge_name TEXT PRIMARY KEY,
                current_day INTEGER,
                retries_count INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS challenge_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_name TEXT,
                day_number INTEGER,
                date TEXT,
                completed_sets INTEGER,
                completed_reps INTEGER,
                actual_duration_min INTEGER,
                actual_rest_sec INTEGER,
                status TEXT,
                notes TEXT
            )
        """)
        for ch in ["30-Day Foundation Challenge", "90-Day Elite Beast Challenge"]:
            c.execute("INSERT OR IGNORE INTO challenge_state (challenge_name, current_day, retries_count) VALUES (?, 1, 0)", (ch,))
        
        conn.commit()

init_db()

# ==============================================================================
# 2. CALISTHENICS & CHALLENGE DOMAIN CONSTANTS
# ==============================================================================
EXERCISE_STANDARDS = {
    "Wall / Incline Push-Ups": {"tier": "Beginner", "category": "Push", "sets": 3, "reps": 12, "duration_min": 15, "rest_sec": 60, "cue": "Straight plank, elbows at 45°"},
    "Scapular Pulls & Dead Hang": {"tier": "Beginner", "category": "Pull", "sets": 3, "reps": 30, "duration_min": 12, "rest_sec": 60, "cue": "Depress shoulder blades without bending elbows"},
    "Incline Australian Rows": {"tier": "Beginner", "category": "Pull", "sets": 3, "reps": 10, "duration_min": 15, "rest_sec": 60, "cue": "Chest to bar, rigid core at 45° angle"},
    "Bodyweight Deep Squats": {"tier": "Beginner", "category": "Legs", "sets": 3, "reps": 15, "duration_min": 15, "rest_sec": 60, "cue": "Heels flat on floor, knees tracking over toes"},
    "Plank & Hollow Body Hold": {"tier": "Beginner", "category": "Core", "sets": 3, "reps": 45, "duration_min": 12, "rest_sec": 45, "cue": "Posterior pelvic tilt, dome upper back"},
    "Strict Standard Push-Ups": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 15, "duration_min": 20, "rest_sec": 90, "cue": "Full chest-to-floor, lockout at top"},
    "Parallel Bar Dips": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 10, "duration_min": 25, "rest_sec": 90, "cue": "Elbows at 90°, slight forward torso lean"},
    "Strict Hollow Pull-Ups": {"tier": "Intermediate", "category": "Pull", "sets": 4, "reps": 8, "duration_min": 25, "rest_sec": 90, "cue": "Dead hang to chin-over-bar without kipping"},
    "Pike Push-Ups (Elevated)": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 8, "duration_min": 20, "rest_sec": 90, "cue": "Hips high, head tracks forward into tripod"},
    "Parallel Bar / Floor L-Sit": {"tier": "Intermediate", "category": "Core", "sets": 4, "reps": 15, "duration_min": 18, "rest_sec": 75, "cue": "Depress shoulders, locked knees, pointed toes"},
    "Bar Muscle-Up": {"tier": "Advanced", "category": "Pull/Push", "sets": 5, "reps": 4, "duration_min": 30, "rest_sec": 120, "cue": "Explosive pull to sternum, rapid wrist snap"},
    "Handstand Push-Ups (Wall)": {"tier": "Advanced", "category": "Push", "sets": 4, "reps": 6, "duration_min": 30, "rest_sec": 120, "cue": "Belly to wall, controlled tripod descent"},
    "Front Lever (Tuck/Full)": {"tier": "Advanced", "category": "Pull", "sets": 5, "reps": 8, "duration_min": 25, "rest_sec": 120, "cue": "Locked arms, pull bar down towards hips"},
    "Full Planche Lean & Tuck": {"tier": "Advanced", "category": "Push", "sets": 5, "reps": 10, "duration_min": 25, "rest_sec": 120, "cue": "Protracted scapula, hands turned out, lean forward"}
}

CALISTHENICS_VIDEOS = {
    "Push-Up Progression (Wall to Floor)": {"coach": "Hybrid Calisthenics", "url": "https://www.youtube.com/watch?v=zkU6Ok44_CI", "tier": "Beginner"},
    "First Pull-Up Progression (0 to 1)": {"coach": "THENX", "url": "https://www.youtube.com/watch?v=itaC8CXWP6A", "tier": "Beginner"},
    "Incline Australian Rows": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=GBqAZP6jquc", "tier": "Beginner"},
    "Deep Bodyweight Squat": {"coach": "Hybrid Calisthenics", "url": "https://www.youtube.com/watch?v=z3XQ7T4-abQ", "tier": "Beginner"},
    "Plank & Hollow Body": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=kL_NJAkCQBg", "tier": "Beginner"},
    "Strict Pull-Up Mastery": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "tier": "Intermediate"},
    "Parallel Bar Dips Guide": {"coach": "FitnessFAQs", "url": "https://www.youtube.com/watch?v=K5JxupmoLW4", "tier": "Intermediate"},
    "Floor L-Sit Tutorial": {"coach": "Antranik", "url": "https://www.youtube.com/watch?v=IUZJoSP66HI", "tier": "Intermediate"},
    "Bar Muscle-Up 3 Steps": {"coach": "THENX", "url": "https://www.youtube.com/watch?v=p7q0UhxPdLY", "tier": "Advanced"},
    "Wall Handstand Push-Ups": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=h0HjqYRlXYg", "tier": "Advanced"},
    "Front Lever Progressions": {"coach": "FitnessFAQs", "url": "https://www.youtube.com/watch?v=AGhb8V8M758", "tier": "Advanced"},
    "Planche Progression Masterclass": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=UZ-1jwG7aQ4", "tier": "Advanced"}
}

CHALLENGE_SPECS = {
    "30-Day Foundation Challenge": {
        "days": 30,
        "blueprint": [
            {"name": "Push Foundation", "protocol": "4 Sets × 12 Incline/Floor Push-Ups", "duration": 25, "rest": 60},
            {"name": "Pull & Scapula Primer", "protocol": "4 Sets × 8 Australian Rows + 30s Dead Hang", "duration": 25, "rest": 60},
            {"name": "Core & Pelvic Stability", "protocol": "4 Sets × 45s Plank + 3x15 Hollow Tucks", "duration": 20, "rest": 45},
            {"name": "Lower Body Power", "protocol": "4 Sets × 15 Deep Squats + 3x12 Walking Lunges", "duration": 25, "rest": 60},
            {"name": "Full Body Volume Circuit", "protocol": "3 Rounds: 10 Push-Ups, 8 Rows, 15 Squats, 30s Plank", "duration": 30, "rest": 75},
            {"name": "Active Mobility & Decompression", "protocol": "20 Mins Shoulder Dislocates & Hangs", "duration": 20, "rest": 30},
            {"name": "Systemic Recovery / Rest Day", "protocol": "Complete Rest, 3L Hydration & Contrast Shower", "duration": 15, "rest": 0}
        ]
    },
    "90-Day Elite Beast Challenge": {
        "days": 90,
        "blueprint": [
            {"name": "Explosive Upper Pull", "protocol": "5 Sets × 6 Strict Pull-Ups + 4x8 Archer Rows", "duration": 35, "rest": 90},
            {"name": "Heavy Push & Overhead", "protocol": "5 Sets × 10 Deep Dips + 4x6 Elevated Pike Push-Ups", "duration": 35, "rest": 90},
            {"name": "Core Compression & Lever", "protocol": "5 Sets × 15s L-Sit Hold + 4x8 Hanging Leg Raises", "duration": 30, "rest": 75},
            {"name": "Pistol & Plyo Leg Engine", "protocol": "4 Sets × 6 Pistol Squats (per leg) + 4x10 Jump Squats", "duration": 35, "rest": 90},
            {"name": "Skill Crucible (Muscle-Up & HSPU)", "protocol": "5 Sets × 3 Muscle-Up Attempts + 4x5 Wall HSPU", "duration": 40, "rest": 120},
            {"name": "The Century Gauntlet", "protocol": "For Time: 100 Push-ups, 50 Pull-ups, 100 Squats", "duration": 45, "rest": 60},
            {"name": "Deep Recovery & Mobility", "protocol": "30 Mins Hip Openers & Thoracic Mobility", "duration": 30, "rest": 0}
        ]
    }
}

# ==============================================================================
# 3. PAGE INITIALIZATION & HIGH-END ATHLETE DARK THEME
# ==============================================================================
st.set_page_config(page_title="Mero Suite — Executive Operating System", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0c1017; color: #f1f5f9; }
    
    .hero-header { font-size: 32px; font-weight: 800; color: #ffffff; line-height: 1.15; margin-bottom: 2px; }
    .hero-sub { color: #94a3b8; font-size: 14px; margin-bottom: 16px; }
    
    .kpi-card {
        background: #141a24;
        border: 1px solid #20293a;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 14px;
    }
    .kpi-val { font-size: 26px; font-weight: 800; color: #ffffff; margin-top: 4px; }
    .kpi-lbl { font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    
    .badge-pass { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #059669; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .badge-fail { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid #e11d48; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .badge-work { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. UNIFIED 5-BUTTON NAVIGATION MATRIX
# ==============================================================================
st.sidebar.markdown('### ⚡ MERO SUITE OS')
st.sidebar.markdown('<div style="background:#17202e; border:1px solid #253349; padding:6px 12px; border-radius:999px; font-size:12px; color:#cbd5e1; margin-bottom:15px;">🛡️ Operator: <b>Raju Maharjan</b></div>', unsafe_allow_html=True)

active_tab = st.sidebar.radio(
    "Domain Control Matrix",
    [
        "💎 Executive Dashboard",
        "💰 Finance & Ledger",
        "🎯 Operations & To-Do Lists",
        "🩺 Health & Wellness",
        "🤸 Calisthenics & Exercises"
    ]
)

conn = get_db()

# ==============================================================================
# MODULE 1: 💎 EXECUTIVE DASHBOARD (Shows Panoramic Results Across All Domains)
# ==============================================================================
if active_tab == "💎 Executive Dashboard":
    st.markdown('<p class="hero-header">Executive Command Cockpit</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Consolidated real-time operational status, net cash flow, and fitness telemetry.</p>', unsafe_allow_html=True)

    # 1. Financial KPI Computations
    total_income = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Income'").fetchone()[0]
    total_expense = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Expense'").fetchone()[0]
    net_cashflow = total_income - total_expense
    
    # 2. Operations & Task Computations
    active_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
    urgent_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed' AND priority LIKE '%Urgent%'").fetchone()[0]
    
    # 3. Health & Fitness Computations
    today_str = str(date.today())
    water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
    water_cups = water_row[0] if water_row else 0
    ch_state = conn.execute("SELECT current_day FROM challenge_state WHERE challenge_name = '30-Day Foundation Challenge'").fetchone()
    current_ch_day = ch_state[0] if ch_state else 1

    # TOP ROW: 4 MASTER KPIS
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        color = "#10b981" if net_cashflow >= 0 else "#f43f5e"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">Net Cash Flow (NPR)</div>
                <div class="kpi-val" style="color:{color};">Rs. {net_cashflow:,.2f}</div>
                <div style="font-size:12px; color:#94a3b8; margin-top:4px;">In: <b>+{total_income:,.0f}</b> | Out: <b>-{total_expense:,.0f}</b></div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">Active To-Do Operations</div>
                <div class="kpi-val" style="color:#38bdf8;">{active_tasks} <span style="font-size:14px; color:#94a3b8;">Pending</span></div>
                <div style="font-size:12px; color:#fb7185; margin-top:4px;">🚨 {urgent_tasks} Urgent Tasks Remaining</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">Daily Hydration</div>
                <div class="kpi-val" style="color:#60a5fa;">{water_cups} / 10 <span style="font-size:14px; color:#94a3b8;">Glasses</span></div>
                <div style="font-size:12px; color:#10b981; margin-top:4px;">Target: 2.5 Liters / Day</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">Active Calisthenics Level</div>
                <div class="kpi-val" style="color:#f59e0b;">Day {current_ch_day} <span style="font-size:14px; color:#94a3b8;">/ 30</span></div>
                <div style="font-size:12px; color:#38bdf8; margin-top:4px;">Crucible Progression Active</div>
            </div>
        """, unsafe_allow_html=True)

    # SECOND ROW: FINANCIAL & OPERATIONAL STREAMS
    col_f_chart, col_t_preview = st.columns([1.3, 1.2], gap="medium")
    
    with col_f_chart:
        with st.container(border=True):
            st.markdown("##### 📊 Cashflow Allocation Breakdown")
            df_expenses = pd.read_sql("SELECT category, SUM(amount) as total FROM transactions WHERE type = 'Expense' GROUP BY category ORDER BY total DESC LIMIT 6", conn)
            if not df_expenses.empty:
                chart = alt.Chart(df_expenses).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                    x=alt.X("category:N", sort="-y", title=None),
                    y=alt.Y("total:Q", title="NPR Spent"),
                    color=alt.Color("category:N", legend=None)
                ).properties(height=200)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No expenditures logged yet. Open 'Finance & Ledger' to add daily expenses.")

    with col_t_preview:
        with st.container(border=True):
            st.markdown("##### 📌 High-Priority Action Items")
            df_dash_tasks = pd.read_sql("SELECT id, title, category, priority, deadline FROM tasks WHERE status != 'Completed' ORDER BY id DESC LIMIT 4", conn)
            if not df_dash_tasks.empty:
                for _, t in df_dash_tasks.iterrows():
                    st.markdown(f"""
                        <div style="background:#131822; padding:10px 14px; border-radius:10px; margin-bottom:8px; border:1px solid #1e2638; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <b style="color:#ffffff; font-size:14px;">{t['title']}</b>
                                <div style="color:#94a3b8; font-size:12px; margin-top:2px;">{t['category']} | Target: {t['deadline']}</div>
                            </div>
                            <span class="badge-work">{t['priority']}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 All operational objectives cleared!")

# ==============================================================================
# MODULE 2: 💰 FINANCE & LEDGER (Full Daily Options, Income & Expense)
# ==============================================================================
elif active_tab == "💰 Finance & Ledger":
    st.markdown('<p class="hero-header">Financial Ledger & Capital Management</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Full daily options for income streams, personal & business expenses, and automated cashflow analysis.</p>', unsafe_allow_html=True)

    col_entry, col_overview = st.columns([1.1, 1.4], gap="medium")

    with col_entry:
        with st.container(border=True):
            st.markdown("#### ➕ Record Transaction")
            
            t_type = st.radio("Transaction Type", ["Expense", "Income"], horizontal=True)

            with st.form("tx_entry_form", clear_on_submit=True):
                t_date = st.date_input("Accounting Date", date.today())
                
                # Dynamic options tailored for daily life and work
                if t_type == "Expense":
                    cat_options = [
                        "Food & Groceries", "Dining Out & Cafes", "Rent & Housing", 
                        "Electricity & Water", "Internet & Mobile", "Fuel & Vehicle Service", 
                        "Public Ride (Pathao/Indrive)", "Shopping & Clothing", "Software & Tools", 
                        "Medical & Healthcare", "Education & Books", "Family & Remittance", 
                        "Entertainment & Travel", "EMI & Loan Repayment", "General Miscellaneous"
                    ]
                    entity_label = "Merchant / Vendor Name"
                    entity_ph = "e.g. Bhatbhateni, Local Mart, Landlord"
                else:
                    cat_options = [
                        "Salary & Wages", "Freelance / Consulting", "Business Sales & Profit", 
                        "Client Retainer", "Investments & Dividends", "Rental Income", 
                        "Gift / Reimbursement", "Refund / Cashback"
                    ]
                    entity_label = "Source / Payer"
                    entity_ph = "e.g. Employer, Client Name, Tenant"

                t_cat = st.selectbox("Category", cat_options)
                t_entity = st.text_input(entity_label, placeholder=entity_ph)
                t_desc = st.text_input("Item Description / Memo", placeholder="e.g. Weekly vegetable haul, Client invoice #102")
                t_amount = st.number_input("Amount (NPR)", min_value=1.0, step=100.0, value=500.0)
                
                payment_methods = ["QR Pay (Fonepay/eSewa)", "eSewa / Khalti Wallet", "Bank Transfer (ConnectIPS)", "Cash Settlement", "Credit / Debit Card", "Cheque"]
                t_method = st.selectbox("Payment Channel", payment_methods)
                t_notes = st.text_input("Additional Notes", placeholder="Optional reference or invoice number")

                if st.form_submit_button(f"Commit {t_type} to Ledger", type="primary", use_container_width=True):
                    with conn:
                        conn.execute("""
                            INSERT INTO transactions (date, type, entity, description, amount, category, payment_method, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (str(t_date), t_type, t_entity.strip() or "Standard", t_desc.strip(), t_amount, t_cat, t_method, t_notes.strip()))
                    st.toast(f"Logged Rs. {t_amount:,.2f} under {t_cat}!", icon="💾")
                    st.rerun()

    with col_overview:
        with st.container(border=True):
            st.markdown("#### 📋 Transaction History & Ledger")
            df_tx = pd.read_sql("SELECT id, date, type, category, entity, description, amount, payment_method FROM transactions ORDER BY id DESC", conn)
            
            if not df_tx.empty:
                # Filter Controls
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    filter_type = st.selectbox("Filter Type", ["All Transactions", "Expenses Only", "Income Only"])
                with col_f2:
                    filter_cat = st.selectbox("Filter Category", ["All Categories"] + sorted(df_tx['category'].unique().tolist()))

                df_filtered = df_tx.copy()
                if filter_type == "Expenses Only": df_filtered = df_filtered[df_filtered['type'] == 'Expense']
                elif filter_type == "Income Only": df_filtered = df_filtered[df_filtered['type'] == 'Income']
                if filter_cat != "All Categories": df_filtered = df_filtered[df_filtered['category'] == filter_cat]

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)

                # Quick Delete
                with st.expander("🗑️ Delete / Manage Record"):
                    del_id = st.selectbox("Select Transaction ID to Delete", df_filtered["id"].tolist())
                    if st.button("Delete Selected Transaction", use_container_width=True):
                        with conn:
                            conn.execute("DELETE FROM transactions WHERE id = ?", (del_id,))
                        st.toast(f"Transaction #{del_id} removed!")
                        st.rerun()

                csv_data = df_tx.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Full Ledger to CSV", data=csv_data, file_name="mero_financial_ledger.csv", mime="text/csv")
            else:
                st.info("Your ledger is currently clean. Add transactions on the left.")

# ==============================================================================
# MODULE 3: 🎯 OPERATIONS & TO-DO LISTS (Daily Life, Work, Errands & Matrix)
# ==============================================================================
elif active_tab == "🎯 Operations & To-Do Lists":
    st.markdown('<p class="hero-header">Operations Engine & Daily To-Do Lists</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Organize your daily work objectives, personal errands, study sessions, and operational workflows.</p>', unsafe_allow_html=True)

    col_t_create, col_t_board = st.columns([1.1, 1.4], gap="medium")

    with col_t_create:
        with st.container(border=True):
            st.markdown("#### ➕ Create New Objective")
            with st.form("new_task_form", clear_on_submit=True):
                t_title = st.text_input("Task Objective / Name", placeholder="e.g. Submit Q3 VAT reconciliation, Call plumber")
                
                t_category = st.selectbox(
                    "Operational Domain",
                    ["💼 Work & Client Projects", "🏠 Personal & Home", "💳 Finance & Bills", "🛒 Errands & Shopping", "📚 Growth & Learning", "🩺 Health & Medical"]
                )
                
                c_p, c_d = st.columns(2)
                with c_p:
                    t_priority = st.selectbox("Priority Matrix", ["🔴 Urgent / Critical", "🟡 Medium / Normal", "🔵 Low / Backlog"])
                with c_d:
                    t_deadline = st.date_input("Target Due Date", date.today())

                if st.form_submit_button("Deploy Task to Queue", type="primary", use_container_width=True):
                    if t_title.strip():
                        with conn:
                            conn.execute("""
                                INSERT INTO tasks (title, category, priority, deadline, status, created_date)
                                VALUES (?, ?, ?, ?, 'Pending', ?)
                            """, (t_title.strip(), t_category, t_priority, str(t_deadline), str(date.today())))
                        st.toast(f"Task '{t_title}' queued!", icon="🚀")
                        st.rerun()
                    else:
                        st.error("Please provide a task title.")

    with col_t_board:
        with st.container(border=True):
            st.markdown("#### 📋 Active Operational Queue")
            df_tasks = pd.read_sql("SELECT * FROM tasks ORDER BY id DESC", conn)

            if not df_tasks.empty:
                tab_active, tab_completed = st.tabs(["Active Operations", "Archive / Completed"])
                
                with tab_active:
                    active_items = df_tasks[df_tasks['status'] != 'Completed']
                    if not active_items.empty:
                        for _, row in active_items.iterrows():
                            c_box, c_info, c_action = st.columns([0.15, 0.75, 0.2])
                            with c_info:
                                st.markdown(f"**{row['title']}**")
                                st.caption(f"{row['category']} | Due: {row['deadline']} | {row['priority']}")
                            with c_action:
                                if st.button("✅ Done", key=f"done_{row['id']}"):
                                    with conn:
                                        conn.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (row['id'],))
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.success("🎉 No active pending tasks! Everything is completed.")

                with tab_completed:
                    done_items = df_tasks[df_tasks['status'] == 'Completed']
                    if not done_items.empty:
                        st.dataframe(done_items[["title", "category", "deadline", "priority"]], use_container_width=True, hide_index=True)
                        if st.button("🗑️ Clear Completed Archive", use_container_width=True):
                            with conn:
                                conn.execute("DELETE FROM tasks WHERE status = 'Completed'")
                            st.rerun()
                    else:
                        st.info("No completed tasks in archive.")
            else:
                st.info("No tasks created yet. Schedule your first task on the left.")

# ==============================================================================
# MODULE 4: 🩺 HEALTH & WELLNESS (All Health, Vitals, Glucose, BP & Hydration)
# ==============================================================================
elif active_tab == "🩺 Health & Wellness":
    col_hero, col_chips = st.columns([1.5, 1])
    with col_hero:
        st.markdown('''
            <div>
                <p class="hero-header">Stay Healthy<br>Keep Body <span style="background:#2563eb; color:white; padding:2px 14px; border-radius:999px;">Strong</span></p>
                <p class="hero-sub">Biometric telemetry, cellular hydration, and cardiovascular analytics.</p>
            </div>
        ''', unsafe_allow_html=True)
    with col_chips:
        st.markdown('''
            <div style="text-align: right; padding-top: 10px;">
                <span style="background:#1c2434; border:1px solid #2a374f; padding:6px 12px; border-radius:999px; font-size:12px;">🔥 2,480 Kcal</span>
                <span style="background:#1c2434; border:1px solid #2a374f; padding:6px 12px; border-radius:999px; font-size:12px;">❤️ 110 bpm</span>
                <span style="background:#1c2434; border:1px solid #2a374f; padding:6px 12px; border-radius:999px; font-size:12px;">⚡ HRV 54</span>
            </div>
        ''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('''
            <div class="kpi-card">
                <div class="kpi-lbl">PULSE RATE MONITOR</div>
                <div class="kpi-val">110 <span style="font-size:14px; color:#94a3b8;">BPM</span></div>
                <div style="color:#38bdf8; font-size:11px; margin-top:4px;">✓ Need to keep balance</div>
            </div>
        ''', unsafe_allow_html=True)
        pulse_df = pd.DataFrame({"Time": ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"], "BPM": [65, 82, 110, 95, 128, 74]})
        st.altair_chart(alt.Chart(pulse_df).mark_line(color="#38bdf8", strokeWidth=3).encode(x="Time:N", y=alt.Y("BPM:Q", scale=alt.Scale(domain=[50, 140]))).properties(height=110), use_container_width=True)

    with c2:
        st.markdown('''
            <div class="kpi-card">
                <div class="kpi-lbl">GLUCOSE RESULTS (WEEKLY)</div>
                <div class="kpi-val">120.00 <span style="font-size:14px; color:#94a3b8;">Avg. mg/dl</span></div>
                <div style="color:#10b981; font-size:11px; margin-top:4px;">Optimal Target Range</div>
            </div>
        ''', unsafe_allow_html=True)
        glucose_df = pd.DataFrame({
            "Day": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "Level": [95, 105, 110, 100, 85, 115, 102],
            "Color": ["#25334d", "#25334d", "#25334d", "#25334d", "#3b82f6", "#25334d", "#25334d"]
        })
        st.altair_chart(alt.Chart(glucose_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x="Day:N", y="Level:Q", color=alt.Color("Color:N", scale=None)).properties(height=110), use_container_width=True)

    with c3:
        st.markdown('''
            <div class="kpi-card">
                <div class="kpi-lbl">CARDIOVASCULAR VITALS</div>
                <div style="display:flex; justify-content:space-between; margin-top:8px;">
                    <div><span style="font-size:11px; color:#64748b;">GLYCATED SUGAR</span><br><b style="font-size:20px;">120 HbA1c</b></div>
                    <div><span style="font-size:11px; color:#64748b;">BLOOD PRESSURE</span><br><b style="font-size:20px; color:#38bdf8;">104 mmHg</b></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        today_str = str(date.today())
        water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
        cur_w = water_row[0] if water_row else 2
        with st.container(border=True):
            st.markdown(f"**💧 Hydration**: `{cur_w} / 10 Glasses` (2.5L)")
            st.progress(min(cur_w / 10.0, 1.0))
            colw1, colw2 = st.columns(2)
            with colw1:
                if st.button("➕ +250ml Glass", use_container_width=True):
                    with conn:
                        conn.execute("INSERT INTO daily_water (date, cups) VALUES (?, 1) ON CONFLICT(date) DO UPDATE SET cups = cups + 1", (today_str,))
                    st.rerun()
            with colw2:
                if st.button("➖ Remove Glass", use_container_width=True):
                    if cur_w > 0:
                        with conn:
                            conn.execute("UPDATE daily_water SET cups = cups - 1 WHERE date = ?", (today_str,))
                        st.rerun()

# ==============================================================================
# MODULE 5: 🤸 CALISTHENICS & EXERCISES (Codex, Logger, 30/90 Challenges, Videos)
# ==============================================================================
elif active_tab == "🤸 Calisthenics & Exercises":
    st.markdown('<p class="hero-header">Calisthenics & Athletic Training Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Complete calisthenics skill codex, daily sets/reps logger, and adaptive 30/90 days challenges.</p>', unsafe_allow_html=True)

    c_sub1, c_sub2, c_sub3 = st.tabs([
        "🏋️ Daily Sets/Reps Performance Logger",
        "🏆 30 / 90 Days Adaptive Challenges",
        "📋 Exercise Standards & Free Video Codex"
    ])

    # SUB-TAB 1: DAILY PERFORMANCE LOGGER
    with c_sub1:
        col_l1, col_l2 = st.columns([1.1, 1.4], gap="medium")
        with col_l1:
            with st.container(border=True):
                st.markdown("#### ⚡ Log Performance Set")
                chosen_ex = st.selectbox("Select Target Exercise", list(EXERCISE_STANDARDS.keys()))
                default_spec = EXERCISE_STANDARDS[chosen_ex]

                with st.form("exercise_logging_form"):
                    e_date = st.date_input("Training Date", date.today())
                    st.info(f"💡 Standard Prescription: **{default_spec['sets']} Sets** × **{default_spec['reps']} Reps** | **{default_spec['rest_sec']}s Rest** | **~{default_spec['duration_min']}m Duration**")

                    c1, c2 = st.columns(2)
                    with c1:
                        completed_sets = st.number_input("Completed Sets", min_value=1, max_value=15, value=default_spec['sets'])
                        completed_reps = st.number_input("Completed Reps / Sec", min_value=0, max_value=250, value=default_spec['reps'])
                    with c2:
                        actual_dur = st.number_input("Duration (Mins)", min_value=1, max_value=120, value=default_spec['duration_min'])
                        actual_rest = st.number_input("Rest Taken (Sec)", min_value=10, max_value=300, step=5, value=default_spec['rest_sec'])

                    added_weight = st.number_input("Added Weight / Vest (kg)", min_value=0.0, step=2.5, value=0.0)
                    outcome_status = st.radio("Protocol Outcome", ["Successfully Done (Pass)", "Failed / Form Breakdown (Incomplete)"], horizontal=True)
                    notes = st.text_input("Execution Notes", placeholder="e.g. Crisp lockout, struggled on 4th set")

                    if st.form_submit_button("Commit Exercise Entry", type="primary", use_container_width=True):
                        status_clean = "Success" if "Successfully" in outcome_status else "Failed"
                        with conn:
                            conn.execute("""
                                INSERT INTO exercise_logs (date, exercise_name, tier, target_sets, completed_sets, target_reps, completed_reps, duration_min, rest_sec, weight_added, status, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (str(e_date), chosen_ex, default_spec['tier'], default_spec['sets'], completed_sets, default_spec['reps'], completed_reps, actual_dur, actual_rest, added_weight, status_clean, notes))
                        st.toast(f"Logged {chosen_ex}!", icon="💪")
                        st.rerun()

        with col_l2:
            with st.container(border=True):
                st.markdown("#### 📋 Performance Feed")
                df_logs = pd.read_sql("SELECT * FROM exercise_logs ORDER BY id DESC LIMIT 10", conn)
                if not df_logs.empty:
                    success_count = len(df_logs[df_logs['status'] == 'Success'])
                    total_count = len(df_logs)
                    st.metric("Protocol Pass Rate", f"{int(success_count / total_count * 100)}%", f"{success_count}/{total_count} Passed")

                    for _, r in df_logs.iterrows():
                        badge = '<span class="badge-pass">✓ SUCCESS</span>' if r['status'] == 'Success' else '<span class="badge-fail">✕ FAILED</span>'
                        st.markdown(f"""
                            <div style="background:#131822; padding:10px 12px; border-radius:10px; margin-bottom:8px; border:1px solid #1e2638;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <b style="color:#ffffff;">{r['exercise_name']}</b> {badge}
                                </div>
                                <div style="color:#94a3b8; font-size:12px; margin-top:3px;">
                                    Sets: <b>{r['completed_sets']}/{r['target_sets']}</b> | Reps: <b>{r['completed_reps']}/{r['target_reps']}</b> | Rest: <b>{r['rest_sec']}s</b> | Load: <b>{r['weight_added']}kg</b>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No exercise logs recorded yet.")

    # SUB-TAB 2: 30 / 90 DAYS ADAPTIVE CHALLENGES
    with c_sub2:
        selected_ch = st.radio("Choose Track", list(CHALLENGE_SPECS.keys()), horizontal=True)
        spec = CHALLENGE_SPECS[selected_ch]
        total_days = spec["days"]
        blueprint = spec["blueprint"]

        state = conn.execute("SELECT current_day, retries_count FROM challenge_state WHERE challenge_name = ?", (selected_ch,)).fetchone()
        cur_day = state["current_day"] if state else 1
        retries = state["retries_count"] if state else 0
        workout = blueprint[(cur_day - 1) % len(blueprint)]

        cm1, cm2, cm3 = st.columns(3)
        with cm1: st.metric("Active Day", f"Day {cur_day} / {total_days}")
        with cm2: st.metric("Overall Completion", f"{int((cur_day - 1) / total_days * 100)}%")
        with cm3: st.metric("Failure Retries", f"{retries} Attempts")

        st.progress(min((cur_day - 1) / float(total_days), 1.0))

        col_ch_entry, col_ch_hist = st.columns([1.2, 1.3], gap="medium")
        with col_ch_entry:
            with st.container(border=True):
                st.markdown(f"### 🎯 Day {cur_day}: {workout['name']}")
                st.warning(f"⚡ **Prescribed Routine:** {workout['protocol']}")
                st.caption(f"⏱️ Target Duration: {workout['duration']} mins | 🛑 Prescribed Rest: {workout['rest']} sec")

                with st.form("challenge_sub_form"):
                    s_done = st.number_input("Sets Done", min_value=1, max_value=20, value=4)
                    r_done = st.number_input("Reps Done", min_value=1, max_value=300, value=40)
                    d_done = st.number_input("Actual Duration (Mins)", min_value=5, max_value=180, value=workout['duration'])
                    rest_done = st.number_input("Actual Rest Taken (Sec)", min_value=0, max_value=300, value=workout['rest'])

                    ch_outcome = st.radio("Result", ["🟢 Successfully Done (Advance to Next Day)", "🔴 Failed / Incomplete (Repeat Day Again)"])
                    ch_notes = st.text_input("Session Notes", placeholder="e.g. Cleared all sets")

                    if st.form_submit_button("Submit Challenge Session", type="primary", use_container_width=True):
                        is_pass = "Successfully" in ch_outcome
                        with conn:
                            conn.execute("""
                                INSERT INTO challenge_logs (challenge_name, day_number, date, completed_sets, completed_reps, actual_duration_min, actual_rest_sec, status, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (selected_ch, cur_day, str(date.today()), s_done, r_done, d_done, rest_done, "Success" if is_pass else "Failed", ch_notes))

                        if is_pass:
                            if cur_day < total_days:
                                with conn:
                                    conn.execute("UPDATE challenge_state SET current_day = ? WHERE challenge_name = ?", (cur_day + 1, selected_ch))
                                st.balloons()
                                st.success(f"🎉 Day {cur_day} Conquered! Unlocked Day {cur_day + 1}!")
                            else:
                                st.balloons()
                                st.success("🏆 You conquered the entire challenge!")
                        else:
                            with conn:
                                conn.execute("UPDATE challenge_state SET retries_count = retries_count + 1 WHERE challenge_name = ?", (selected_ch,))
                            st.error(f"⚠️ You must REPEAT Day {cur_day} until mastered!")
                        st.rerun()

        with col_ch_hist:
            with st.container(border=True):
                st.markdown("#### 📜 Attempt Audit")
                df_ch_hist = pd.read_sql("SELECT * FROM challenge_logs WHERE challenge_name = ? ORDER BY id DESC LIMIT 10", conn, params=(selected_ch,))
                if not df_ch_hist.empty:
                    for _, r in df_ch_hist.iterrows():
                        badge = '<span class="badge-pass">✓ PASSED</span>' if r['status'] == 'Success' else '<span class="badge-fail">✕ FAILED (REPEAT)</span>'
                        st.markdown(f"""
                            <div style="background:#131822; padding:10px 12px; border-radius:10px; margin-bottom:6px; border:1px solid #1e2638;">
                                <div style="display:flex; justify-content:space-between;">
                                    <b>Day {r['day_number']} Attempt</b> {badge}
                                </div>
                                <div style="color:#94a3b8; font-size:12px; margin-top:2px;">Sets: {r['completed_sets']} | Reps: {r['completed_reps']} | Rest: {r['actual_rest_sec']}s | {r['date']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No attempts recorded yet for this challenge.")

    # SUB-TAB 3: CODEX & VIDEOS
    with c_sub3:
        st.markdown("#### 🎬 Verified Free Video Codex")
        v_tier = st.selectbox("Filter Tier", ["All Tiers", "Beginner", "Intermediate", "Advanced"])
        v_cols = st.columns(2)
        idx = 0
        for title, data in CALISTHENICS_VIDEOS.items():
            if v_tier == "All Tiers" or data["tier"] == v_tier:
                with v_cols[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"**{title}** (`{data['coach']}`)")
                        st.video(data["url"])
                idx += 1
