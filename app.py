import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ==============================================================================
# 1. DATABASE & STORAGE LAYER (SQLite Persistence)
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
        # Tasks
        c.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, deadline TEXT, client TEXT, priority TEXT, status TEXT
            )
        """)
        # Counterparty Credit
        c.execute("""
            CREATE TABLE IF NOT EXISTS credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, person TEXT, amount REAL, due_date TEXT, status TEXT
            )
        """)
        # Hydration
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_water (
                date TEXT PRIMARY KEY, cups INTEGER
            )
        """)
        # Calisthenics Exercise Session Logger (Sets, Reps, Success / Fail)
        c.execute("""
            CREATE TABLE IF NOT EXISTS exercise_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise_name TEXT,
                tier TEXT,
                sets_target INTEGER,
                sets_done INTEGER,
                reps_target INTEGER,
                reps_done INTEGER,
                weight_added REAL,
                outcome TEXT,
                notes TEXT
            )
        """)
        # 30 / 90 Days Challenge Progress
        c.execute("""
            CREATE TABLE IF NOT EXISTS challenge_progress (
                challenge_name TEXT,
                day_number INTEGER,
                completed INTEGER,
                completion_date TEXT,
                PRIMARY KEY (challenge_name, day_number)
            )
        """)
        # Telemetry & Health Vitals (Mockup reference)
        c.execute("""
            CREATE TABLE IF NOT EXISTS vitals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                pulse_bpm INTEGER,
                hrv INTEGER,
                blood_pressure TEXT,
                glucose REAL,
                hba1c REAL,
                kcal INTEGER
            )
        """)
        conn.commit()

init_db()

# ==============================================================================
# 2. CALISTHENICS REPOSITORY & PROGRESSION DATA
# ==============================================================================
CALISTHENICS_LIBRARY = {
    "Tier 1: Foundation (Beginner)": [
        {
            "name": "Scapular Pull-Ups & Dead Hang",
            "muscles": "Lats, Grip, Lower Trapezius",
            "cues": "Hang from bar with active shoulders. Depress scapula downward without bending elbows.",
            "mistakes": "Swinging, shrugging shoulders up to ears.",
            "target": "3 Sets × 30-45s Hang",
            "video_url": "https://www.youtube.com/watch?v=Jm_w8t4b9_8",
            "icon": "🏋️‍♂️"
        },
        {
            "name": "Incline & Knee Push-Ups",
            "muscles": "Pectorals, Anterior Deltoids, Core",
            "cues": "Keep straight hollow body line. Elbows at 45° angle, touch chest to elevated surface.",
            "mistakes": "Flaring elbows to 90°, arching lower back.",
            "target": "3 Sets × 12-15 Reps",
            "video_url": "https://www.youtube.com/watch?v=4dF1DOWzf20",
            "icon": "💪"
        },
        {
            "name": "Incline Australian Rows",
            "muscles": "Upper Back, Rear Delts, Rhomboids, Biceps",
            "cues": "Hold bar at waist height, lean back at 45°, pull chest directly to bar maintaining plank.",
            "mistakes": "Dropping hips, pulling with neck.",
            "target": "3 Sets × 10-12 Reps",
            "video_url": "https://www.youtube.com/watch?v=dvkIa Karns0",
            "icon": "⚡"
        }
    ],
    "Tier 2: Core Strength (Intermediate)": [
        {
            "name": "Strict Hollow Body Pull-Ups",
            "muscles": "Latissimus Dorsi, Biceps, Core, Forearms",
            "cues": "Full dead hang at bottom, chin clearly clears the bar at top. No kipping or swinging.",
            "mistakes": "Crossing legs and arching back, partial range of motion.",
            "target": "4 Sets × 8-10 Reps",
            "video_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g",
            "icon": "🦅"
        },
        {
            "name": "Parallel Bar Dips",
            "muscles": "Triceps Brachii, Lower Chest, Shoulders",
            "cues": "Lower body until shoulders are below 90° elbow bend. Press up explosively to lockout.",
            "mistakes": "Half reps, shrugging shoulders into ears.",
            "target": "4 Sets × 10-12 Reps",
            "video_url": "https://www.youtube.com/watch?v=2z8JmcrW-As",
            "icon": "🔥"
        },
        {
            "name": "Parallel Bar / Floor L-Sit",
            "muscles": "Abdominals, Hip Flexors, Triceps Lockout",
            "cues": "Push floor/bars away with locked arms, elevate legs parallel to ground with pointed toes.",
            "mistakes": "Bending knees, leaning excessively backward.",
            "target": "4 Sets × 15-20s Hold",
            "video_url": "https://www.youtube.com/watch?v=IUZJoSP66HI",
            "icon": "🎯"
        }
    ],
    "Tier 3: Elite Mastery (Advanced)": [
        {
            "name": "Bar Muscle-Up",
            "muscles": "Lats, Chest, Explosive Fast-Twitch Fibers, Triceps",
            "cues": "Explosive high pull to sternum, rapid chest transition over the bar, finish with straight dip.",
            "mistakes": "Chicken-winging one arm over first, excessive swinging kip.",
            "target": "4 Sets × 3-5 Reps",
            "video_url": "https://www.youtube.com/watch?v=b0iG5sV_ZgY",
            "icon": "👑"
        },
        {
            "name": "Front Lever Progression (Straddle / Full)",
            "muscles": "Lats, Scapular Retractors, Full Posterior Chain, Abs",
            "cues": "Straight arm lockout, pull bar down toward hips, create rigid horizontal plank.",
            "mistakes": "Bending elbows, piked hips.",
            "target": "5 Sets × 5-10s Hold",
            "video_url": "https://www.youtube.com/watch?v=t5Jc8q44j74",
            "icon": "⚡"
        },
        {
            "name": "Full Handstand Push-Up (HSPU)",
            "muscles": "Anterior Deltoids, Triceps, Trapezius, Core Balance",
            "cues": "Maintain tight hollow body, head moves forward creating tripod at bottom, press up.",
            "mistakes": "Banana back arch, flared elbows.",
            "target": "4 Sets × 5-8 Reps",
            "video_url": "https://www.youtube.com/watch?v=hMN1XQ_q0X4",
            "icon": "🏆"
        }
    ]
}

