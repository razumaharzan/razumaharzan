import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

# ==============================================================================
# 1. DATABASE SETUP & PERSISTENCE LAYER (SQLite)
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
        # Counterparty Credit
        c.execute("""
            CREATE TABLE IF NOT EXISTS credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, person TEXT, amount REAL, due_date TEXT, status TEXT
            )
        """)
        # Daily Water Tracker
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_water (
                date TEXT PRIMARY KEY, cups INTEGER
            )
        """)
        # Exercise Logs
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
        # Challenge Progress (30 / 90 Days)
        c.execute("""
            CREATE TABLE IF NOT EXISTS challenge_progress (
                challenge_name TEXT,
                day_number INTEGER,
                completed INTEGER,
                completion_date TEXT,
                PRIMARY KEY (challenge_name, day_number)
            )
        """)
        conn.commit()

init_db()

# ==============================================================================
# 2. PAGE CONFIGURATION & ATHLETE DARK THEME
# ==============================================================================
st.set_page_config(
    page_title="MERO OS — Executive Health & Calisthenics", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background-color: #0d1117;
        color: #f1f5f9;
    }
    
    .hero-title {
        font-size: 36px;
        font-weight: 800;
        line-height: 1.15;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .hero-pill {
        background: #2563eb;
        color: #ffffff;
        padding: 4px 14px;
        border-radius: 9999px;
        display: inline-block;
        font-weight: 800;
    }
    
    .athlete-card {
        background: #161c26;
        border: 1px solid #232d3f;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 15px;
    }
    
    .chip {
        display: inline-flex;
        align-items: center;
        background: #1c2434;
        border: 1px solid #2a374f;
        padding: 6px 14px;
        border-radius: 9999px;
        color: #cbd5e1;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .metric-hero-val {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    .metric-sub {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-fail {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #e11d48;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. CALISTHENICS REPOSITORY WITH 100% VERIFIED FREE VIDEO LINKS
# ==============================================================================
CALISTHENICS_LIBRARY = {
    "Tier 1: Foundation (Beginner)": [
        {
            "name": "Push-Up Progression (Wall to Floor)",
            "coach": "Hampton (Hybrid Calisthenics)",
            "badge": "PUSH FOUNDATION",
            "icon": "🧱",
            "muscles": "Pectorals, Anterior Deltoids, Triceps, Core",
            "target": "3 Sets × 10-15 Clean Reps",
            "cues": "Maintain a rigid plank. Keep elbows at 45 degrees, tuck hips and brace core.",
            "mistakes": "Flaring elbows to 90 degrees, sagging the lower back, doing partial reps.",
            "video_url": "https://www.youtube.com/watch?v=zkU6Ok44_CI"
        },
        {
            "name": "First Pull-Up Progression (0 to 1st Rep)",
            "coach": "Chris Heria (THENX)",
            "badge": "PULL FOUNDATION",
            "icon": "🧗",
            "muscles": "Lats, Biceps, Grip, Scapular Retractors",
            "target": "3 Sets × 30s Hang + 4x5 Slow Negatives",
            "cues": "Start with dead hangs, progress to scapular shrugs, then 5-second slow negative descents.",
            "mistakes": "Swinging, kicking knees up, skipping the eccentric lowering phase.",
            "video_url": "https://www.youtube.com/watch?v=itaC8CXWP6A"
        },
        {
            "name": "Australian Incline Horizontal Rows",
            "coach": "Calisthenicmovement",
            "badge": "POSTURE & BACK",
            "icon": "⚡",
            "muscles": "Rhomboids, Mid Trapezius, Rear Delts, Biceps",
            "target": "3 Sets × 8-12 Clean Reps",
            "cues": "Set bar at waist level. Keep straight bodyline and pull chest firmly to bar.",
            "mistakes": "Dropping hips, pulling with neck rather than back.",
            "video_url": "https://www.youtube.com/watch?v=GBqAZP6jquc"
        },
        {
            "name": "Bodyweight Deep Squat & Hip Mobility",
            "coach": "Hampton (Hybrid Calisthenics)",
            "badge": "LOWER BODY",
            "icon": "🦵",
            "muscles": "Quadriceps, Glutes, Hamstrings, Ankles",
            "target": "3 Sets × 15-20 Deep Reps",
            "cues": "Heels flat on the floor, push knees outward tracking over toes, descend deep.",
            "mistakes": "Heels lifting off ground, knees caving inward.",
            "video_url": "https://www.youtube.com/watch?v=z3XQ7T4-abQ"
        },
        {
            "name": "Plank & Hollow Body Stability",
            "coach": "Calisthenicmovement",
            "badge": "CORE INTEGRATION",
            "icon": "🛡️",
            "muscles": "Rectus Abdominis, Transverse Abdominis",
            "target": "4 Sets × 45-60s Hold",
            "cues": "Tuck tailbone under (posterior pelvic tilt). Dome upper back slightly and squeeze glutes.",
            "mistakes": "Letting hips sag toward floor, arching the lumbar spine.",
            "video_url": "https://www.youtube.com/watch?v=kL_NJAkCQBg"
        }
    ],
    "Tier 2: Core Strength (Intermediate)": [
        {
            "name": "Strict Hollow Body Pull-Ups",
            "coach": "Calisthenicmovement",
            "badge": "UPPER BODY PULL",
            "icon": "🦅",
            "muscles": "Latissimus Dorsi, Biceps, Upper Back",
            "target": "4 Sets × 6-10 Strict Reps",
            "cues": "Dead hang to full chin-over-bar without kipping or swinging legs.",
            "mistakes": "Kipping, half reps, shrugging shoulders.",
            "video_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g"
        },
        {
            "name": "Parallel Bar Dips (Form & Joint Longevity)",
            "coach": "Daniel Vadnal (FitnessFAQs)",
            "badge": "UPPER BODY PUSH",
            "icon": "🔥",
            "muscles": "Triceps, Lower Chest, Front Delts",
            "target": "4 Sets × 8-12 Full Reps",
            "cues": "Slight forward lean, lower until elbows reach 90 degrees, press up to lockout.",
            "mistakes": "Elbow flare, dropping too deep under uncontrolled momentum.",
            "video_url": "https://www.youtube.com/watch?v=K5JxupmoLW4"
        },
        {
            "name": "Floor L-Sit Progression",
            "coach": "Antranik (Calisthenics)",
            "badge": "COMPRESSION STRENGTH",
            "icon": "📐",
            "muscles": "Hip Flexors, Rectus Abdominis, Triceps",
            "target": "4 Sets × 15-20s Sustained Hold",
            "cues": "Push floor away forcefully with locked arms. Squeeze quads to extend legs.",
            "mistakes": "Bending elbows, relying only on abs instead of shoulder depression.",
            "video_url": "https://www.youtube.com/watch?v=IUZJoSP66HI"
        },
        {
            "name": "Pike Push-Up (Vertical Shoulder Strength)",
            "coach": "Calisthenicmovement",
            "badge": "OVERHEAD PRESSING",
            "icon": "⛰️",
            "muscles": "Deltoids, Upper Chest, Triceps",
            "target": "4 Sets × 6-10 Reps",
            "cues": "Hips elevated high above shoulders. Lower head forward into a tripod shape.",
            "mistakes": "Flaring elbows, letting hips slide backward.",
            "video_url": "https://www.youtube.com/watch?v=87MFaCpbTvM"
        }
    ],
    "Tier 3: Elite Mastery (Advanced)": [
        {
            "name": "Bar Muscle-Up Mastery",
            "coach": "Chris Heria (THENX)",
            "badge": "ELITE EXPLOSION",
            "icon": "👑",
            "muscles": "Fast-Twitch Lats, Chest, Triceps, Core",
            "target": "4 Sets × 3-5 Clean Reps",
            "cues": "Explosive pull to chest level, rapid wrist roll over the bar, finish with straight dip.",
            "mistakes": "Chicken-winging (one elbow over first), attempting without a base of 10+ pull-ups.",
            "video_url": "https://www.youtube.com/watch?v=p7q0UhxPdLY"
        },
        {
            "name": "Handstand Push-Up (HSPU)",
            "coach": "Calisthenicmovement",
            "badge": "VERTICAL BALANCE",
            "icon": "🤸‍♂️",
            "muscles": "Deltoids, Triceps, Upper Traps, Core",
            "target": "4 Sets × 4-6 Strict Reps",
            "cues": "Belly facing wall for straight alignment. Lower head forward, press to lockout.",
            "mistakes": "Arching back into banana handstand, flaring elbows.",
            "video_url": "https://www.youtube.com/watch?v=h0HjqYRlXYg"
        },
        {
            "name": "Front Lever Progression",
            "coach": "Daniel Vadnal (FitnessFAQs)",
            "badge": "HORIZONTAL PULL POWER",
            "icon": "📏",
            "muscles": "Latissimus Dorsi, Posterior Chain, Core",
            "target": "5 Sets × 5-10s Solid Hold",
            "cues": "Locked straight arms. Pull bar down toward hips while depressing shoulder blades.",
            "mistakes": "Bending elbows, piked hips.",
            "video_url": "https://www.youtube.com/watch?v=AGhb8V8M758"
        },
        {
            "name": "Full Planche Progression",
            "coach": "Calisthenicmovement",
            "badge": "PINNACLE CALISTHENICS",
            "icon": "🏆",
            "muscles": "Anterior Deltoids, Biceps Tendons, Serratus, Glutes",
            "target": "5 Sets × 8-12s Lean/Hold",
            "cues": "Protracted and depressed scapula, hands turned slightly outward, lean shoulders forward.",
            "mistakes": "Rushing before tendon adaptation, bent arms.",
            "video_url": "https://www.youtube.com/watch?v=UZ-1jwG7aQ4"
        }
    ]
}

# ==============================================================================
# 4. CHALLENGE SPECIFICATIONS
# ==============================================================================
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
# 5. SIDEBAR NAVIGATION — (DEFINES active_tab FIRST)
# ==============================================================================
st.sidebar.markdown('### ⚡ MERO ATHLETIC OS')
st.sidebar.markdown('<span class="chip">👤 Raju Maharjan</span>', unsafe_allow_html=True)
st.sidebar.write("")

# HERE IS WHERE active_tab IS DEFINED:
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

conn = get_db()

# ==============================================================================
# MODULE 1: WELLNESS, VITALS & HUD
# ==============================================================================
if active_tab == "🩺 Wellness, Vitals & HUD":
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

        pulse_data = pd.DataFrame({
            "Time": ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
            "BPM": [65, 82, 110, 95, 128, 74]
        })
        chart_pulse = alt.Chart(pulse_data).mark_line(color="#38bdf8", strokeWidth=3, point=True).encode(
            x=alt.X("Time:N", title=None),
            y=alt.Y("BPM:Q", scale=alt.Scale(domain=[50, 140]), title=None)
        ).properties(height=120)
        st.altair_chart(chart_pulse, use_container_width=True)

    with col_c2:
        st.markdown('''
            <div class="athlete-card">
                <div class="metric-sub">GLUCOSE RESULTS (WEEKLY)</div>
                <div class="metric-hero-val" style="margin-top:6px;">120.00 <span style="font-size:16px; color:#94a3b8;">Avg. mg/dl</span></div>
                <div style="color:#10b981; font-size:12px; font-weight:600; margin-top:4px;">Optimal Fasting Range</div>
            </div>
        ''', unsafe_allow_html=True)

        glucose_df = pd.DataFrame({
            "Day": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "Level": [95, 105, 110, 100, 85, 115, 102],
            "Color": ["#25334d", "#25334d", "#25334d", "#25334d", "#3b82f6", "#25334d", "#25334d"]
        })
        chart_glucose = alt.Chart(glucose_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Day:N", sort=None, title=None),
            y=alt.Y("Level:Q", title=None),
            color=alt.Color("Color:N", scale=None)
        ).properties(height=120)
        st.altair_chart(chart_glucose, use_container_width=True)

    with col_c3:
        st.markdown('''
            <div class="athlete-card">
                <div class="metric-sub">METABOLIC LAB REPORT</div>
                <div style="margin-top:10px; display:flex; justify-content:space-between;">
                    <div>
                        <div style="color:#64748b; font-size:11px; font-weight:700;">GLYCATED SUGAR</div>
                        <div style="font-size:22px; font-weight:800; color:#ffffff;">120 <span style="font-size:13px; color:#94a3b8;">HbA1c</span></div>
                    </div>
                    <div>
                        <div style="color:#64748b; font-size:11px; font-weight:700;">BLOOD PRESSURE</div>
                        <div style="font-size:22px; font-weight:800; color:#38bdf8;">104 <span style="font-size:13px; color:#94a3b8;">mmHg</span></div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        today_str = str(date.today())
        water_row = conn.execute("SELECT cups FROM daily_water WHERE date = ?", (today_str,)).fetchone()
        current_water = water_row[0] if water_row else 2

        with st.container(border=True):
            st.markdown(f"**💧 Cellular Hydration**: `{current_water} / 10 Glasses` (2.5L)")
            st.progress(min(current_water / 10.0, 1.0))
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                if st.button("➕ +250ml Glass", use_container_width=True):
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
# MODULE 2: CALISTHENICS MASTERY ACADEMY
# ==============================================================================
elif active_tab == "🤸 Calisthenics Mastery Academy":
    st.markdown('<p class="hero-title">Calisthenics Progression Academy</p>', unsafe_allow_html=True)
    st.caption("Structured progression from foundational moves to elite skills with 100% free video masterclasses.")
    
    tier_choice = st.radio(
        "Progression Level",
        list(CALISTHENICS_LIBRARY.keys()),
        horizontal=True
    )

    exercise_list = CALISTHENICS_LIBRARY.get(tier_choice, [])

    for ex in exercise_list:
        with st.container(border=True):
            col_info, col_vid = st.columns([1.3, 1.4], gap="medium")
            
            with col_info:
                st.markdown(f"### {ex['icon']} {ex['name']}")
                st.markdown(f"**Coach:** `{ex['coach']}` | **Category:** `{ex['badge']}`")
                st.markdown(f"**🎯 Target Anatomy:** `{ex['muscles']}`")
                st.markdown(f"**📊 Target Volume:** `{ex['target']}`")
                
                st.markdown("---")
                st.markdown("##### 📌 Master Biomechanical Cues")
                st.info(ex['cues'])
                
                st.markdown("##### ⚠️ Form Mistakes to Avoid")
                st.warning(ex['mistakes'])

            with col_vid:
                st.markdown("##### 🎬 Free Video Masterclass")
                st.video(ex['video_url'])

# ==============================================================================
# MODULE 3: DAILY EXERCISE REPS & SETS LOGGER
# ==============================================================================
elif active_tab == "📝 Daily Workout Reps & Sets Logger":
    st.markdown('<p class="hero-title">Exercise Protocol & Performance Log</p>', unsafe_allow_html=True)
    st.caption("Record every set, track progressive overload, and audit success vs failure.")

    col_form, col_history = st.columns([1.1, 1.4])

    with col_form:
        with st.container(border=True):
            st.markdown("#### ⚡ Log Current Exercise Set")
            with st.form("exercise_entry_form", clear_on_submit=False):
                log_date = st.date_input("Session Date", date.today())
                all_exercises = [
                    "Push-Up Progression", "Strict Pull-Ups", "Parallel Bar Dips", 
                    "Australian Rows", "L-Sit Hold", "Bar Muscle-Up", "Handstand Push-Ups", 
                    "Bodyweight Deep Squat", "Plank & Hollow Body", "Front Lever", "Full Planche"
                ]
                selected_ex = st.selectbox("Exercise Name", all_exercises)
                tier_tag = st.selectbox("Category", ["Push", "Pull", "Core & Lever", "Legs"])

                c_set1, c_set2 = st.columns(2)
                with c_set1:
                    target_sets = st.number_input("Target Sets", min_value=1, max_value=10, value=4)
                    target_reps = st.number_input("Target Reps/Hold (sec)", min_value=1, max_value=100, value=10)
                with c_set2:
                    done_sets = st.number_input("Completed Sets", min_value=1, max_value=10, value=4)
                    done_reps = st.number_input("Completed Reps/Hold", min_value=0, max_value=100, value=10)

                weight_add = st.number_input("Added Weight / Vest (kg)", min_value=0.0, step=2.5, value=0.0)
                outcome = st.radio("Execution Result", ["Crushed Target (Success)", "Failed / Form Breakdown"], horizontal=True)
                notes = st.text_input("Session Notes", placeholder="e.g. Crisp lockout, struggled on 4th set")

                if st.form_submit_button("Commit Exercise Log", type="primary", use_container_width=True):
                    with conn:
                        conn.execute("""
                            INSERT INTO exercise_logs (date, exercise_name, tier, sets_target, sets_done, reps_target, reps_done, weight_added, outcome, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (str(log_date), selected_ex, tier_tag, target_sets, done_sets, target_reps, done_reps, weight_add, outcome, notes))
                    st.success(f"Logged {selected_ex} successfully!")
                    st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown("#### 📋 Performance History")
            df_logs = pd.read_sql("SELECT * FROM exercise_logs ORDER BY id DESC LIMIT 15", conn)
            
            if not df_logs.empty:
                success_count = len(df_logs[df_logs["outcome"].str.contains("Success")])
                total_logged = len(df_logs)
                rate = int((success_count / total_logged) * 100)
                
                st.metric("Protocol Success Rate", f"{rate}%", f"{success_count}/{total_logged} Sets Finished")

                for _, r in df_logs.iterrows():
                    badge = '<span class="badge-success">✓ SUCCESS</span>' if "Success" in r['outcome'] else '<span class="badge-fail">✕ FAILED</span>'
                    st.markdown(f"""
                        <div style="background:#131822; padding:12px; border-radius:12px; margin-bottom:8px; border:1px solid #1f2736;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#ffffff; font-size:15px;">{r['exercise_name']}</b>
                                {badge}
                            </div>
                            <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                                Sets: <b>{r['sets_done']}/{r['sets_target']}</b> | Reps: <b>{r['reps_done']}/{r['reps_target']}</b> | Load: <b>{r['weight_added']} kg</b> | {r['date']}
                            </div>
                            <div style="color:#64748b; font-size:11px; margin-top:2px;">Notes: {r['notes'] or 'Standard form'}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No exercise logs recorded yet. Add your first set on the left!")

# ==============================================================================
# MODULE 4: 30 / 90 DAYS CALISTHENICS CHALLENGE
# ==============================================================================
elif active_tab == "🏆 30 / 90 Days Transformation":
    st.markdown('<p class="hero-title">Transformation Challenge Matrix</p>', unsafe_allow_html=True)
    st.caption("Stay consistent with daily prescribed routines and track completion streaks.")

    challenge_mode = st.radio(
        "Select Crucible Track", 
        ["30-Day Foundation Challenge", "90-Day Elite Beast Challenge"], 
        horizontal=True
    )

    spec = CHALLENGE_SCHEDULE[challenge_mode]
    total_days = spec["days"]
    routines = spec["routine"]

    completed_records = pd.read_sql(
        "SELECT day_number FROM challenge_progress WHERE challenge_name = ? AND completed = 1", 
        conn, 
        params=(challenge_mode,)
    )
    completed_days_set = set(completed_records["day_number"].tolist())
    completion_count = len(completed_days_set)
    progress_ratio = completion_count / float(total_days)

    col_p1, col_p2 = st.columns([1.2, 2])
    with col_p1:
        st.markdown(f'''
            <div class="athlete-card" style="text-align:center;">
                <div class="metric-sub">CRUCIBLE COMPLETION</div>
                <div class="metric-hero-val" style="color:#38bdf8; font-size:40px; margin-top:8px;">
                    {completion_count} <span style="font-size:18px; color:#64748b;">/ {total_days} Days</span>
                </div>
                <div style="margin-top:10px; font-weight:700; color:#10b981;">{int(progress_ratio * 100)}% Finished</div>
            </div>
        ''', unsafe_allow_html=True)
        st.progress(progress_ratio)

    with col_p2:
        with st.container(border=True):
            st.markdown("##### 🎯 Daily Protocol Check-in")
            selected_day = st.number_input("Select Day to Log", min_value=1, max_value=total_days, value=min(completion_count + 1, total_days))
            prescribed_routine = routines[(selected_day - 1) % len(routines)]
            
            st.markdown(f"**Day {selected_day} Assignment:**")
            st.info(f"⚡ {prescribed_routine}")

            if selected_day in completed_days_set:
                st.success(f"✓ Day {selected_day} is already completed!")
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

# ==============================================================================
# MODULE 5: FINANCIAL LEDGER
# ==============================================================================
elif active_tab == "💰 Financial Ledger":
    st.markdown('<p class="hero-title">Financial Transaction Ledger</p>', unsafe_allow_html=True)
    
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
