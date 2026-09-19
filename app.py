import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from datetime import datetime, date, timedelta

# ==============================================================================
# 1. PERSISTENCE ENGINE & AUTOMATIC MIGRATION (SQLite)
# ==============================================================================
DB_FILE = "mero_app.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        
        # Unified Transactions (Income & Expense)
        c.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                entity TEXT,
                description TEXT,
                amount REAL,
                category TEXT,
                payment_method TEXT,
                notes TEXT
            )
        """)
        
        # Backward compatibility migration from old 'expenses' table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        if c.fetchone():
            count_tx = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            if count_tx == 0:
                c.execute("""
                    INSERT INTO transactions (date, type, entity, description, amount, category, payment_method, notes)
                    SELECT date, 'Expense', shop, items, amount, main_category, payment_method, sub_category FROM expenses
                """)

        # Operations & Daily To-Dos
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
        
        # Daily Hydration
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_water (
                date TEXT PRIMARY KEY,
                cups INTEGER
            )
        """)
        
        # Exercise Logs
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
        
        # Challenge Adaptive Engine
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
# 2. CALISTHENICS REPOSITORY & STANDARDS DATA
# ==============================================================================
EXERCISE_STANDARDS = {
    "Wall / Incline Push-Ups": {"tier": "Beginner", "sets": 3, "reps": 12, "duration_min": 15, "rest_sec": 60, "cue": "Plank line, elbows at 45°"},
    "Scapular Pulls & Dead Hang": {"tier": "Beginner", "sets": 3, "reps": 30, "duration_min": 12, "rest_sec": 60, "cue": "Depress scapula, active shoulders"},
    "Incline Australian Rows": {"tier": "Beginner", "sets": 3, "reps": 10, "duration_min": 15, "rest_sec": 60, "cue": "Straight body, pull chest to bar"},
    "Bodyweight Deep Squats": {"tier": "Beginner", "sets": 3, "reps": 15, "duration_min": 15, "rest_sec": 60, "cue": "Heels planted, knees over toes"},
    "Plank & Hollow Body Hold": {"tier": "Beginner", "sets": 3, "reps": 45, "duration_min": 12, "rest_sec": 45, "cue": "Posterior pelvic tilt, tight glutes"},
    "Strict Standard Push-Ups": {"tier": "Intermediate", "sets": 4, "reps": 15, "duration_min": 20, "rest_sec": 90, "cue": "Chest touches deck, full lockout"},
    "Parallel Bar Dips": {"tier": "Intermediate", "sets": 4, "reps": 10, "duration_min": 25, "rest_sec": 90, "cue": "Lower to 90°, slight forward torso lean"},
    "Strict Hollow Pull-Ups": {"tier": "Intermediate", "sets": 4, "reps": 8, "duration_min": 25, "rest_sec": 90, "cue": "Dead hang to chin clearing bar"},
    "Pike Push-Ups (Elevated)": {"tier": "Intermediate", "sets": 4, "reps": 8, "duration_min": 20, "rest_sec": 90, "cue": "Hips elevated, head tracks into tripod"},
    "Parallel Bar / Floor L-Sit": {"tier": "Intermediate", "sets": 4, "reps": 15, "duration_min": 18, "rest_sec": 75, "cue": "Push floor away, locked knees"},
    "Bar Muscle-Up": {"tier": "Advanced", "sets": 5, "reps": 4, "duration_min": 30, "rest_sec": 120, "cue": "Explosive pull to chest, rapid wrist snap"},
    "Handstand Push-Ups (Wall)": {"tier": "Advanced", "sets": 4, "reps": 6, "duration_min": 30, "rest_sec": 120, "cue": "Belly facing wall, controlled descent"},
    "Front Lever (Tuck/Full)": {"tier": "Advanced", "sets": 5, "reps": 8, "duration_min": 25, "rest_sec": 120, "cue": "Locked arms, pull bar down towards hips"},
    "Full Planche Progression": {"tier": "Advanced", "sets": 5, "reps": 10, "duration_min": 25, "rest_sec": 120, "cue": "Protracted scapula, extreme forward lean"}
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
            {"name": "Upper Body Push", "protocol": "4 Sets × 12 Incline/Floor Push-Ups", "duration": 25, "rest": 60},
            {"name": "Upper Body Pull", "protocol": "4 Sets × 8 Australian Rows + 30s Dead Hang", "duration": 25, "rest": 60},
            {"name": "Core & Compression", "protocol": "4 Sets × 45s Plank + 3x15 Hollow Tucks", "duration": 20, "rest": 45},
            {"name": "Leg Engine & Stability", "protocol": "4 Sets × 15 Deep Squats + 3x12 Lunges", "duration": 25, "rest": 60},
            {"name": "Full Body Circuit", "protocol": "3 Rounds: 10 Push-Ups, 8 Rows, 15 Squats, 30s Plank", "duration": 30, "rest": 75},
            {"name": "Active Mobility", "protocol": "20 Mins Shoulder Dislocates & Wrist Mobility", "duration": 20, "rest": 30},
            {"name": "Complete Rest Day", "protocol": "Hydration, Nutrition & Sleep Rebalance", "duration": 10, "rest": 0}
        ]
    },
    "90-Day Elite Beast Challenge": {
        "days": 90,
        "blueprint": [
            {"name": "Explosive Pull Force", "protocol": "5 Sets × 6 Strict Pull-Ups + 4x8 Archer Rows", "duration": 35, "rest": 90},
            {"name": "Overhead & Heavy Dips", "protocol": "5 Sets × 10 Deep Dips + 4x6 Elevated Pike Push-Ups", "duration": 35, "rest": 90},
            {"name": "Static Lever & Core", "protocol": "5 Sets × 15s L-Sit Hold + 4x8 Hanging Leg Raises", "duration": 30, "rest": 75},
            {"name": "Pistol & Unilateral Legs", "protocol": "4 Sets × 6 Pistol Squats each leg + 4x10 Jump Squats", "duration": 35, "rest": 90},
            {"name": "Acrobatic Skill Work", "protocol": "5 Sets × 3 Muscle-Up Transitions + 4x5 Wall HSPU", "duration": 40, "rest": 120},
            {"name": "The Century Gauntlet", "protocol": "100 Push-ups, 50 Pull-ups, 100 Squats for time", "duration": 45, "rest": 60},
            {"name": "Deep Tissue Restoration", "protocol": "30 Mins Hip Openers & Contrast Therapy", "duration": 30, "rest": 0}
        ]
    }
}