# 30 & 90 Days Preset Routines
CHALLENGE_SCHEDULE = {
    "30-Day Foundation Challenge": {
        "days": 30,
        "routine": [
            "Upper Push: 4x10 Push-ups, 3x8 Dips, 3x30s Plank",
            "Upper Pull: 4x6 Pull-ups, 3x10 Australian Rows, 3x30s Hang",
            "Core & Legs: 4x15 Squats, 4x12 Walking Lunges, 3x20s L-sit",
            "Active Recovery / Mobility: 20min Stretch & Wrist Conditioning",
            "Full Body Primer: 3x8 Pull-ups, 3x12 Push-ups, 3x15 Squats",
            "Endurance Circuit: 5 Rounds (5 Pull-ups, 10 Push-ups, 15 Squats)",
            "Complete Rest & Nutrition Rebalance"
        ]
    },
    "90-Day Elite Beast Challenge": {
        "days": 90,
        "routine": [
            "Explosive Pull: 5x5 High Pull-ups, 4x8 Archer Rows, 4x10s Lever Hold",
            "Heavy Push: 5x8 Deep Dips, 4x5 Pike HSPU, 4x12 Diamond Push-ups",
            "Core Compression: 5x15s L-Sit, 4x10 Hanging Leg Raises, 4x8 Dragon Flags",
            "Leg Power: 4x8 Pistol Squats each leg, 5x10 Jump Squats, 4x45s Wall Sit",
            "Skill Day: Muscle-up Transition Drills + Handstand Balance (30 mins)",
            "Metabolic Calisthenics: 100 Push-ups + 50 Pull-ups for time",
            "Deep Rest & Contrast Therapy"
        ]
    }
}

