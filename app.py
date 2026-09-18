import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from datetime import datetime, date, timedelta

# ==============================================================================
# 1. PERSISTENCE ENGINE (SQLite)
# ==============================================================================
DB_FILE = "mero_app.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # Expenses Ledger
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, shop TEXT, items TEXT, amount REAL,
                payment_method TEXT, main_category TEXT, sub_category TEXT
            )
        """)
        # Tasks & Operations
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, deadline TEXT, client TEXT, priority TEXT, status TEXT
            )
        """)
        # Hydration
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_water (
                date TEXT PRIMARY KEY, cups INTEGER
            )
        """)
        # Exercise Performance Logs
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
        # Challenge Session Logs
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
        # Seed challenge state if empty
        for ch in ["30-Day Foundation Challenge", "90-Day Elite Beast Challenge"]:
            c.execute("INSERT OR IGNORE INTO challenge_state (challenge_name, current_day, retries_count) VALUES (?, 1, 0)", (ch,))
        conn.commit()

init_db()

# ==============================================================================
# 2. RESEARCHED EXERCISE REFERENCE DATABASE (BEGINNER TO ADVANCED)
# ==============================================================================
# Standards compiled from Reddit Recommended Routine, Thenx, and Caliverse
EXERCISE_STANDARDS = {
    # BEGINNER
    "Wall / Incline Push-Ups": {"tier": "Beginner", "category": "Push", "sets": 3, "reps": 12, "duration_min": 15, "rest_sec": 60, "cue": "Straight plank line, elbows 45°"},
    "Scapular Pulls & Dead Hang": {"tier": "Beginner", "category": "Pull", "sets": 3, "reps": 30, "duration_min": 12, "rest_sec": 60, "cue": "Depress shoulder blades without bending elbows"},
    "Incline Australian Rows": {"tier": "Beginner", "category": "Pull", "sets": 3, "reps": 10, "duration_min": 15, "rest_sec": 60, "cue": "Chest to bar, body straight at 45°"},
    "Bodyweight Deep Squats": {"tier": "Beginner", "category": "Legs", "sets": 3, "reps": 15, "duration_min": 15, "rest_sec": 60, "cue": "Heels flat, knees tracking over toes"},
    "Plank & Hollow Body Hold": {"tier": "Beginner", "category": "Core", "sets": 3, "reps": 45, "duration_min": 12, "rest_sec": 45, "cue": "Posterior pelvic tilt, dome upper back"},
    
    # INTERMEDIATE
    "Strict Standard Push-Ups": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 15, "duration_min": 20, "rest_sec": 90, "cue": "Full chest-to-deck, lockout at top"},
    "Parallel Bar Dips": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 10, "duration_min": 25, "rest_sec": 90, "cue": "Elbows at 90°, slight forward torso lean"},
    "Strict Hollow Pull-Ups": {"tier": "Intermediate", "category": "Pull", "sets": 4, "reps": 8, "duration_min": 25, "rest_sec": 90, "cue": "Chin clears bar, no swinging or kipping"},
    "Pike Push-Ups (Elevated)": {"tier": "Intermediate", "category": "Push", "sets": 4, "reps": 8, "duration_min": 20, "rest_sec": 90, "cue": "Hips high, head tracks forward into tripod"},
    "Parallel Bar / Floor L-Sit": {"tier": "Intermediate", "category": "Core", "sets": 4, "reps": 15, "duration_min": 18, "rest_sec": 75, "cue": "Depress shoulders, locked knees, pointed toes"},
    "Bulgarian Split Squats": {"tier": "Intermediate", "category": "Legs", "sets": 4, "reps": 12, "duration_min": 20, "rest_sec": 60, "cue": "Rear foot elevated, deep controlled lunge"},

    # ADVANCED
    "Bar Muscle-Up": {"tier": "Advanced", "category": "Pull/Push", "sets": 5, "reps": 4, "duration_min": 30, "rest_sec": 120, "cue": "Explosive pull to sternum, rapid wrist snap, press up"},
    "Handstand Push-Ups (Wall)": {"tier": "Advanced", "category": "Push", "sets": 4, "reps": 6, "duration_min": 30, "rest_sec": 120, "cue": "Belly to wall, controlled descent, push through palms"},
    "Front Lever (Tuck/Straddle)": {"tier": "Advanced", "category": "Pull", "sets": 5, "reps": 8, "duration_min": 25, "rest_sec": 120, "cue": "Locked arms, pull bar down towards hips, horizontal torso"},
    "Full Planche Lean & Tuck": {"tier": "Advanced", "category": "Push", "sets": 5, "reps": 10, "duration_min": 25, "rest_sec": 120, "cue": "Protracted scapula, hands turned out, maximum lean forward"},
    "Pistol Squats (Single Leg)": {"tier": "Advanced", "category": "Legs", "sets": 4, "reps": 8, "duration_min": 25, "rest_sec": 90, "cue": "Single-leg balance, full depth, opposite leg straight"}
}

# Verified free video library
CALISTHENICS_VIDEOS = {
    "Push-Up Progression (Wall to Floor)": {"coach": "Hybrid Calisthenics", "url": "https://www.youtube.com/watch?v=zkU6Ok44_CI", "tier": "Beginner"},
    "First Pull-Up Progression (0 to 1)": {"coach": "THENX", "url": "https://www.youtube.com/watch?v=itaC8CXWP6A", "tier": "Beginner"},
    "Incline Australian Rows": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=GBqAZP6jquc", "tier": "Beginner"},
    "Deep Bodyweight Squat": {"coach": "Hybrid Calisthenics", "url": "https://www.youtube.com/watch?v=z3XQ7T4-abQ", "tier": "Beginner"},
    "Plank & Hollow Body": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=kL_NJAkCQBg", "tier": "Beginner"},
    "Strict Pull-Up Mastery": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "tier": "Intermediate"},
    "Parallel Bar Dips Guide": {"coach": "FitnessFAQs", "url": "https://www.youtube.com/watch?v=K5JxupmoLW4", "tier": "Intermediate"},
    "Floor L-Sit Tutorial": {"coach": "Antranik", "url": "https://www.youtube.com/watch?v=IUZJoSP66HI", "tier": "Intermediate"},
    "Pike Push-Up to Handstand": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=87MFaCpbTvM", "tier": "Intermediate"},
    "Bar Muscle-Up 3 Steps": {"coach": "THENX", "url": "https://www.youtube.com/watch?v=p7q0UhxPdLY", "tier": "Advanced"},
    "Wall Handstand Push-Ups": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=h0HjqYRlXYg", "tier": "Advanced"},
    "Front Lever Progressions": {"coach": "FitnessFAQs", "url": "https://www.youtube.com/watch?v=AGhb8V8M758", "tier": "Advanced"},
    "Planche Progression Masterclass": {"coach": "Calisthenicmovement", "url": "https://www.youtube.com/watch?v=UZ-1jwG7aQ4", "tier": "Advanced"}
}

# Researched Challenge Programming
CHALLENGE_SPECS = {
    "30-Day Foundation Challenge": {
        "days": 30,
        "blueprint": [
            {"name": "Push Foundation", "protocol": "4 Sets × 12 Incline/Floor Push-Ups", "duration": 25, "rest": 60},
            {"name": "Pull & Scapula Primer", "protocol": "4 Sets × 8 Australian Rows + 30s Dead Hang", "duration": 25, "rest": 60},
            {"name": "Core & Pelvic Stability", "protocol": "4 Sets × 45s Plank + 3x15 Hollow Tucks", "duration": 20, "rest": 45},
            {"name": "Lower Body Power", "protocol": "4 Sets × 15 Deep Squats + 3x12 Walking Lunges", "duration": 25, "rest": 60},
            {"name": "Full Body Volume Circuit", "protocol": "3 Rounds: 10 Push-Ups, 8 Rows, 15 Squats, 30s Plank", "duration": 30, "rest": 75},
            {"name": "Active Mobility & Decompression", "protocol": "20 Mins Shoulder Dislocates, Wrist Stretches & Hangs", "duration": 20, "rest": 30},
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
            {"name": "Deep Recovery & Mobility", "protocol": "30 Mins Hip Openers, Hamstring Flossing & Thoracic Mobility", "duration": 30, "rest": 0}
        ]
    }
}

# ==============================================================================
# 3. PAGE INITIALIZATION & UI STYLES
# ==============================================================================
st.set_page_config(page_title="MERO OS — Elite Calisthenics Engine", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0c1017; color: #f1f5f9; }
    
    .hero-header { font-size: 34px; font-weight: 800; color: #ffffff; line-height: 1.15; margin-bottom: 4px; }
    .blue-accent { color: #38bdf8; }
    
    .card {
        background: #141a24;
        border: 1px solid #20293a;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 14px;
    }
    
    .badge-pass {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-fail {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #e11d48;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
    .tag-tier {
        background: #1e293b;
        color: #38bdf8;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown('### ⚡ MERO ATHLETIC OS')
st.sidebar.markdown('<span style="background:#1e2638; padding:5px 10px; border-radius:999px; font-size:12px; color:#cbd5e1;">👤 Raju Maharjan (Admin)</span>', unsafe_allow_html=True)
st.sidebar.write("")

# Defines active_tab before any conditionals:
active_tab = st.sidebar.radio(
    "Navigation Matrix",
    [
        "📋 Calisthenics Codex & Standards",
        "🏋️ Daily Exercise Entry Logger",
        "🏆 30 / 90 Days Adaptive Challenge",
        "🩺 Wellness & Vitals HUD",
        "💰 Financial Ledger",
        "🎯 Operations & Tasks"
    ]
)

conn = get_db()

# ==============================================================================
# MODULE 1: CALISTHENICS CODEX & STANDARDS DIRECTORY
# ==============================================================================
if active_tab == "📋 Calisthenics Codex & Standards":
    st.markdown('<p class="hero-header">Calisthenics Progression Standards</p>', unsafe_allow_html=True)
    st.caption("Standardized rep ranges, set protocols, duration, and rest parameters researched from Thenx and Reddit RR.")

    tier_filter = st.radio("Select Experience Tier", ["All Tiers", "Beginner", "Intermediate", "Advanced"], horizontal=True)
    
    # Filter standards
    filtered_items = {k: v for k, v in EXERCISE_STANDARDS.items() if tier_filter == "All Tiers" or v["tier"] == tier_filter}
    
    for name, data in filtered_items.items():
        with st.container(border=True):
            col_l, col_r = st.columns([2, 1.2])
            with col_l:
                st.markdown(f"#### ⚡ {name}")
                st.markdown(f"<span class='tag-tier'>{data['tier']}</span> &nbsp; <span style='color:#94a3b8; font-size:13px;'>Category: <b>{data['category']}</b></span>", unsafe_allow_html=True)
                st.markdown(f"**Key Form Cue:** `{data['cue']}`")
            with col_r:
                st.markdown(f"""
                - **Target Sets:** `{data['sets']} Sets`
                - **Target Reps/Hold:** `{data['reps']} Reps/Sec`
                - **Target Duration:** `~{data['duration_min']} Mins`
                - **Prescribed Rest:** `{data['rest_sec']} Seconds`
                """)

    st.markdown("---")
    st.markdown("### 🎬 Free Video Masterclasses")
    v_cols = st.columns(2)
    idx = 0
    for title, vdata in CALISTHENICS_VIDEOS.items():
        if tier_filter == "All Tiers" or vdata["tier"] == tier_filter:
            with v_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**{title}** (`{vdata['coach']}`)")
                    st.video(vdata["url"])
            idx += 1

# ==============================================================================
# MODULE 2: DAILY EXERCISE ENTRY LOGGER (SETS, REPS, TIME, REST, SUCCESS/FAIL)
# ==============================================================================
elif active_tab == "🏋️ Daily Exercise Entry Logger":
    st.markdown('<p class="hero-header">Daily Exercise Entry & Performance Log</p>', unsafe_allow_html=True)
    st.caption("Auto-populates scientific set/rep/rest benchmarks. Log actual numbers and track your Success/Failure rate.")

    col_entry, col_history = st.columns([1.2, 1.3], gap="medium")

    with col_entry:
        with st.container(border=True):
            st.markdown("#### 📝 Record Performance Set")
            
            chosen_ex = st.selectbox("Select Target Exercise", list(EXERCISE_STANDARDS.keys()))
            default_spec = EXERCISE_STANDARDS[chosen_ex]

            with st.form("exercise_logging_form", clear_on_submit=False):
                e_date = st.date_input("Training Date", date.today())
                
                st.info(f"💡 Standard Prescription: **{default_spec['sets']} Sets** × **{default_spec['reps']} Reps** | **{default_spec['rest_sec']}s Rest** | **{default_spec['duration_min']} Mins Duration**")

                c1, c2 = st.columns(2)
                with c1:
                    completed_sets = st.number_input("Completed Sets", min_value=1, max_value=12, value=default_spec['sets'])
                    completed_reps = st.number_input("Completed Reps (or Hold Sec)", min_value=0, max_value=200, value=default_spec['reps'])
                with c2:
                    actual_duration = st.number_input("Total Duration (Mins)", min_value=1, max_value=120, value=default_spec['duration_min'])
                    actual_rest = st.number_input("Rest Time Taken Between Sets (Sec)", min_value=10, max_value=300, step=5, value=default_spec['rest_sec'])

                added_weight = st.number_input("Added Load / Vest (kg)", min_value=0.0, step=2.5, value=0.0)
                
                # Success or Failure Radio
                st.markdown("##### 🎯 Protocol Outcome")
                outcome_status = st.radio("Did you hit target reps without mechanical failure?", ["Successfully Done (Pass)", "Failed / Form Breakdown (Incomplete)"], horizontal=True)
                
                notes = st.text_input("Execution Notes", placeholder="e.g. Clean lockout, struggled on set 4")
                
                if st.form_submit_button("Commit Exercise Entry", type="primary", use_container_width=True):
                    status_clean = "Success" if "Successfully" in outcome_status else "Failed"
                    with conn:
                        conn.execute("""
                            INSERT INTO exercise_logs (date, exercise_name, tier, target_sets, completed_sets, target_reps, completed_reps, duration_min, rest_sec, weight_added, status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (str(e_date), chosen_ex, default_spec['tier'], default_spec['sets'], completed_sets, default_spec['reps'], completed_reps, actual_duration, actual_rest, added_weight, status_clean, notes))
                    
                    if status_clean == "Success":
                        st.toast(f"Crushed {chosen_ex}!", icon="🔥")
                    else:
                        st.toast(f"Marked {chosen_ex} as failure. Rest and re-test!", icon="⚠️")
                    st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown("#### 📋 Performance Feed & Audit")
            df_history = pd.read_sql("SELECT * FROM exercise_logs ORDER BY id DESC LIMIT 15", conn)
            
            if not df_history.empty:
                total_sets = len(df_history)
                success_sets = len(df_history[df_history['status'] == 'Success'])
                pass_rate = int((success_sets / total_sets) * 100)
                
                st.metric("Aggregate Pass / Success Rate", f"{pass_rate}%", f"{success_sets}/{total_sets} Sessions Passed")
                
                for _, row in df_history.iterrows():
                    badge = '<span class="badge-pass">✓ SUCCESS</span>' if row['status'] == 'Success' else '<span class="badge-fail">✕ FAILED</span>'
                    st.markdown(f"""
                        <div style="background:#131822; padding:12px; border-radius:12px; margin-bottom:8px; border:1px solid #1e2638;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#ffffff;">{row['exercise_name']}</b>
                                {badge}
                            </div>
                            <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                                Sets: <b>{row['completed_sets']}/{row['target_sets']}</b> | Reps: <b>{row['completed_reps']}/{row['target_reps']}</b> | Rest: <b>{row['rest_sec']}s</b> | Duration: <b>{row['duration_min']}m</b> | Load: <b>{row['weight_added']}kg</b>
                            </div>
                            <div style="color:#64748b; font-size:11px; margin-top:2px;">{row['date']} | Notes: {row['notes'] or 'Standard'}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No exercise performance logged yet. Commit your first entry on the left.")

# ==============================================================================
# MODULE 3: 30 / 90 DAYS ADAPTIVE CHALLENGE (PASS ➔ ADVANCE, FAIL ➔ REPEAT)
# ==============================================================================
elif active_tab == "🏆 30 / 90 Days Adaptive Challenge":
    st.markdown('<p class="hero-header">30 & 90 Days Crucible Engine</p>', unsafe_allow_html=True)
    st.caption("Hardcore progression rule: **Succeed ➔ Advance to Next Day**. **Fail ➔ Repeat Day Again** until mastered.")

    selected_challenge = st.radio("Select Crucible Track", list(CHALLENGE_SPECS.keys()), horizontal=True)
    spec = CHALLENGE_SPECS[selected_challenge]
    total_days = spec["days"]
    blueprint = spec["blueprint"]

    # Fetch current state from DB
    state_row = conn.execute("SELECT current_day, retries_count FROM challenge_state WHERE challenge_name = ?", (selected_challenge,)).fetchone()
    current_day = state_row["current_day"] if state_row else 1
    total_retries = state_row["retries_count"] if state_row else 0

    # Get prescribed workout for current day
    day_idx = (current_day - 1) % len(blueprint)
    daily_workout = blueprint[day_idx]

    # Metrics HUD
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
            <div class="card">
                <div style="font-size:12px; color:#94a3b8; font-weight:700;">CURRENT UNLOCKED DAY</div>
                <div style="font-size:32px; font-weight:800; color:#38bdf8;">Day {current_day} <span style="font-size:16px; color:#64748b;">/ {total_days}</span></div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="card">
                <div style="font-size:12px; color:#94a3b8; font-weight:700;">CHALLENGE COMPLETION</div>
                <div style="font-size:32px; font-weight:800; color:#10b981;">{int((current_day - 1) / total_days * 100)}%</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="card">
                <div style="font-size:12px; color:#94a3b8; font-weight:700;">FAILURE REPEAT RETRIES</div>
                <div style="font-size:32px; font-weight:800; color:#fb7185;">{total_retries} Retries</div>
            </div>
        """, unsafe_allow_html=True)

    st.progress(min((current_day - 1) / float(total_days), 1.0))

    col_play, col_history = st.columns([1.2, 1.3], gap="medium")

    with col_play:
        with st.container(border=True):
            st.markdown(f"### 🎯 Day {current_day}: {daily_workout['name']}")
            st.warning(f"⚡ **Prescribed Routine:** {daily_workout['protocol']}")
            st.markdown(f"⏱️ **Target Duration:** `{daily_workout['duration']} Minutes` | 🛑 **Prescribed Rest Between Sets:** `{daily_workout['rest']} Seconds`")
            
            st.markdown("---")
            st.markdown("#### 📝 Day Performance Entry")
            with st.form("challenge_checkin_form"):
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    sets_done = st.number_input("Sets Completed", min_value=1, max_value=20, value=4)
                    reps_done = st.number_input("Total Reps Completed", min_value=1, max_value=300, value=40)
                with c_s2:
                    time_taken = st.number_input("Actual Session Duration (Mins)", min_value=5, max_value=180, value=daily_workout['duration'])
                    rest_taken = st.number_input("Actual Rest Taken (Sec)", min_value=0, max_value=300, value=daily_workout['rest'])

                st.markdown("##### ⚖️ Official Verification Result")
                challenge_outcome = st.radio(
                    "Did you complete every single set/rep with solid form?", 
                    ["🟢 Successfully Done (Advance to Next Day)", "🔴 Failed / Incomplete (Repeat Day Again)"]
                )
                attempt_notes = st.text_input("Session Debrief / Reflection", placeholder="e.g. Failed on last set of pull-ups")

                submit_day = st.form_submit_button("Submit Challenge Protocol", type="primary", use_container_width=True)

                if submit_day:
                    is_success = "Successfully" in challenge_outcome
                    status_val = "Success" if is_success else "Failed"

                    # 1. Log attempt
                    with conn:
                        conn.execute("""
                            INSERT INTO challenge_logs (challenge_name, day_number, date, completed_sets, completed_reps, actual_duration_min, actual_rest_sec, status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (selected_challenge, current_day, str(date.today()), sets_done, reps_done, time_taken, rest_taken, status_val, attempt_notes))

                    # 2. Adaptive Rule Engine
                    if is_success:
                        if current_day < total_days:
                            new_day = current_day + 1
                            with conn:
                                conn.execute("UPDATE challenge_state SET current_day = ? WHERE challenge_name = ?", (new_day, selected_challenge))
                            st.balloons()
                            st.success(f"🎉 Day {current_day} Conquered! You have unlocked Day {new_day}!")
                        else:
                            st.balloons()
                            st.success("🏆 VICTORY! You have completely conquered this entire challenge!")
                        st.rerun()
                    else:
                        with conn:
                            conn.execute("UPDATE challenge_state SET retries_count = retries_count + 1 WHERE challenge_name = ?", (selected_challenge,))
                        st.error(f"⚠️ Day {current_day} marked as Failed. Mastery requires discipline. You must REPEAT Day {current_day} tomorrow!")
                        st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown(f"#### 📜 Day Attempt Audit ({selected_challenge})")
            df_ch_logs = pd.read_sql("SELECT * FROM challenge_logs WHERE challenge_name = ? ORDER BY id DESC LIMIT 15", conn, params=(selected_challenge,))
            
            if not df_ch_logs.empty:
                for _, r in df_ch_logs.iterrows():
                    badge = '<span class="badge-pass">✓ PASSED</span>' if r['status'] == 'Success' else '<span class="badge-fail">✕ FAILED (REPEAT)</span>'
                    st.markdown(f"""
                        <div style="background:#131822; padding:12px; border-radius:12px; margin-bottom:8px; border:1px solid #1e2638;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#ffffff;">Day {r['day_number']} Attempt</b>
                                {badge}
                            </div>
                            <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                                Sets: <b>{r['completed_sets']}</b> | Reps: <b>{r['completed_reps']}</b> | Duration: <b>{r['actual_duration_min']}m</b> | Rest: <b>{r['actual_rest_sec']}s</b> | {r['date']}
                            </div>
                            <div style="color:#64748b; font-size:11px; margin-top:2px;">Debrief: {r['notes'] or 'None'}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No attempts logged for this challenge yet.")

    # Reset Option
    with st.expander("⚙️ Challenge Admin Reset"):
        if st.button("Reset Challenge Back to Day 1", use_container_width=True):
            with conn:
                conn.execute("UPDATE challenge_state SET current_day = 1, retries_count = 0 WHERE challenge_name = ?", (selected_challenge,))
            st.rerun()

# ==============================================================================
# MODULE 4: WELLNESS & VITALS HUD (Reference Mockup)
# ==============================================================================
elif active_tab == "🩺 Wellness & Vitals HUD":
    col_hero, col_chips = st.columns([1.5, 1])
    with col_hero:
        st.markdown('''
            <div>
                <p class="hero-header">Stay Healthy<br>Keep Body <span style="background:#2563eb; color:white; padding:2px 14px; border-radius:999px;">Strong</span></p>
                <p style="color:#64748b; font-size:14px;">Real-time biometric telemetrics & cardiovascular efficiency.</p>
            </div>
        ''', unsafe_allow_html=True)
    with col_chips:
        st.markdown('''
            <div style="text-align: right; padding-top: 10px;">
                <span style="background:#1c2434; border:1px solid #2a374f; padding:6px 12px; border-radius:999px; font-size:12px;">🔥 2,480 Kcal</span>
                <span style="background:#1c2434; border:1px solid #2a374f; padding:6px 12px; border-radius:999px; font-size:12px;">❤️ 110 bpm</span>
            </div>
        ''', unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('''
            <div class="card">
                <div style="font-size:11px; color:#94a3b8; font-weight:700;">PULSE RATE MONITOR</div>
                <div style="font-size:28px; font-weight:800; color:#ffffff; margin-top:4px;">110 <span style="font-size:14px; color:#94a3b8;">BPM</span></div>
                <div style="color:#38bdf8; font-size:11px; margin-top:4px;">✓ Need to keep balance</div>
            </div>
        ''', unsafe_allow_html=True)
        pulse_data = pd.DataFrame({"Time": ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"], "BPM": [65, 82, 110, 95, 128, 74]})
        st.altair_chart(alt.Chart(pulse_data).mark_line(color="#38bdf8", strokeWidth=3).encode(x="Time:N", y=alt.Y("BPM:Q", scale=alt.Scale(domain=[50, 140]))).properties(height=110), use_container_width=True)

    with c2:
        st.markdown('''
            <div class="card">
                <div style="font-size:11px; color:#94a3b8; font-weight:700;">GLUCOSE RESULTS (WEEKLY)</div>
                <div style="font-size:28px; font-weight:800; color:#ffffff; margin-top:4px;">120.00 <span style="font-size:14px; color:#94a3b8;">Avg. mg/dl</span></div>
                <div style="color:#10b981; font-size:11px; margin-top:4px;">Optimal Range</div>
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
            <div class="card">
                <div style="font-size:11px; color:#94a3b8; font-weight:700;">VITAL SIGNS</div>
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
                if st.button("➕ +250ml", use_container_width=True):
                    with conn:
                        conn.execute("INSERT INTO daily_water (date, cups) VALUES (?, 1) ON CONFLICT(date) DO UPDATE SET cups = cups + 1", (today_str,))
                    st.rerun()
            with colw2:
                if st.button("➖ Remove", use_container_width=True):
                    if cur_w > 0:
                        with conn:
                            conn.execute("UPDATE daily_water SET cups = cups - 1 WHERE date = ?", (today_str,))
                        st.rerun()

# ==============================================================================
# MODULE 5: FINANCIAL LEDGER
# ==============================================================================
elif active_tab == "💰 Financial Ledger":
    st.markdown('<p class="hero-header">Financial Transaction Ledger</p>', unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([1, 1.4])
    with col_f1:
        with st.container(border=True):
            st.markdown("##### ➕ Record Expenditure")
            with st.form("expense_entry_form", clear_on_submit=True):
                e_date = st.date_input("Date", date.today())
                e_shop = st.text_input("Merchant Entity", placeholder="e.g. Gym Supplements Store")
                e_item = st.text_input("Item Description", placeholder="e.g. Whey Protein, Chalk")
                e_amount = st.number_input("Amount (NPR)", min_value=0.0, step=100.0, value=500.0)
                e_cat = st.selectbox("Category", ["Fitness & Nutrition", "Food & Dining", "Logistics & Fuel", "Subscriptions"])
                
                if st.form_submit_button("Commit Expense", type="primary", use_container_width=True):
                    with conn:
                        conn.execute("""
                            INSERT INTO expenses (date, shop, items, amount, payment_method, main_category, sub_category)
                            VALUES (?, ?, ?, ?, 'Direct', ?, 'General')
                        """, (str(e_date), e_shop, e_item, e_amount, e_cat))
                    st.success("Expense saved to database!")
                    st.rerun()

    with col_f2:
        with st.container(border=True):
            st.markdown("##### 📋 Master Ledger")
            df_exp = pd.read_sql("SELECT date, shop, items, amount, main_category FROM expenses ORDER BY id DESC LIMIT 10", conn)
            if not df_exp.empty:
                st.dataframe(df_exp, use_container_width=True, hide_index=True)
            else:
                st.info("No expenditures logged yet.")

# ==============================================================================
# MODULE 6: OPERATIONS & TASKS
# ==============================================================================
elif active_tab == "🎯 Operations & Tasks":
    st.markdown('<p class="hero-header">Operations & Task Queue</p>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([1, 1.4])
    with col_t1:
        with st.container(border=True):
            st.markdown("##### ➕ Schedule Task")
            with st.form("task_new_form", clear_on_submit=True):
                t_title = st.text_input("Task Objective")
                t_client = st.text_input("Stakeholder", value="Internal")
                t_deadline = st.date_input("Deadline", date.today())
                t_priority = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🔵 Low"])
                if st.form_submit_button("Add Task", type="primary", use_container_width=True):
                    if t_title:
                        with conn:
                            conn.execute("INSERT INTO tasks (title, deadline, client, priority, status) VALUES (?, ?, ?, ?, 'Pending')",
                                         (t_title, str(t_deadline), t_client, t_priority))
                        st.rerun()

    with col_t2:
        with st.container(border=True):
            st.markdown("##### 📌 Active Tasks")
            df_t = pd.read_sql("SELECT id, title, deadline, priority, status FROM tasks WHERE status != 'Completed' ORDER BY id DESC", conn)
            if not df_t.empty:
                st.dataframe(df_t, use_container_width=True, hide_index=True)
            else:
                st.info("All tasks completed.")