# ==============================================================================
# 3. PAGE INITIALIZATION & LUXURY DARK UI
# ==============================================================================
st.set_page_config(
    page_title="MERO OS — Executive Command Suite", 
    layout="wide", 
    page_icon="💎",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0b0f17; color: #f1f5f9; }
    
    .dash-hero-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 2px;
    }
    
    .dash-pill {
        background: linear-gradient(135deg, #2563eb, #38bdf8);
        color: #ffffff;
        padding: 4px 14px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 13px;
        display: inline-block;
    }
    
    .kpi-card {
        background: #141b27;
        border: 1px solid #202b3c;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.35);
        margin-bottom: 12px;
    }
    .kpi-lbl {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-val {
        font-size: 28px;
        font-weight: 800;
        margin-top: 4px;
    }
    
    .badge-success-tag {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
    }
    .badge-fail-tag {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #e11d48;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SIDEBAR NAVIGATION (THE 5 CORE HUBS)
# ==============================================================================
st.sidebar.markdown('### 💎 MERO EXECUTIVE OS')
st.sidebar.markdown('<span style="background:#1e293b; color:#38bdf8; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700;">Operator: Raju Maharjan</span>', unsafe_allow_html=True)
st.sidebar.write("")

# 5 Hub Buttons exactly as requested:
active_tab = st.sidebar.radio(
    "Control Matrix",
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
# HUB 1: EXECUTIVE DASHBOARD (ALL RESULTS & PANORAMIC TELEMETRY)
# ==============================================================================
if active_tab == "💎 Executive Dashboard":
    st.markdown('''
        <div style="margin-bottom:15px;">
            <span class="dash-pill">SYSTEM STATUS: OPTIMAL</span>
            <p class="dash-hero-title">Executive Command Dashboard</p>
            <p style="color:#64748b; font-size:14px; margin-top:-2px;">Consolidated analytics across cashflow, operations, cellular vitality, and athletic conditioning.</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Financial KPI Computations
    total_income = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Income'").fetchone()[0]
    total_expense = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'Expense'").fetchone()[0]
    net_cashflow = total_income - total_expense
    
    # Task KPI Computations
    pending_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed'").fetchone()[0]
    urgent_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Completed' AND priority LIKE '%Urgent%'").fetchone()[0]
    
    # Wellness & Water Computations
    today_str = str(date.today())
    water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
    water_cups = water_row[0] if water_row else 0
    
    # Calisthenics Challenge State
    ch_state = conn.execute("SELECT current_day, retries_count FROM challenge_state WHERE challenge_name = '30-Day Foundation Challenge'").fetchone()
    ch_day = ch_state[0] if ch_state else 1
    ch_retries = ch_state[1] if ch_state else 0

    # 4-Column Hero KPI Strip
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        color_cash = "#34d399" if net_cashflow >= 0 else "#fb7185"
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-lbl">Net Liquid Balance</div>
                <div class="kpi-val" style="color:{color_cash};">NPR {net_cashflow:,.2f}</div>
                <div style="font-size:11px; color:#94a3b8; margin-top:4px;">In: NPR {total_income:,.0f} | Out: NPR {total_expense:,.0f}</div>
            </div>
        ''', unsafe_allow_html=True)
    with k2:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-lbl">Active Operations & Tasks</div>
                <div class="kpi-val" style="color:#38bdf8;">{pending_tasks} Pending</div>
                <div style="font-size:11px; color:#fb7185; margin-top:4px;">🚨 {urgent_tasks} High Priority / Urgent</div>
            </div>
        ''', unsafe_allow_html=True)
    with k3:
        water_pct = int(min(water_cups / 10.0, 1.0) * 100)
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-lbl">Hydration & Vitals</div>
                <div class="kpi-val" style="color:#60a5fa;">{water_cups}/10 Glasses</div>
                <div style="font-size:11px; color:#10b981; margin-top:4px;">💧 {water_pct}% Daily Target Met</div>
            </div>
        ''', unsafe_allow_html=True)
    with k4:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-lbl">Calisthenics Crucible</div>
                <div class="kpi-val" style="color:#a78bfa;">Day {ch_day} <span style="font-size:15px; color:#64748b;">/ 30</span></div>
                <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">🔄 {ch_retries} Retries Logged</div>
            </div>
        ''', unsafe_allow_html=True)

    st.write("")
    
    # Midsection Charts & Action Items
    col_dash_left, col_dash_right = st.columns([1.3, 1.2], gap="medium")
    
    with col_dash_left:
        with st.container(border=True):
            st.markdown("##### 📊 Cashflow Dynamics (Income vs Expense)")
            df_tx_summary = pd.read_sql("SELECT type, SUM(amount) as total FROM transactions GROUP BY type", conn)
            if not df_tx_summary.empty:
                chart_cf = alt.Chart(df_tx_summary).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                    x=alt.X("type:N", title=None),
                    y=alt.Y("total:Q", title="Total Amount (NPR)"),
                    color=alt.Color("type:N", scale=alt.Scale(domain=["Income", "Expense"], range=["#10b981", "#f43f5e"]), legend=None)
                ).properties(height=180)
                st.altair_chart(chart_cf, use_container_width=True)
            else:
                st.info("No transaction records available yet. Add income/expense in Finance & Ledger.")
                
        with st.container(border=True):
            st.markdown("##### 📌 High Priority Operational Objectives")
            df_urgent = pd.read_sql("SELECT title, category, deadline FROM tasks WHERE status != 'Completed' ORDER BY id DESC LIMIT 5", conn)
            if not df_urgent.empty:
                st.dataframe(df_urgent, use_container_width=True, hide_index=True)
            else:
                st.success("✓ All high priority operational tasks are completed!")

    with col_dash_right:
        with st.container(border=True):
            st.markdown("##### 🩺 Cardiovascular & Vitals Snapshot")
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown("**Pulse Monitor:** `110 BPM`")
                st.markdown("**Blood Pressure:** `104/70 mmHg`")
            with c_v2:
                st.markdown("**Glucose Avg:** `120 mg/dl`")
                st.markdown("**HbA1c:** `5.4%`")
            
            # Mini Sparkline
            pulse_df = pd.DataFrame({"Time": ["6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM"], "BPM": [62, 85, 110, 94, 125, 75]})
            spark = alt.Chart(pulse_d