# ==============================================================================
# 3. PAGE INITIALIZATION & HIGH-END ATHLETE DARK THEME
# ==============================================================================
st.set_page_config(
    page_title="MERO OS — Executive Health & Calisthenics", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS mimicking the user's reference mockup
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background-color: #0d1117;
        color: #f1f5f9;
    }
    
    /* Mockup Header Gradient & Cards */
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        line-height: 1.15;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .hero-pill {
        background: #2563eb;
        color: #ffffff;
        padding: 4px 16px;
        border-radius: 9999px;
        display: inline-block;
        font-weight: 800;
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.5);
    }
    
    /* Modern Glassmorphic Metric Container */
    .athlete-card {
        background: #161c26;
        border: 1px solid #232d3f;
        padding: 22px;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 16px;
    }
    
    /* Vitals Chip from Reference */
    .chip {
        display: inline-flex;
        align-items: center;
        background: #1c2434;
        border: 1px solid #2a374f;
        padding: 8px 16px;
        border-radius: 9999px;
        color: #cbd5e1;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .metric-hero-val {
        font-size: 34px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    .metric-sub {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 600;
    }
    
    /* Exercise & Success Badges */
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-fail {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #e11d48;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication & State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Keep open for quick test or lock with auth

conn = get_db()

# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown('### ⚡ MERO ATHLETIC OS')
st.sidebar.markdown('<span class="chip">👤 Operator: <b>Raju Maharjan</b></span>', unsafe_allow_html=True)
st.sidebar.write("")

active_tab = st.sidebar.radio(
    "Navigation Matrix",
    [
        "🩺 Wellness, Vitals & HUD", 
        "🤸 Calisthenics Mastery Academy", 
        "📝 Daily Workout Reps & Sets Logger", 
        "🏆 30 / 90 Days Transformation", 
        "💰 Financial Ledger",
        "🎯 Operations & Tasks"
    ]
)

# ==============================================================================
# MODULE 1: WELLNESS, VITALS & HUD (Directly based on mockup image)
# ==============================================================================
if active_tab == "🩺 Wellness, Vitals & HUD":
    # Top Hero Layout from Mockup Screen 1 & 2
    col_hero, col_chips = st.columns([1.5, 1])
    with col_hero:
        st.markdown('''
            <div>
                <p class="hero-title">Stay Healthy<br>Keep Body <span class="hero-pill">Strong</span></p>
                <p style="color:#64748b; font-size:15px; font-weight:500;">Real-time biometric telemetrics & cardiovascular efficiency.</p>
            </div>
        ''', unsafe_allow_html=True)
    with col_chips:
        st.markdown('''
            <div style="text-align: right; padding-top: 15px;">
                <span class="chip">🔥 2,480 Kcal</span>
                <span class="chip">❤️ 110 bpm</span>
                <span class="chip">⚡ HRV 54</span>
            </div>
        ''', unsafe_allow_html=True)

    st.write("")

    # Three Column Telemetry Cards (Matching Screen 1 & 2 from screenshot)
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown('''
            <div class="athlete-card">
                <div class="metric-sub">PULSE RATE MONITOR</div>
                <div style="display:flex; align-items:center; gap: 10px; margin-top:8px;">
                    <span style="font-size:30px;">❤️</span>
                    <span class="metric-hero-val">110 <span style="font-size:16px; color:#94a3b8;">BPM</span></span>
                </div>
                <div style="margin-top:8px; color:#38bdf8; font-size:12px; font-weight:600;">
                    ✓ Need to keep <span style="text-decoration:underline;">balance</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # Pulse Sparkline
        pulse_data = pd.DataFrame({
            "Time": ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
            "BPM": [65, 82, 110, 95, 128, 74]
        })
        chart_pulse = alt.Chart(pulse_data).mark_line(color="#38bdf8", strokeWidth=3, point=True).encode(
            x=alt.X("Time:N", title=None),
            y=alt.Y("BPM:Q", scale=alt.Scale(domain=[50, 140]), title=None)
        ).properties(height=130)
        st.altair_chart(chart_pulse, use_container_width=True)

    with col_c2:
        st.markdown('''
            <div class="athlete-card">
                <div class="metric-sub">GLUCOSE RESULTS (WEEKLY)</div>
                <div class="metric-hero-val" style="margin-top:6px;">120.00 <span style="font-size:16px; color:#94a3b8;">Avg. mg/dl</span></div>
                <div style="color:#10b981; font-size:12px; font-weight:600; margin-top:4px;">Optimal Fasting Target</div>
            </div>
        ''', unsafe_allow_html=True)

        # Glucose Bar Chart with Thursday highlighted (from mockup)
        glucose_df = pd.DataFrame({
            "Day": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "Level": [95, 105, 110, 100, 85, 115, 102],
            "Color": ["#25334d", "#25334d", "#25334d", "#25334d", "#3b82f6", "#25334d", "#25334d"]
        })
        chart_glucose = alt.Chart(glucose_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Day:N", sort=None, title=None),
            y=alt.Y("Level:Q", title=None),
            color=alt.Color("Color:N", scale=None)
        ).properties(height=130)
        st.altair_chart(chart_glucose, use_container_width=True)

    with col_c3:
        st.markdown('''
            <div class="athlete-card">
                <div class="metric-sub">CARDIOVASCULAR & LAB METRICS</div>
                <div style="margin-top:10px; display:flex; justify-content:space-between;">
                    <div>
                        <div style="color:#64748b; font-size:12px; font-weight:700;">GLYCATED SUGAR</div>
                        <div style="font-size:24px; font-weight:800; color:#ffffff;">120 <span style="font-size:14px; color:#94a3b8;">HbA1c</span></div>
                    </div>
                    <div>
                        <div style="color:#64748b; font-size:12px; font-weight:700;">BLOOD PRESSURE</div>
                        <div style="font-size:24px; font-weight:800; color:#38bdf8;">104 <span style="font-size:14px; color:#94a3b8;">mmHg</span></div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # Hydration integration
        today_str = str(date.today())
        water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
        current_water = water_row[0] if water_row else 2

        with st.container(border=True):
            st.markdown(f"**💧 Cellular Hydration**: `{current_water} / 10 Glasses` (2.5L)")
            st.progress(min(current_water / 10.0, 1.0))
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                if st.button("➕ Drink +250ml", use_container_width=True):
                    with conn:
                        conn.execute("INSERT INTO daily_water (date, cups) VALUES (?, 1) ON CONFLICT(date) DO UPDATE SET cups = cups + 1", (today_str,))
                    st.rerun()
            with col_w2:
                if st.button("➖ Remove Glass", use_container_width=True):
                    if current_water > 0:
                        with conn:
                            conn.execute("UPDATE daily_water SET cups = cups - 1 WHERE date = ?", (today_str,))
                        st.rerun()

# ==============================================================================
# MODULE 2: CALISTHENICS MASTERY ACADEMY (Beginner to Advanced)
# ==============================================================================
elif active_tab == "🤸 Calisthenics Mastery Academy":
    st.markdown('<p class="hero-title">Calisthenics Progression Codex</p>', unsafe_allow_html=True)
    st.caption("Curated from the biomechanics frameworks of Thenx, Caliverse, and GymnasticBodies.")
    
    tier_choice = st.segmented_control(
        "Select Experience Level",
        ["Tier 1: Foundation (Beginner)", "Tier 2: Core Strength (Intermediate)", "Tier 3: Elite Mastery (Advanced)"],
        default="Tier 1: Foundation (Beginner)"
    )

    exercises = CALISTHENICS_LIBRARY.get(tier_choice, [])

    for ex in exercises:
        with st.container(border=True):
            c_header, c_action = st.columns([3, 1])
            with c_header:
                st.markdown(f"### {ex['icon']} {ex['name']}")
                st.markdown(f"**🎯 Target Anatomy**: `{ex['muscles']}` | **Prescribed Volume**: `{ex['target']}`")
            
            col_desc, col_media = st.columns([1.6, 1.2])
            with col_desc:
                st.markdown("##### 📌 Master Form Cues")
                st.info(ex['cues'])
                
                st.markdown("##### ⚠️ Common Fatal Mistakes")
                st.warning(ex['mistakes'])
                
            with col_media:
                st.markdown("##### 🎬 Video Tutorial Reference")
                st.video(ex['video_url'])

# ==============================================================================
# MODULE 3: DAILY EXERCISE REPS & SETS LOGGER (With Success / Failure Tracking)
# ==============================================================================
elif active_tab == "📝 Daily Workout Reps & Sets Logger":
    st.markdown('<p class="hero-title">Exercise Protocol & Performance Log</p>', unsafe_allow_html=True)
    st.caption("Record individual sets and reps, track progressive overload, and audit success vs. mechanical failure.")

    col_log_form, col_log_stats = st.columns([1.1, 1.4])

    with col_log_form:
        with st.container(border=True):
            st.markdown("#### ⚡ Log Current Exercise Set")
            with st.form("set_logger_form", clear_on_submit=False):
                log_date = st.date_input("Session Date", date.today())
                
                # All exercise choices flat list
                all_exercises = [
                    "Strict Pull-Ups", "Incline Push-Ups", "Standard Push-Ups", "Diamond Push-Ups",
                    "Parallel Bar Dips", "Australian Rows", "L-Sit Hold", "Bar Muscle-Up",
                    "Handstand Push-Ups", "Hanging Leg Raises", "Pistol Squats", "Planche Lean"
                ]
                selected_ex = st.selectbox("Exercise Name", all_exercises)
                tier_tag = st.selectbox("Skill Category", ["Push", "Pull", "Core & Lever", "Legs"])

                c_set1, c_set2 = st.columns(2)
                with c_set1:
                    target_sets = st.number_input("Target Sets", min_value=1, max_value=10, value=4)
                    target_reps = st.number_input("Target Reps/Hold (sec)", min_value=1, max_value=100, value=10)
                with c_set2:
                    done_sets = st.number_input("Completed Sets", min_value=1, max_value=10, value=4)
                    done_reps = st.number_input("Completed Reps/Hold", min_value=0, max_value=100, value=10)

                weight_add = st.number_input("Added Load / Vest (kg)", min_value=0.0, step=2.5, value=0.0)
                
                # Success or Failure choice
                outcome = st.radio("Set Outcome", ["Crushed Target (Success)", "Failed / Mechanical Fatigue"], horizontal=True)
                session_notes = st.text_input("Execution Notes", placeholder="e.g. Crisp lockout, struggled on 4th set")

                btn_log = st.form_submit_button("Commit Exercise Log", type="primary", use_container_width=True)
                
                if btn_log:
                    with conn:
                        conn.execute("""
                            INSERT INTO exercise_logs (date, exercise_name, tier, sets_target, sets_done, reps_target, reps_done, weight_added, outcome, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (str(log_date), selected_ex, tier_tag, target_sets, done_sets, target_reps, done_reps, weight_add, outcome, session_notes))
                    st.success(f"Logged {selected_ex} successfully!")
                    st.rerun()

    with col_log_stats:
        with st.container(border=True):
            st.markdown("#### 📋 Today's Session Feed & History")
            df_logs = pd.read_sql("SELECT * FROM exercise_logs ORDER BY id DESC LIMIT 15", conn)
            
            if not df_logs.empty:
                # Calculate success rate
                success_count = len(df_logs[df_logs["outcome"].str.contains("Success")])
                total_logged = len(df_logs)
                rate = int((success_count / total_logged) * 100)
                
                st.metric("Aggregate Protocol Success Rate", f"{rate}%", f"{success_count}/{total_logged} Sets Completed")

                for _, r in df_logs.iterrows():
                    badge_html = (
                        '<span class="badge-success">✓ SUCCESS</span>' 
                        if "Success" in r['outcome'] 
                        else '<span class="badge-fail">✕ FAILED</span>'
                    )
                    st.markdown(f"""
                        <div style="background:#131822; padding:12px; border-radius:12px; margin-bottom:8px; border:1px solid #1f2736;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#ffffff; font-size:15px;">{r['exercise_name']}</b>
                                {badge_html}
                            </div>
                            <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                                Sets: <b>{r['sets_done']}/{r['sets_target']}</b> | Reps: <b>{r['reps_done']}/{r['reps_target']}</b> | Load: <b>{r['weight_added']} kg</b> | {r['date']}
                            </div>
                            <div style="color:#64748b; font-size:11px; margin-top:3px;">Notes: {r['notes'] or 'Standard form'}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No exercise logs recorded yet. Complete your first set on the left!")

# ==============================================================================
# MODULE 4: 30 / 90 DAYS CALISTHENICS CHALLENGE
# ==============================================================================
elif active_tab == "🏆 30 / 90 Days Transformation":
    st.markdown('<p class="hero-title">Transformation Challenge Matrix</p>', unsafe_allow_html=True)
    st.caption("Hardcore progression schedule. Stick to the daily prescribed protocol and check off each day.")

    challenge_mode = st.radio(
        "Choose Your Crucible", 
        ["30-Day Foundation Challenge", "90-Day Elite Beast Challenge"], 
        horizontal=True
    )

    spec = CHALLENGE_SCHEDULE[challenge_mode]
    total_days = spec["days"]
    routines = spec["routine"]

    # Fetch completed days from DB
    completed_records = pd.read_sql(
        "SELECT day_number FROM challenge_progress WHERE challenge_name = ? AND completed = 1", 
        conn, 
        params=(challenge_mode,)
    )
    completed_days_set = set(completed_records["day_number"].tolist())
    completion_count = len(completed_days_set)
    progress_ratio = completion_count / float(total_days)

    # Progress Ring & Dashboard
    col_p1, col_p2 = st.columns([1.2, 2])
    with col_p1:
        st.markdown(f'''
            <div class="athlete-card" style="text-align:center;">
                <div class="metric-sub">OVERALL PROGRESSION</div>
                <div class="metric-hero-val" style="color:#38bdf8; font-size:42px; margin-top:10px;">
                    {completion_count} <span style="font-size:20px; color:#64748b;">/ {total_days} Days</span>
                </div>
                <div style="margin-top:12px; font-weight:700; color:#10b981;">{int(progress_ratio * 100)}% Completed</div>
            </div>
        ''', unsafe_allow_html=True)
        st.progress(progress_ratio)

    with col_p2:
        with st.container(border=True):
            st.markdown("##### 🎯 Quick Check-in Operator")
            selected_day = st.number_input("Select Day to Log", min_value=1, max_value=total_days, value=min(completion_count + 1, total_days))
            prescribed_routine = routines[(selected_day - 1) % len(routines)]
            
            st.markdown(f"**Day {selected_day} Protocol:**")
            st.info(f"⚡ {prescribed_routine}")

            is_already_done = selected_day in completed_days_set
            if is_already_done:
                st.success(f"✓ Day {selected_day} is completed and verified!")
                if st.button("Undo Day Completion", use_container_width=True):
                    with conn:
                        conn.execute("DELETE FROM challenge_progress WHERE challenge_name = ? AND day_number = ?", (challenge_mode, selected_day))
                    st.rerun()
            else:
                if st.button(f"Mark Day {selected_day} As Crushed & Finished", type="primary", use_container_width=True):
                    with conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO challenge_progress (challenge_name, day_number, completed, completion_date)
                            VALUES (?, ?, 1, ?)
                        """, (challenge_mode, selected_day, str(date.today())))
                    st.balloons()
                    st.rerun()

    st.write("---")
    st.markdown("#### 📅 30-Day / 90-Day Calendar Matrix")
    
    # Render Grid of Day Badges
    cols = st.columns(10)
    for d in range(1, total_days + 1):
        with cols[(d - 1) % 10]:
            if d in completed_days_set:
                st.markdown(f'<div style="background:#065f46; color:#34d399; text-align:center; padding:10px 4px; border-radius:10px; font-weight:800; margin-bottom:8px; font-size:12px;">D{d}<br>✓</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#1e293b; color:#64748b; text-align:center; padding:10px 4px; border-radius:10px; font-weight:700; margin-bottom:8px; font-size:12px;">D{d}<br>—</div>', unsafe_allow_html=True)

# ==============================================================================
# MODULE 5: FINANCIAL LEDGER
# ==============================================================================
elif active_tab == "💰 Financial Ledger":
    st.markdown('<p class="hero-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
    st.caption("Track business expenses, receipt staging, and budget allocation.")
    
    col_f1, col_f2 = st.columns([1, 1.3])
    with col_f1:
        with st.container(border=True):
            st.markdown("##### ➕ Record Expenditure")
            with st.form("expense_quick_form", clear_on_submit=True):
                e_date = st.date_input("Date", date.today())
                e_shop = st.text_input("Merchant Entity", placeholder="e.g. Gym Supplements Store")
                e_item = st.text_input("Item Description", placeholder="e.g. Whey Protein, Chalk, Straps")
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
            st.markdown("##### 📋 Recent Ledger History")
            df_exp = pd.read_sql("SELECT date, shop, items, amount, main_category FROM expenses ORDER BY id DESC LIMIT 10", conn)
            if not df_exp.empty:
                st.dataframe(df_exp, use_container_width=True, hide_index=True)
            else:
                st.info("No expenditures logged yet.")

# ==============================================================================
# MODULE 6: OPERATIONS & TASKS
# ==============================================================================
elif active_tab == "🎯 Operations & Tasks":
    st.markdown('<p class="hero-title">Operations & Task Queue</p>', unsafe_allow_html=True)
    
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
