import streamlit as st
import time
import os
import glob
import pandas as pd
import datetime
from dotenv import load_dotenv
from gemini_utils import get_gemini_response, analyze_audio_with_gemini
from db_utils import (init_db, get_recent_coughs, clear_db, 
                      get_daily_counts, get_hourly_counts_today,
                      get_total_count, get_today_count, get_weekly_counts)

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Smart Cough Monitor", page_icon="🩺", layout="wide")

# ==============================
# CUSTOM CSS - PREMIUM STYLING
# ==============================
st.markdown("""
<style>
    /* ===== GOOGLE FONT ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== MAIN BACKGROUND ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1321 100%);
    }
    
    /* ===== HEADER STYLING ===== */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.08), rgba(255, 107, 107, 0.08));
        border-radius: 16px;
        border: 1px solid rgba(78, 205, 196, 0.15);
        backdrop-filter: blur(10px);
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4ECDC4, #44B9F0, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8B95A5;
        font-size: 0.95rem;
        font-weight: 400;
    }
    
    /* ===== GLASS CARD ===== */
    .glass-card {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(78, 205, 196, 0.12);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(78, 205, 196, 0.3);
        box-shadow: 0 4px 20px rgba(78, 205, 196, 0.08);
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: linear-gradient(145deg, rgba(26, 31, 46, 0.8), rgba(20, 25, 38, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    .metric-label {
        color: #8B95A5;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FAFAFA;
    }
    .metric-value.teal { color: #4ECDC4; }
    .metric-value.coral { color: #FF6B6B; }
    .metric-value.gold { color: #FFD93D; }
    .metric-value.blue { color: #44B9F0; }
    .metric-delta-up { color: #FF6B6B; font-size: 0.8rem; }
    .metric-delta-down { color: #4ECDC4; font-size: 0.8rem; }
    
    /* ===== STATUS BADGES ===== */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-recording {
        background: rgba(255, 107, 107, 0.15);
        border: 1px solid rgba(255, 107, 107, 0.4);
        color: #FF6B6B;
        animation: pulse 1.5s infinite;
    }
    .badge-ready {
        background: rgba(255, 217, 61, 0.15);
        border: 1px solid rgba(255, 217, 61, 0.4);
        color: #FFD93D;
    }
    .badge-success {
        background: rgba(78, 205, 196, 0.15);
        border: 1px solid rgba(78, 205, 196, 0.4);
        color: #4ECDC4;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ===== SECTION HEADERS ===== */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FAFAFA;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(78, 205, 196, 0.2);
    }
    
    /* ===== CHART CONTAINERS ===== */
    .chart-container {
        background: rgba(26, 31, 46, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1rem;
        margin: 0.5rem 0 1.5rem 0;
    }
    
    /* ===== TABLE STYLING ===== */
    .stTable table {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    .stTable th {
        background: rgba(78, 205, 196, 0.1) !important;
        color: #4ECDC4 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    .stTable td {
        font-size: 0.85rem !important;
        color: #C8D0DB !important;
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(26, 31, 46, 0.5);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #8B95A5;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(78, 205, 196, 0.15) !important;
        color: #4ECDC4 !important;
        border-color: transparent !important;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0d1321 100%);
        border-right: 1px solid rgba(78, 205, 196, 0.1);
    }
    [data-testid="stSidebar"] .stButton button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    
    /* ===== INSIGHT CARD ===== */
    .insight-box {
        background: linear-gradient(145deg, rgba(26, 31, 46, 0.7), rgba(20, 25, 38, 0.5));
        border-left: 3px solid #4ECDC4;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .insight-box.warning {
        border-left-color: #FFD93D;
    }
    .insight-box.danger {
        border-left-color: #FF6B6B;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border-color: rgba(78, 205, 196, 0.1) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* ===== SMOOTH SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(78, 205, 196, 0.3);
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize DB
try:
    init_db()
except Exception as e:
    st.error(f"Database Error: {e}")

# ==============================
# SESSION STATE
# ==============================
if 'last_id' not in st.session_state:
    st.session_state.last_id = -1
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analyzed_file' not in st.session_state:
    st.session_state.analyzed_file = None

# ==============================
# HEADER
# ==============================
st.markdown("""
<div class="main-header">
    <h1>🩺 Smart AI Cough Monitor</h1>
    <p>IoT Connected Health System • Real-Time Tracking • AI-Powered Analysis</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.markdown("## ⚙️ Controls")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 Recording")

# Check recording status
is_recording = False
if os.path.exists("recording_status.txt"):
    try:
        with open("recording_status.txt", "r") as f:
            rec_status = f.read().strip()
        if rec_status == "START":
            is_recording = True
    except:
        pass

if is_recording:
    st.sidebar.markdown('<span class="badge badge-recording">● RECORDING</span>', unsafe_allow_html=True)
    if st.sidebar.button("⬛ Stop Recording", use_container_width=True):
        with open("recording_status.txt", "w") as f:
            f.write("STOP")
        time.sleep(1)
        st.rerun()
else:
    if st.sidebar.button("🔴 Start Recording", use_container_width=True):
        with open("recording_status.txt", "w") as f:
            f.write("START")
        st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("🗑️ Clear History", use_container_width=True):
    clear_db()
    st.session_state.last_id = -1
    st.session_state.analysis_result = None
    st.session_state.analyzed_file = None
    for f in glob.glob('*.wav') + glob.glob('manual_record_*.wav'):
        try:
            os.remove(f)
        except:
            pass
    st.rerun()

# System status
st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 System Status")
total = get_total_count()
today = get_today_count()
st.sidebar.markdown(f"**Today:** {today} events")
st.sidebar.markdown(f"**Total:** {total} events")
st.sidebar.markdown(f"**Status:** {'🔴 Recording' if is_recording else '🟢 Ready'}")

# ==============================
# TABS
# ==============================
tab_monitor, tab_tracker = st.tabs(["📡  Live Monitor", "📊  Cough Tracker"])

# ==============================
# TAB 1: LIVE MONITOR
# ==============================
with tab_monitor:
    
    if is_recording:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(255, 107, 107, 0.4); text-align: center;">
            <span class="badge badge-recording">● REC</span>
            <span style="color: #FF6B6B; font-weight: 600; margin-left: 10px;">
                RECORDING IN PROGRESS — Speak into the microphone
            </span>
        </div>
        """, unsafe_allow_html=True)

    recent_data = get_recent_coughs(10)

    if recent_data:
        latest = recent_data[0]
        current_id = latest[0]

        # --- Custom Metrics Row ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Latest Detection</div>
                <div class="metric-value teal">{latest[2]}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Confidence</div>
                <div class="metric-value gold">{latest[3]*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Date</div>
                <div class="metric-value blue">{latest[1].split(" ")[0]}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- New Event ---
        if current_id != st.session_state.last_id:
            st.session_state.last_id = current_id
            st.session_state.analysis_result = None
            st.session_state.analyzed_file = None

        # --- Audio Analysis ---
        if latest[2] == "Audio Recorded":
            st.markdown("""
            <div class="glass-card">
                <span class="badge badge-ready">● READY</span>
                <span style="color: #FFD93D; font-weight: 600; margin-left: 10px;">
                    New Audio Clip Ready for Analysis
                </span>
            </div>
            """, unsafe_allow_html=True)

            list_of_files = glob.glob('*.wav') + glob.glob('manual_record_*.wav')
            list_of_files = list(set(list_of_files))

            latest_file = None
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
            else:
                st.error("No audio files found!")

            if latest_file and st.session_state.analysis_result is None:
                if st.button("🔍 Analyze with AI Doctor", type="primary", use_container_width=True):
                    with st.spinner("🤖 AI Doctor is analyzing the audio..."):
                        try:
                            analysis = analyze_audio_with_gemini(latest_file, api_key)
                            st.session_state.analysis_result = analysis
                            st.session_state.analyzed_file = latest_file
                            st.rerun()
                        except Exception as e:
                            st.error(f"Analysis Error: {e}")

            if st.session_state.analysis_result:
                st.markdown(f"""
                <div class="glass-card" style="border-color: rgba(78, 205, 196, 0.3);">
                    <span class="badge badge-success">✓ COMPLETE</span>
                    <span style="color: #4ECDC4; font-weight: 600; margin-left: 10px;">
                        Analysis for {st.session_state.analyzed_file}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.analysis_result)

        elif latest[2] != "Audio Recorded" and "Cough" in latest[2]:
            st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(78, 205, 196, 0.3);">
                <span class="badge badge-success">✓ DETECTED</span>
                <span style="color: #4ECDC4; font-weight: 600; margin-left: 10px;">
                    {latest[2]}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # --- History Table ---
        st.markdown('<div class="section-title">📜 Recent Event History</div>', unsafe_allow_html=True)
        history_data = []
        for r in recent_data:
            history_data.append({
                "🕐 Time": r[1],
                "🏷️ Type": r[2],
                "📊 Confidence": f"{r[3]*100:.0f}%"
            })
        st.table(history_data)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎤</div>
            <div style="color: #8B95A5; font-size: 1.1rem;">No data received yet</div>
            <div style="color: #5A6474; font-size: 0.9rem; margin-top: 0.5rem;">
                Click <strong style="color: #4ECDC4;">Start Recording</strong> in the sidebar to begin
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================
# TAB 2: COUGH TRACKER
# ==============================
with tab_tracker:
    
    st.markdown('<div class="section-title">📊 Cough Tracking Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #8B95A5; margin-top: -0.8rem; margin-bottom: 1.5rem;">Track your cough patterns over time to monitor health trends</p>', unsafe_allow_html=True)
    
    # --- Summary Metrics ---
    total_count = get_total_count()
    today_count = get_today_count()
    daily_data = get_daily_counts(7)
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_count = 0
    for day, count in daily_data:
        if day == yesterday:
            yesterday_count = count
    
    if yesterday_count > 0:
        delta = today_count - yesterday_count
        delta_html = f'<div class="{"metric-delta-up" if delta > 0 else "metric-delta-down"}">{"↑" if delta > 0 else "↓"} {abs(delta)} from yesterday</div>'
    else:
        delta_html = ""
    
    tracking_since = daily_data[0][0] if daily_data else "—"
    days_tracked = len(daily_data)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Today's Coughs</div>
            <div class="metric-value coral">{today_count}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Recorded</div>
            <div class="metric-value teal">{total_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tracking Since</div>
            <div class="metric-value blue" style="font-size: 1.1rem;">{tracking_since}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Days Tracked</div>
            <div class="metric-value gold">{days_tracked}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Daily Trend Chart ---
    st.markdown('<div class="section-title">📈 Daily Cough Count — Last 7 Days</div>', unsafe_allow_html=True)
    
    if daily_data:
        today_date = datetime.datetime.now().date()
        all_days = {}
        for i in range(6, -1, -1):
            day = (today_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            all_days[day] = 0
        for day, count in daily_data:
            if day in all_days:
                all_days[day] = count
        
        df_daily = pd.DataFrame({
            "Date": list(all_days.keys()),
            "Coughs": list(all_days.values())
        }).set_index("Date")
        
        st.bar_chart(df_daily, color="#FF6B6B", height=300)
        
        # Trend analysis
        counts = list(all_days.values())
        if len(counts) >= 2 and sum(counts) > 0:
            recent_avg = sum(counts[-3:]) / 3
            older_avg = sum(counts[:4]) / max(len(counts[:4]), 1)
            
            if recent_avg > older_avg * 1.2:
                st.markdown("""
                <div class="insight-box danger">
                    <strong>⚠️ Trend: Increasing</strong> — Your cough frequency is rising. Consider consulting a doctor if it persists.
                </div>
                """, unsafe_allow_html=True)
            elif recent_avg < older_avg * 0.8:
                st.markdown("""
                <div class="insight-box">
                    <strong>✅ Trend: Improving</strong> — Your cough frequency is decreasing. Keep it up!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box warning">
                    <strong>➡️ Trend: Stable</strong> — Your cough frequency is consistent.
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem; color: #5A6474;">
            No data yet — start recording to see daily trends
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Two Column: Hourly + Weekly ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-title">🕐 Today\'s Timeline</div>', unsafe_allow_html=True)
        
        hourly_data = get_hourly_counts_today()
        
        if hourly_data:
            all_hours = {f"{h:02d}:00": 0 for h in range(24)}
            for hour, count in hourly_data:
                all_hours[f"{hour:02d}:00"] = count
            
            df_hourly = pd.DataFrame({
                "Hour": list(all_hours.keys()),
                "Coughs": list(all_hours.values())
            }).set_index("Hour")
            
            st.area_chart(df_hourly, color="#4ECDC4", height=250)
            
            peak_hour, peak_count = max(hourly_data, key=lambda x: x[1])
            st.markdown(f"""
            <div class="insight-box">
                <strong>🕐 Peak Hour:</strong> {peak_hour:02d}:00 ({peak_count} coughs)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem; color: #5A6474;">
                No coughs recorded today
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="section-title">📅 Weekly Summary</div>', unsafe_allow_html=True)
        
        weekly_data = get_weekly_counts(4)
        
        if weekly_data:
            df_weekly = pd.DataFrame(weekly_data, columns=["Week", "Coughs"]).set_index("Week")
            st.line_chart(df_weekly, color="#FFD93D", height=250)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem; color: #5A6474;">
                Not enough data for weekly summary
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Health Insights ---
    st.markdown('<div class="section-title">💡 Health Insights</div>', unsafe_allow_html=True)
    
    if total_count > 0:
        avg_per_day = total_count / max(len(daily_data), 1)
        
        ins_left, ins_right = st.columns(2)
        
        with ins_left:
            st.markdown(f"""
            <div class="glass-card">
                <div style="color: #4ECDC4; font-weight: 700; font-size: 1rem; margin-bottom: 0.8rem;">📊 Statistics</div>
                <div style="color: #C8D0DB; line-height: 2;">
                    Average: <strong style="color: #FFD93D;">{avg_per_day:.1f}</strong> coughs/day<br>
                    Today: <strong style="color: #FF6B6B;">{today_count}</strong> coughs<br>
                    Total tracked: <strong style="color: #4ECDC4;">{total_count}</strong> events
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with ins_right:
            if avg_per_day > 20:
                severity_color = "#FF6B6B"
                severity_text = "HIGH — Please consult a doctor"
                severity_icon = "🔴"
            elif avg_per_day > 10:
                severity_color = "#FFD93D"
                severity_text = "MODERATE — Monitor closely"
                severity_icon = "🟡"
            else:
                severity_color = "#4ECDC4"
                severity_text = "NORMAL — Within range"
                severity_icon = "🟢"
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="color: #4ECDC4; font-weight: 700; font-size: 1rem; margin-bottom: 0.8rem;">🏥 Health Advisory</div>
                <div style="color: {severity_color}; font-weight: 600; margin-bottom: 0.8rem;">
                    {severity_icon} {severity_text}
                </div>
                <div style="color: #8B95A5; font-size: 0.85rem; line-height: 1.8;">
                    See a doctor if:<br>
                    • Cough persists &gt; 3 weeks<br>
                    • Frequency is increasing<br>
                    • Fever or breathing difficulty
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="color: #5A6474;">Start recording coughs to see health insights</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================
# AUTO-REFRESH
# ==============================
if st.session_state.analysis_result is None and not is_recording:
    time.sleep(3)
    st.rerun()
elif is_recording:
    time.sleep(1)
    st.rerun()
