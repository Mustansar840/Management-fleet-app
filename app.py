# ==============================================================================
# ☢️ RIYADH FLEET MANAGER - TITAN LOG MASTER (V15.0) - GOOGLE SHEETS VERSION
# ==============================================================================
# FEATURES:
# 1. DUAL HISTORY: View 'Shift Logs' AND 'Transaction Logs' separately.
# 2. AUTO-SAVE: All money moves saved to Google Sheets.
# 3. DRIVER VIEW: Drivers see their own money history.
# 4. ADVANCE SYSTEM: Complete advance management with approval flow.
# 5. DURATION CALCULATION: Automatic shift duration calculation.
# 6. NEON ANALYTICS: Advanced graphs with historical data.
# ==============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px  # Ensure this is imported at top
import os
import time
import json
import uuid
import sys
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. KERNEL SETUP
# ==========================================
sys.tracebacklimit = 0

st.set_page_config(
    page_title="NOMORE_MANAGEMENT",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. VISUAL ENGINE (THE HACKER LOOK)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700&display=swap');

    /* --- BACKGROUND --- */
    .stApp {
        background-color: #000000;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 255, 65, 0.02) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(0, 100, 255, 0.02) 0%, transparent 20%),
            linear-gradient(0deg, transparent 24%, rgba(0, 255, 65, .03) 25%, rgba(0, 255, 65, .03) 26%, transparent 27%, transparent 74%, rgba(0, 255, 65, .03) 75%, rgba(0, 255, 65, .03) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 255, 65, .03) 25%, rgba(0, 255, 65, .03) 26%, transparent 27%, transparent 74%, rgba(0, 255, 65, .03) 75%, rgba(0, 255, 65, .03) 76%, transparent 77%, transparent);
        background-size: 50px 50px;
        color: #00ff41;
        font-family: 'Share Tech Mono', monospace;
    }

    /* --- HEADERS --- */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        letter-spacing: 1px;
    }

    /* --- INPUTS --- */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input {
        background-color: #000500 !important; 
        color: #00ff41 !important;
        border: 1px solid #004400 !important;
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: 4px !important;
    }

    /* --- BUTTONS --- */
    div.stButton > button {
        background: linear-gradient(135deg, #001a00 0%, #000 100%) !important;
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important;
        letter-spacing: 2px !important; 
        text-transform: uppercase !important; 
        padding: 12px 24px !important;
        transition: all 0.3s ease !important; 
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        border-radius: 4px !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00ff41 0%, #007722 100%) !important;
        color: #000000 !important; 
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* --- LOG ROWS --- */
    .terminal-row {
        background: rgba(0, 20, 0, 0.8);
        border-bottom: 1px solid #333;
        padding: 12px 15px; 
        display: flex; 
        justify-content: space-between;
        align-items: center;
        font-size: 14px; 
        transition: all 0.2s ease;
        border-left: 2px solid transparent;
        margin: 2px 0;
        border-radius: 2px;
    }
    .terminal-row:hover { 
        background: rgba(0, 50, 0, 0.9); 
        border-left: 3px solid #00ff41; 
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1);
    }
    
    .t-date { color: #888; width: 15%; font-size: 12px; }
    .t-main { color: #fff; width: 25%; font-weight: bold; font-family: 'Orbitron', sans-serif; }
    .t-sub { color: #0088ff; width: 30%; font-size: 12px; }
    .t-val { color: #00ff41; width: 15%; text-align: right; font-weight: bold; font-size: 14px; }
    .t-duration { color: #ffaa00; width: 15%; text-align: center; font-size: 12px; font-family: 'Share Tech Mono'; }
    
    .t-advance { border-left: 3px solid #0088ff !important; }
    .t-cash { border-left: 3px solid #00ff41 !important; }
    .t-ceo { border-left: 3px solid #ff0055 !important; }

    /* --- HUD CARDS --- */
    .hud-card {
        background: rgba(5, 10, 5, 0.95); 
        border: 1px solid #003300;
        padding: 15px; 
        margin-bottom: 10px; 
        border-left: 4px solid #333;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .hud-active {
        border-color: #00ff41; 
        border-left: 4px solid #00ff41;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.1);
        animation: glow 3s infinite alternate;
    }
    @keyframes glow { 
        from { box-shadow: 0 0 10px rgba(0,255,65,0.1); } 
        to { box-shadow: 0 0 25px rgba(0,255,65,0.4); } 
    }

    /* --- VAULT BOX --- */
    .vault-box {
        background: linear-gradient(135deg, rgba(0,10,0,0.9) 0%, rgba(0,5,0,0.95) 100%);
        border: 1px solid #111; 
        padding: 20px; 
        text-align: center;
        border-radius: 8px;
        box-shadow: inset 0 0 30px rgba(0,255,65,0.05),
                    0 5px 15px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    .vault-box:hover {
        transform: translateY(-5px);
        box-shadow: inset 0 0 30px rgba(0,255,65,0.1),
                    0 8px 25px rgba(0,0,0,0.7);
    }
    .v-lbl { 
        font-size: 12px; 
        color: #aaa; 
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .v-val { 
        font-size: 28px; 
        font-weight: bold; 
        color: #fff; 
        text-shadow: 0 0 10px rgba(0,255,65,0.5);
        font-family: 'Orbitron', sans-serif;
    }

    /* --- DIGITAL RECEIPT --- */
    .receipt-box {
        font-family: 'Courier New', monospace;
        background: rgba(0, 5, 0, 0.95);
        border: 2px solid #00ff41;
        padding: 25px;
        color: #00ff41;
        text-align: left;
        margin: 20px 0;
        position: relative;
        border-radius: 8px;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);
    }
    .receipt-box::before { 
        content: "✅ TRANSACTION SUCCESSFUL"; 
        font-weight: bold; 
        display: block; 
        margin-bottom: 15px;
        text-align: center;
        font-size: 16px;
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }

    /* --- NOTIFICATION BADGE --- */
    .notification-badge {
        background: #ff0055;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(0,10,0,0.8);
        padding: 5px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0,20,0,0.5);
        color: #888;
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
        font-family: 'Orbitron', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0,255,65,0.1) !important;
        color: #00ff41 !important;
        border-bottom: 2px solid #00ff41 !important;
    }

    /* --- PROGRESS BAR --- */
    .stProgress > div > div > div > div {
        background-color: #00ff41 !important;
        background-image: linear-gradient(90deg, #00ff41, #007722) !important;
    }

    /* --- METRIC CARDS --- */
    [data-testid="metric-container"] {
        background-color: rgba(0,15,0,0.9) !important;
        border: 1px solid #004400 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }

    /* Hide Streamlit elements */
    header, footer {visibility: hidden;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GLOBAL CONFIG
# ==========================================
DRIVERS = ["Faryad", "Parvaiz", "Ijaz", "Saood", "Sunny","Azeem"] 
CARS = ["Car Boult (Black)", "Car Jenny (White)", "Car Max (New)"]

DRIVER_PHONES = {
    "Faryad": "0577451015", 
    "Parvaiz": "0597098541",
    "Ijaz": "0574307850", 
    "Saood": "050XXXX104", 
    "Sunny": "0510446075",
    "Azeem": "050XXXX105"
}

BASE_SALARY = 2000
MONTHLY_TARGET = 6000
DUTY_HOURS_LIMIT = 12

USERS_DB = {
    # 👇 ADMIN (Mustansar) - Full Control
    "mustansar":   {"pass": "nomore", "role": "admin",  "name": "Mustansar"},
    
    # 👇 CEO (Abdul Razzaq) - View Only
    "ceo": {"pass": "ceo786",   "role": "ceo",    "name": "Abdul Razzaq"},
    
    # 👇 DRIVERS
    "sunny":       {"pass": "0000",     "role": "driver", "name": "Sunny"},
    "faryad":      {"pass": "1111",     "role": "driver", "name": "Faryad"},
    "parvaiz":     {"pass": "2222",     "role": "driver", "name": "Parvaiz"},
    "ijaz":        {"pass": "3333",     "role": "driver", "name": "Ijaz"},
    "saood":       {"pass": "4444",     "role": "driver", "name": "Saood"},
    "azeem":       {"pass": "5555",     "role": "driver", "name": "Azeem"},
}
FILES = {
    "sessions": "active_sessions.json", 
    "data": "shifts_log", 
    "trans": "transactions_log"
}

# ==========================================
# 4. GOOGLE SHEETS DATABASE ENGINE (ANTI-DELETE & RETRY MODE)
# ==========================================
@st.cache_resource
def get_google_sheet_client():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def load_db(key):
    client = get_google_sheet_client()
    if not client: 
        st.error("❌ Database Disconnected!")
        st.stop()
    
    sheet_name = "FLEET_DB_V15"
    
    for attempt in range(3):
        try:
            sh = client.open(sheet_name)
            wk_name = FILES[key]
            worksheet = sh.worksheet(wk_name)
            
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if key == 'data':
                req_cols = ["Shift_ID", "Driver", "Car", "Status", "Approval_Status", 
                            "Start_Time", "End_Time", "Duration", "Total_Earnings", 
                            "Start_Wallet", "End_Wallet", "Cash_Collected", 
                            "Start_Fuel", "End_Fuel"]
            else:
                req_cols = ["Trans_ID", "Date", "Driver", "Type", "Amount", 
                            "Method", "Notes", "Approval_Status", "Source"]

            for c in req_cols:
                if c not in df.columns: df[c] = ""
            
            if not df.empty:
                cols_num = ['Total_Earnings', 'Duration', 'Amount']
                for c in cols_num:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                if key == 'data':
                    for d_col in ['Start_Time', 'End_Time']:
                        if d_col in df.columns:
                            df[d_col] = pd.to_datetime(df[d_col], errors='coerce')
                elif key == 'trans':
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    
            return df

        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(2)
                continue
            else:
                st.error(f"❌ Read Error: {str(e)}")
                st.stop()
    
    return pd.DataFrame()

def save_db(key, df):
    if df.empty: return False

    client = get_google_sheet_client()
    if not client: 
        st.error("Database connection failed!")
        return False
    
    sheet_name = "FLEET_DB_V15"
    
    for attempt in range(3):
        try:
            sh = client.open(sheet_name)
            wk_name = FILES[key]
            worksheet = sh.worksheet(wk_name)
            
            df_save = df.copy()
            
            target_cols = ['Start_Time', 'End_Time', 'Date']
            for col in target_cols:
                if col in df_save.columns:
                    df_save[col] = df_save[col].astype(str)
                    df_save[col] = df_save[col].replace(['NaT', 'nan', '<NA>', 'None'], '')

            df_save = df_save.fillna('')
            
            data_to_write = [df_save.columns.values.tolist()] + df_save.values.tolist()
            
            worksheet.update(data_to_write)
            worksheet.resize(rows=len(data_to_write))
            
            load_db.clear()
            return True
            
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(3)
                continue
            else:
                st.error(f"❌ Save Failed: {str(e)}")
                return False
                
    st.error("❌ Server Busy (Google Quota). Please wait 1 min.")
    return False

# ==========================================
# 5. SESSION MANAGER
# ==========================================
def create_session(user):
    s = {}
    try: 
        if os.path.exists(FILES['sessions']):
            s = json.load(open(FILES['sessions']))
    except: 
        pass
    
    token = str(uuid.uuid4())
    s[token] = {
        "username": user, 
        "expiry": (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(FILES['sessions'], 'w') as f: 
        json.dump(s, f)
    return token

def check_session():
    token = st.query_params.get("session", None)
    if not token or not os.path.exists(FILES['sessions']): 
        return None
    
    try:
        s = json.load(open(FILES['sessions']))
        if token in s:
            expiry = datetime.strptime(s[token]['expiry'], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry:
                u = s[token]['username']
                return USERS_DB.get(u, None)
    except: 
        pass
    
    return None

def logout(): 
    st.query_params.clear()
    st.rerun()

# ==========================================
# 6. UI: LOGIN
# ==========================================
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
        <div style="border:2px solid #00ff41; padding:40px; background:rgba(0,0,0,0.95); 
                    text-align:center; border-radius:10px; box-shadow:0 0 50px rgba(0,255,65,0.3);">
            <h1 style="color:#fff; font-family:'Orbitron'; font-size:32px; margin-bottom:10px;">
                ⚡ NOMORE\nMANAGEMENT
            </h1>
            <p style="color:#00ff41; font-family:'Share Tech Mono'; letter-spacing:2px;">
                SECURE OPERATING SYSTEM
            </p>
            <hr style="border-color:#004400; margin:20px 0;">
            <p style="color:#888; font-size:12px;">
                🔒 RESTRICTED ACCESS | AUTHORIZED PERSONNEL ONLY
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("log", clear_on_submit=True):
            st.markdown("<br>", unsafe_allow_html=True)
            u = st.text_input("**USER ID**", key="user_id").lower().strip()
            p = st.text_input("**ACCESS CODE**", type="password", key="pass")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button("🚀 INITIATE CONNECTION", use_container_width=True):
                    if u in USERS_DB and USERS_DB[u]["pass"] == p:
                        t = create_session(u)
                        st.query_params["session"] = t
                        st.rerun()
                    else:
                        st.error("⚠️ ACCESS DENIED: Invalid credentials")

# ==========================================
# 7. UI: DUAL HISTORY LOGS (FIXED DUPLICATE KEY ERROR)
# ==========================================
def render_history_logs(user, role, unique_key="default"):
    st.markdown("### 📜 HISTORY LOGS")
    
    # 👇 FIX: Widget Keys ab unique hongi (e.g., 'type_ceo_shift', 'type_driver')
    log_type = st.radio("TYPE", ["🚙 SHIFTS", "💸 TRANSACTIONS"], horizontal=True, key=f"log_type_{unique_key}")
    
    if "SHIFT" in log_type:
        df = load_db('data')
        
        valid = ['Completed', 'Pending_End', 'Complete']
        
        if role == "driver":
            logs = df[(df['Driver'] == user) & (df['Status'].isin(valid))]
        else:
            # 👇 FIX: Key added here too
            sel = st.selectbox("FILTER DRIVER", ["ALL"] + DRIVERS, key=f"filter_shift_{unique_key}")
            if sel == "ALL":
                logs = df[df['Status'].isin(valid)]
            else:
                logs = df[(df['Driver'] == sel) & (df['Status'].isin(valid))]
        
        if logs.empty: st.info("NO DATA"); return
        
        # Sort
        if 'Start_Time' in logs.columns:
            logs['Start_Time'] = pd.to_datetime(logs['Start_Time'], errors='coerce')
            logs = logs.sort_values(by="Start_Time", ascending=False)
        
        st.markdown("""<div style="display:flex;justify-content:space-between;color:#888;font-size:12px;padding:5px;">
            <div class="t-date">DATE</div>
            <div class="t-main">UNIT</div>
            <div class="t-sub">TIMELINE</div>
            <div class="t-duration">STATUS</div>
            <div class="t-val">REV</div>
        </div>""", unsafe_allow_html=True)
        
        for _, r in logs.iterrows():
            try:
                if pd.notna(r['Start_Time']):
                    d_str = r['Start_Time'].strftime("%d-%b")
                    t_str = r['Start_Time'].strftime("%I:%M%p")
                else:
                    d_str = "Unknown"; t_str = "--"
                
                if pd.notna(r['End_Time']): 
                    e_str = pd.to_datetime(r['End_Time']).strftime("%I:%M%p")
                else: 
                    e_str = "--"
                
                stat = r['Status']
                col = "#ffaa00" if "Pending" in stat else "#00ff41"
                
                st.markdown(f"""<div class="terminal-row"><div class="t-date" style="color:#fff">{d_str}</div>
                <div class="t-main">{str(r['Car']).split(' ')[1]}</div><div class="t-sub">{t_str} ➔ {e_str}</div>
                <div class="t-duration" style="color:{col}">{stat}</div><div class="t-val">{float(r['Total_Earnings']):,.0f}</div></div>""", unsafe_allow_html=True)
            except: continue

    else:
        df = load_db('trans')
        
        if role == "driver": logs = df[df['Driver'] == user]
        else:
            # 👇 FIX: Key added here too
            sel = st.selectbox("FILTER DRIVER", ["ALL"] + DRIVERS, key=f"filter_trans_{unique_key}")
            logs = df if sel == "ALL" else df[df['Driver'] == sel]
            
        if logs.empty: st.info("NO DATA"); return
        
        if 'Date' in logs.columns:
            logs['Date'] = pd.to_datetime(logs['Date'], errors='coerce')
            logs = logs.sort_values(by="Date", ascending=False)
            
        st.markdown("""<div style="display:flex;justify-content:space-between;color:#888;font-size:12px;padding:5px;">
            <div class="t-date">DATE</div>
            <div class="t-main">TYPE</div>
            <div class="t-sub">NOTE</div>
            <div class="t-sub">STATUS</div>
            <div class="t-val">AMT</div>
        </div>""", unsafe_allow_html=True)
        
        for _, r in logs.iterrows():
            try:
                d_str = r['Date'].strftime("%d-%b") if pd.notna(r['Date']) else "N/A"
                raw_type = r['Type']
                
                # Label Logic
                display_label = raw_type
                if raw_type == "Received":
                    display_label = "💸 SENT" if role == "driver" else "📥 RECEIVED"
                elif raw_type == "Advance":
                    display_label = "💰 RECEIVED" if role == "driver" else "📤 SENT (ADV)"
                
                col = "#0088ff" if "Advance" in raw_type else "#00ff41"

                st.markdown(f"""<div class="terminal-row"><div class="t-date" style="color:#fff">{d_str}</div>
                <div class="t-main" style="color:{col}">{display_label}</div>
                <div class="t-sub">{str(r['Notes'])[:15]}..</div>
                <div class="t-sub">{r['Approval_Status']}</div><div class="t-val" style="color:{col}">{r['Amount']}</div></div>""", unsafe_allow_html=True)
            except: continue
# ==========================================
# 8. UI: DRIVER HUD & TIMER
# ==========================================
def render_driver_hud(driver):
    df = load_db('data')
    
    comp = df[(df['Driver'] == driver) & (df['Status'] == 'Completed') & (df['Approval_Status'] == 'Approved')]
    
    rev = comp['Total_Earnings'].sum() if not comp.empty else 0
    
    ratio = min(rev / MONTHLY_TARGET, 1.0) if MONTHLY_TARGET > 0 else 0
    sal = BASE_SALARY * ratio
    
    days_worked = len(comp['Start_Time'].dt.date.unique()) if not comp.empty else 0
    
    st.markdown(f"### 👤 CMD╰┈➤ {driver.upper()}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(ratio, text=f"TARGET PROGRESS: {ratio*100:.1f}%")
    with col2:
        st.metric("DAYS", days_worked)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #00ff41;">
            <div class="v-lbl">TOTAL REVENUE</div>
            <div class="v-val">{rev:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">SAR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #0088ff;">
            <div class="v-lbl">SALARY EARNED</div>
            <div class="v-val" style="color:#0088ff">{sal:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">SAR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #ff0055;">
            <div class="v-lbl">LEFT TO GO</div>
            <div class="v-val" style="color:#ff0055">{max(MONTHLY_TARGET - rev, 0):,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">SAR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        avg_rev = rev / days_worked if days_worked > 0 else 0
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #ffaa00;">
            <div class="v-lbl">DAILY AVG</div>
            <div class="v-val" style="color:#ffaa00">{avg_rev:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">SAR</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# ⏱️ UI: MISSION TIMER (RIYADH TIME FIX)
# ==========================================
def render_js_timer(driver):
    df = load_db('data')
    active = df[(df['Driver'] == driver) & (df['Status'] == 'Active')]
    
    if active.empty:
        return
    
    try:
        # 1. Get Start Time from DB
        start_time = pd.to_datetime(active.iloc[0]['Start_Time'])
        
        # 2. Get Current Time (Fixed for Riyadh)
        # Server UTC par hota hai, usme 3 ghantay add karein taake Riyadh ka waqt ban jaye
        server_now = datetime.utcnow()
        riyadh_now = server_now + timedelta(hours=3) 
        
        # 3. Calculate Difference
        # Ab Riyadh ke waqt se Start Time minus karein
        delta = riyadh_now - start_time
        elapsed_seconds = int(delta.total_seconds())
        
        # Safety: Agar phir b time negative ho, to 0 kar do (Crash na ho)
        if elapsed_seconds < 0:
            elapsed_seconds = 0
        
        limit_seconds = DUTY_HOURS_LIMIT * 3600
        progress = min(elapsed_seconds / limit_seconds, 1.0)
        
        # 4. Python Side Format (Backup Display)
        h = elapsed_seconds // 3600
        m = (elapsed_seconds % 3600) // 60
        s = elapsed_seconds % 60
        
        # 5. HTML & JS
        html = f"""
        <div style="background:rgba(0,10,0,0.9); border:2px solid #00ff41; padding:20px; 
                    text-align:center; margin-bottom:20px; border-radius:10px;
                    box-shadow:0 0 30px rgba(0,255,65,0.3);">
            <div style="font-size:11px; color:#888; margin-bottom:5px; letter-spacing:1px; font-family:'Share Tech Mono';">
                ⏱️ ACTIVE MISSION TIMER
            </div>
            
            <div id="clock" style="font-size:48px; font-weight:bold; color:#fff; 
                    font-family:'Orbitron', sans-serif; text-shadow:0 0 10px rgba(0,255,65,0.5);">
                {h:02d}:{m:02d}:{s:02d}
            </div>
            
            <div style="background:rgba(0,20,0,0.8); height:8px; width:100%; margin-top:15px; 
                    border-radius:4px; overflow:hidden;">
                <div id="bar" style="height:100%; width:{progress*100}%; 
                     background:linear-gradient(90deg, #00ff41, #007722); 
                     transition:width 1s ease;"></div>
            </div>
            <div id="msg" style="color:#00ff41; font-size:12px; margin-top:8px; 
                    font-family:'Share Tech Mono';">
                {('⚠️ OVERTIME ALERT' if elapsed_seconds > limit_seconds else '● ACTIVE TRACKING')}
            </div>
        </div>

        <script>
        var totalSeconds = {elapsed_seconds};
        var limit = {limit_seconds};

        setInterval(function() {{
            totalSeconds++;
            
            var hours = Math.floor(totalSeconds / 3600);
            var minutes = Math.floor((totalSeconds % 3600) / 60);
            var seconds = totalSeconds % 60;

            // Format numbers to always show 2 digits (e.g., 05 instead of 5)
            var hStr = hours < 10 ? "0" + hours : hours;
            var mStr = minutes < 10 ? "0" + minutes : minutes;
            var sStr = seconds < 10 ? "0" + seconds : seconds;

            var clock = document.getElementById("clock");
            if (clock) {{
                clock.innerHTML = hStr + ":" + mStr + ":" + sStr;
            }}

            var bar = document.getElementById("bar");
            if (bar) {{
                var pct = Math.min((totalSeconds / limit) * 100, 100);
                bar.style.width = pct + "%";
                
                if (totalSeconds > limit) {{
                    bar.style.background = "linear-gradient(90deg, #ff0055, #aa0033)";
                    document.getElementById("clock").style.color = "#ff0055";
                    document.getElementById("msg").innerHTML = "⚠️ OVERTIME LIMIT EXCEEDED";
                    document.getElementById("msg").style.color = "#ff0055";
                }}
            }}
        }}, 1000);
        </script>
        """
        st.components.v1.html(html, height=180)
        
    except Exception as e:
        st.error(f"Timer System Error: {str(e)}")
# ==========================================
# 9. UI: ADMIN & OPS
# ==========================================
def render_fleet(role):
    df = load_db('data')
    active = df[df['Status'] == 'Active']
    
    st.markdown("### 📡 FLEET RADAR")
    
    drivers = DRIVERS if role != "driver" else [d for d in DRIVERS if d in active['Driver'].values]
    
    if not drivers:
        st.info("🚫 NO ACTIVE UNITS DETECTED")
        return

    cols = st.columns(len(drivers)) if len(drivers) > 0 else [st.empty()]
    
    for i, d in enumerate(drivers):
        row = active[active['Driver'] == d]
        is_active = not row.empty
        
        car = row.iloc[0]['Car'].split(' ')[1] if is_active else "---"
        phone = DRIVER_PHONES.get(d, "N/A")
        
        if is_active:
            border_color = "#00ff41"
            border_width = "3px"
            status_color = "#00ff41"
            status_text = "🟢 LIVE"
            bg_anim = "box-shadow: 0 0 25px rgba(0,255,65,0.4);"
        else:
            border_color = "#ff0055"
            border_width = "2px"
            status_color = "#ff0055"
            status_text = "🔴 OFF-DUTY"
            bg_anim = "opacity: 0.8;"

        with cols[i]:
            st.markdown(f"""
            <div style="border:{border_width} solid {border_color}; background:rgba(0,10,0,0.8); 
                        padding:15px; border-radius:10px; text-align:center; {bg_anim} margin-bottom:10px;">
                <div style="font-size:18px; font-weight:bold; color:#fff; margin-bottom:5px;">{d}</div>
                <div style="background:#002200; color:#00ff41; padding:4px 8px; border-radius:5px; 
                            font-family:'Courier New'; font-weight:bold; font-size:14px; display:inline-block; margin-bottom:8px;">
                    📞 {phone}
                </div>
                <div style="color:#888; font-size:12px;">{car}</div>
                <div style="color:{status_color}; font-size:12px; margin-top:5px; font-weight:bold;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")

def render_manager_stats():
    df_s = load_db('data')
    df_t = load_db('trans')
    
    comp = df_s[df_s['Status'] == 'Completed']
    gross_rev = comp['Total_Earnings'].sum() if not comp.empty else 0
    
    if not df_t.empty:
        app = df_t[df_t['Approval_Status'] == 'Approved']
        
        rec = app[app['Type'] == 'Received']['Amount'].sum() if not app.empty else 0
        
        adv = app[app['Type'] == 'Advance']['Amount'].sum() if not app.empty else 0
        mgr_ceo = app[(app['Type'] == 'CEO_Transfer') & (app['Source'] == 'Manager')]['Amount'].sum() if not app.empty else 0
        
        expenses = app[app['Type'] == 'Expense']['Amount'].sum() if not app.empty else 0
        
        safe = rec - adv - mgr_ceo
        
    else:
        rec = adv = mgr_ceo = expenses = safe = 0
    
    st.markdown("### 💠 FINANCE CORE")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #00ff41">
            <div class="v-lbl">SAFE CASH</div>
            <div class="v-val">{safe:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">PHYSICAL CASH IN HAND</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #ffaa00">
            <div class="v-lbl">EXPENSES</div>
            <div class="v-val" style="color:#ffaa00">{expenses:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">CEO COST (WASH/REPAIR)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #0088ff">
            <div class="v-lbl">ADVANCES</div>
            <div class="v-val" style="color:#0088ff">{adv:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">GIVEN TO DRIVERS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class="vault-box" style="border-top:2px solid #ff0055">
            <div class="v-lbl">GROSS REVENUE</div>
            <div class="v-val" style="color:#ff0055">{gross_rev:,.0f}</div>
            <div style="font-size:10px; color:#888; margin-top:5px;">TOTAL WORK DONE</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

# ==========================================
# 🏆 UI: LIVE LEADERBOARD
# ==========================================
def render_leaderboard():
    df = load_db('data')
    
    comp = df[(df['Status'] == 'Completed') & (df['Approval_Status'] == 'Approved')]
    
    if comp.empty:
        st.info("WAITING FOR DATA...")
        return
    
    ranking = comp.groupby('Driver').agg(
        Total_Earnings=('Total_Earnings', 'sum'),
        Total_Shifts=('Shift_ID', 'count')
    ).reset_index()
    
    ranking = ranking.sort_values(by='Total_Earnings', ascending=False)
    st.markdown("### 🏆 ELITE DRIVER RANKING")
    
    fig = go.Figure(data=[
        go.Bar(
            x=ranking['Driver'],
            y=ranking['Total_Earnings'],
            text=ranking.apply(lambda x: f"{x['Total_Shifts']} SHIFTS", axis=1),
            textposition='auto',
            marker=dict(
                color=['#FFD700', '#C0C0C0', '#CD7F32', '#00ff41', '#0088ff'][:len(ranking)],
                line=dict(color='#003300', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Revenue: %{y:,.0f} SAR<extra></extra>'
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#00ff41', family='Share Tech Mono'),
        xaxis=dict(
            title='',
            tickfont=dict(size=12),
            gridcolor='rgba(0,255,65,0.1)'
        ),
        yaxis=dict(
            title='Revenue (SAR)',
            gridcolor='rgba(0,255,65,0.1)',
            tickformat=',.0f'
        ),
        showlegend=False,
        height=450, 
        margin=dict(t=40, b=20),
        dragmode='pan'
    )
    st.plotly_chart(fig, use_container_width=True, config={'modeBarButtonsToRemove': ['zoom2d', 'select2d', 'lasso2d']})

# ==========================================
# 📈 UI: NEON ANALYTICS (ENHANCED)
# ==========================================
def render_analytics(user, role):
    df = load_db('data')
    
    data = df[df['Status'] == 'Completed'] if role == 'admin' else df[(df['Driver'] == user) & (df['Status'] == 'Completed')]
    
    if data.empty:
        st.info("📊 NO DATA AVAILABLE FOR ANALYTICS")
        return

    st.markdown("### 📊 PERFORMANCE ANALYTICS")
    
    data['Date'] = pd.to_datetime(data['Start_Time']).dt.date
    data['Day'] = pd.to_datetime(data['Start_Time']).dt.strftime('%a %d')

    daily_data = data.groupby(['Date', 'Day', 'Driver'])['Total_Earnings'].sum().reset_index()
    
    fig_line = px.line(
        daily_data, 
        x='Day', 
        y='Total_Earnings', 
        color='Driver', 
        markers=True,
        title="<b>📈 DAILY REVENUE RACE</b>",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='#fff',
        xaxis_title="Timeline",
        yaxis_title="Revenue (SAR)",
        dragmode='pan'
    )
    st.plotly_chart(fig_line, use_container_width=True, config={'modeBarButtonsToRemove': ['zoom2d', 'select2d', 'lasso2d']})

# ==========================================
# 🔄 UI: OPERATIONS (RIYADH TIME FIXED)
# ==========================================
def render_ops(user, role, unique_key):
    df = load_db('data')
    
    # Active/Pending shifts dhoondo
    mask = df['Status'].isin(['Active', 'Pending_Start', 'Pending_End'])
    busy_drivers = df[mask]['Driver'].astype(str).tolist()
    busy_cars = df[mask]['Car'].astype(str).tolist()
    
    st.markdown("### 🛠️ OPERATIONS CENTER")
    
    t1, t2, t3 = st.tabs(["🚀 START MISSION", "🛑 END MISSION", "💸 FINANCE"])
    
    # --- TAB 1: START MISSION ---
    with t1:
        with st.form(key=f"start_form_{unique_key}", clear_on_submit=True):
            st.markdown("#### ⚡ INITIATE LAUNCH SEQUENCE")
            
            c1, c2 = st.columns(2)
            with c1:
                free_drivers = [d for d in DRIVERS if d not in busy_drivers]
                
                if role == "driver":
                    if user in busy_drivers:
                        st.error(f"⚠️ {user}, YOU ARE ALREADY ON A MISSION!")
                        driver = None 
                    else:
                        driver = user
                        st.info(f"👤 PILOT: {driver}")
                else:
                    if not free_drivers:
                        st.warning("⚠️ ALL PILOTS ARE CURRENTLY BUSY")
                        driver = None
                    else:
                        driver = st.selectbox("SELECT PILOT", free_drivers)

                free_cars = [c for c in CARS if c not in busy_cars]
                if not free_cars:
                    st.warning("⚠️ ALL UNITS ARE IN USE")
                    car = None
                else:
                    car = st.selectbox("SELECT UNIT", free_cars)

            with c2:
                start_wallet = st.number_input("INITIAL WALLET (SAR)", min_value=0.0, step=10.0)
                start_fuel = st.slider("FUEL TANK LEVEL", 0, 100, 100, format="%d%%")
            
            if role == "admin":
                auto_live = st.checkbox("⚡ AUTO-ACTIVATE (Skip Pending)", value=False)
            else:
                auto_live = False
            
            submitted = st.form_submit_button("🚀 LAUNCH MISSION", use_container_width=True)
            
            if submitted:
                if driver is None or car is None:
                    st.error("❌ LAUNCH FAILED: No Pilot or Unit Available!")
                else:
                    with st.spinner("🔄 INITIALIZING SYSTEMS..."):
                        time.sleep(1) 
                        
                        status = "Active" if auto_live else "Pending_Start"
                        appr_status = "Approved" if auto_live else "Pending"
                        
                        # 👇 FIX: Start Time ko Riyadh Time (+3 Hours) banao
                        riyadh_start = datetime.utcnow() + timedelta(hours=3)
                        
                        new_shift = {
                            "Shift_ID": str(uuid.uuid4())[:8],
                            "Driver": driver, "Car": car,
                            "Status": status, "Approval_Status": appr_status,
                            # Save as String to avoid JSON errors
                            "Start_Time": riyadh_start.strftime("%Y-%m-%d %H:%M:%S"),
                            "Start_Wallet": start_wallet, "Start_Fuel": start_fuel,
                            "End_Wallet": 0, "Cash_Collected": 0, "End_Fuel": 0, 
                            "Total_Earnings": 0, "Duration": 0, "End_Time": ""
                        }
                        
                        df = pd.concat([df, pd.DataFrame([new_shift])], ignore_index=True)
                        save_db('data', df)
                        
                        if status == "Active":
                            st.toast(f"✅ {driver} is now ONLINE!", icon="🟢")
                            st.balloons()
                        else:
                            st.toast("📩 Request Sent to Manager!", icon="📨")
                            st.success("✅ REQUEST SUBMITTED FOR APPROVAL")
                        
                        time.sleep(1)
                        st.rerun()

    # --- TAB 2: END MISSION ---
    with t2:
        if role == "driver":
            acts = df[(df['Driver'] == user) & (df['Status'].isin(['Active', 'Pending_Start']))]
        else:
            acts = df[df['Status'].isin(['Active', 'Pending_Start'])]
            
        if not acts.empty:
            opts = [f"{r['Shift_ID']} | {r['Driver']} | {r['Car'].split(' ')[1]}" for i, r in acts.iterrows()]
            sel = st.selectbox("SELECT ACTIVE MISSION", opts, key=f"sel_end_{unique_key}")
            
            if sel:
                sid = sel.split(" | ")[0]
                row_idx = df.index[df['Shift_ID'] == sid].tolist()[0]
                row = df.loc[row_idx]
                
                st.info(f"🛑 TERMINATING MISSION: {row['Driver']}")
                
                with st.form(key=f"end_form_{unique_key}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        cash = st.number_input("TOTAL EARNINGS", min_value=0.0, key=f"total_earnings_{unique_key}")
                        ew = float(row['Start_Wallet'])
                    with c2:
                        ef = st.slider("FINAL FUEL", 0, 100, 50)
                    
                    if st.form_submit_button("🏁 COMPLETE MISSION", use_container_width=True):
                        with st.spinner("💾 GENERATING RECEIPT..."):
                            
                            # 1. Start Time Read Karo
                            s_time = pd.to_datetime(row['Start_Time'])
                            
                            # 👇 FIX: End Time ko Riyadh Time (+3 Hours) banao
                            riyadh_end = datetime.utcnow() + timedelta(hours=3)
                            
                            # 3. Duration Calculation (Riyadh End - Start)
                            # Agar Start Time purana (UTC) tha, tab bhi diff positive ayega
                            dur_seconds = (riyadh_end - s_time).total_seconds()
                            dur = max(0, dur_seconds / 3600) # Minus na ho
                            
                            # Receipt Date Format
                            receipt_dt = riyadh_end.strftime("%d-%b-%Y | %I:%M %p")
                            
                            earn = cash
                            stat = "Pending_End"
                            appr = "Pending"
                            
                            # Update DB
                            df.at[row_idx, 'End_Time'] = riyadh_end.strftime("%Y-%m-%d %H:%M:%S")
                            df.at[row_idx, 'Duration'] = round(dur, 2)
                            df.at[row_idx, 'End_Wallet'] = ew
                            df.at[row_idx, 'Cash_Collected'] = cash
                            df.at[row_idx, 'End_Fuel'] = ef
                            df.at[row_idx, 'Total_Earnings'] = earn
                            df.at[row_idx, 'Status'] = stat
                            df.at[row_idx, 'Approval_Status'] = appr
                            
                            save_db('data', df)
                            time.sleep(0.5)
                        
                        # Show Receipt
                        st.markdown(f"""
                        <div class="receipt-box">
                            <h3 style="margin:0; text-align:center;">🧾 MISSION REPORT</h3>
                            <div style="text-align:center; font-size:12px; color:#888; margin-bottom:10px; font-family:'Courier New';">
                                {receipt_dt}
                            </div>
                            <hr style="border-color:#00ff41;">
                            <div style="display:flex; justify-content:space-between;"><span>PILOT:</span><span>{row['Driver']}</span></div>
                            <div style="display:flex; justify-content:space-between;"><span>UNIT:</span><span>{row['Car']}</span></div>
                            <div style="display:flex; justify-content:space-between;"><span>DURATION:</span><span>{dur:.1f} HRS</span></div>
                            <div style="display:flex; justify-content:space-between; color:#00ff41;"><span>TOTAL EARNINGS:</span><span>{cash}</span></div>
                            <hr style="border-color:#333;">
                            <h1 style="text-align:center; margin-top:10px; color:#fff;">TOTAL: {earn:,.0f} SAR</h1>
                            <div style="text-align:center; font-size:10px; color:#555;">ID: {sid} | STATUS: {stat.upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success("✅ MISSION ENDED - SENT FOR APPROVAL")
                        st.caption("ℹ️ Closing automatically in 60 seconds...")
                        
                        time.sleep(60) 
                        st.rerun()
        else:
            st.info("😴 NO ACTIVE MISSIONS DETECTED")

    # --- TAB 3: FINANCE (Same as before) ---
    with t3:
        st.markdown("#### 💸 FINANCIAL LOGGING")
        with st.form(key=f"fin_form_{unique_key}", clear_on_submit=True):
            if role == "driver":
                ops = ["💰 HANDOVER CASH"]
                default_idx = 0
            else:
                ops = ["📥 RECEIVE CASH", "📤 GIVE ADVANCE", "🏦 TRANSFER TO CEO"]
                default_idx = 0
            
            ftype = st.selectbox("TRANSACTION TYPE", ops, index=default_idx)
            
            c1, c2 = st.columns(2)
            with c1:
                if "HANDOVER" in ftype:
                    agt = user; src = "Driver"
                elif "RECEIVE" in ftype:
                    agt = st.selectbox("FROM DRIVER", DRIVERS); src = "Manager"
                elif "ADVANCE" in ftype:
                    agt = st.selectbox("TO DRIVER", DRIVERS); src = "Manager"
                else:
                    agt = st.selectbox("ON BEHALF OF (DRIVER)", ["General (Admin)"] + DRIVERS); src = "Manager"
            
            with c2:
                amt = st.number_input("AMOUNT (SAR)", min_value=0.0, step=50.0)
            
            note = st.text_input("REFERENCE / NOTE")
                
            if st.form_submit_button("💾 LOG TRANSACTION", use_container_width=True):
                with st.spinner("💸 PROCESSING FUNDS..."):
                    db_type = "Advance" if "ADVANCE" in ftype.upper() else "CEO_Transfer" if "CEO" in ftype.upper() else "Received"
                    status = "Pending" if role == "driver" else "Approved"
                    
                    tdf = load_db('trans')
                    # Fix Transaction Date to Riyadh Time too
                    riyadh_now = datetime.utcnow() + timedelta(hours=3)
                    
                    new_tx = {
                        "Trans_ID": str(uuid.uuid4())[:8],
                        "Date": riyadh_now.strftime("%Y-%m-%d %H:%M"),
                        "Driver": agt, "Type": db_type, "Amount": amt,
                        "Method": "Cash", "Notes": note,
                        "Approval_Status": status, "Source": src
                    }
                    
                    tdf = pd.concat([tdf, pd.DataFrame([new_tx])], ignore_index=True)
                    save_db('trans', tdf)
                    time.sleep(0.5)
                
                st.toast(f"Transaction Saved: {amt} SAR", icon="💾")
                st.success("✅ TRANSACTION RECORDED SUCCESSFULLY")
                time.sleep(1)
                st.rerun()
#---Services Tab: Maintenance & Penalties ---
def render_services_tab(unique_key):
    st.markdown("### 🔧 MAINTENANCE & PENALTIES")
    
    with st.form(key=f"serv_form_{unique_key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        
        with c1:
            action_type = st.selectbox("SELECT ACTION TYPE", 
                                     ["👮 TRAFFIC CHALLAN (Fine)", 
                                      "🛠️ CAR REPAIR (Expense)", 
                                      "🚿 CAR WASH (Expense)"])
            
            driver = st.selectbox("SELECT DRIVER / PERSON", DRIVERS)
            
        with c2:
            amount = st.number_input("AMOUNT (SAR)", min_value=0.0, step=10.0)
            car = st.selectbox("RELATED VEHICLE", CARS)
            
        notes = st.text_input("NOTES / DETAILS (e.g. 'Saher Camera Riyadh Road' or 'Oil Change')")
        
        if st.form_submit_button("💾 SAVE RECORD", use_container_width=True):
            if amount > 0:
                with st.spinner("💾 UPDATING LEDGERS..."):
                    if "CHALLAN" in action_type:
                        db_type = "Challan"
                        src = "Driver"
                        status = "Approved"
                    else:
                        db_type = "Expense"
                        src = "Manager"
                        status = "Approved"

                    tdf = load_db('trans')
                    new_tx = {
                        "Trans_ID": str(uuid.uuid4())[:8],
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Driver": driver,
                        "Type": db_type,
                        "Amount": amount,
                        "Method": "System",
                        "Notes": f"{car} | {notes}",
                        "Approval_Status": status,
                        "Source": src
                    }
                    tdf = pd.concat([tdf, pd.DataFrame([new_tx])], ignore_index=True)
                    save_db('trans', tdf)
                    
                    time.sleep(0.5)
                
                if db_type == "Challan":
                    st.error(f"⛔ CHALLAN ADDED! Will be deducted from {driver}'s salary.")
                else:
                    st.success(f"✅ EXPENSE RECORDED! Deducted from Manager's Account.")
                time.sleep(1.5)
                st.rerun()
            else:
                st.warning("⚠️ Please enter a valid amount.")

# ==========================================
# 💰 UI: SALARY REPORT (FIXED)
# ==========================================
def render_salary():
    df = load_db('data')
    tdf = load_db('trans')
    
    st.markdown("### 💰 SALARY MATRIX")
    
    comp = df[(df['Status'] == 'Completed') & (df['Approval_Status'] == 'Approved')]
    adv_df = tdf[(tdf['Type'] == 'Advance') & (tdf['Approval_Status'] == 'Approved')]
    
    fine_df = tdf[tdf['Type'] == 'Challan']
    
    rows = []
    
    for driver in DRIVERS:
        driver_shifts = comp[comp['Driver'] == driver]
        rev = driver_shifts['Total_Earnings'].sum() if not driver_shifts.empty else 0
        
        ratio = min(rev / MONTHLY_TARGET, 1.0) if MONTHLY_TARGET > 0 else 0
        sal = BASE_SALARY * ratio
        
        taken = adv_df[adv_df['Driver'] == driver]['Amount'].sum() if not adv_df.empty else 0
        
        penalties = fine_df[fine_df['Driver'] == driver]['Amount'].sum() if not fine_df.empty else 0
        
        pay = sal - taken - penalties
        
        shift_count = len(driver_shifts)
        avg_rev = rev / shift_count if shift_count > 0 else 0
        
        rows.append({
            "DRIVER": driver,
            "SHIFTS": shift_count,
            "REVENUE": f"{rev:,.0f}",
            "PERF": f"{ratio*100:.0f}%",
            "SALARY": f"{sal:,.0f}",
            "ADVANCE": f"{taken:,.0f}",
            "FINE": f"{penalties:,.0f}",
            "PAYABLE": f"{pay:,.0f}",
            "AVG/SHIFT": f"{avg_rev:,.0f}"
        })
    
    salary_df = pd.DataFrame(rows)
    
    st.dataframe(
        salary_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "DRIVER": st.column_config.TextColumn("Driver", width="small"),
            "SHIFTS": st.column_config.NumberColumn("Shifts", format="%d"),
            "REVENUE": st.column_config.TextColumn("Revenue"),
            "PERF": st.column_config.TextColumn("Perf %"),
            "SALARY": st.column_config.TextColumn("Salary"),
            "ADVANCE": st.column_config.TextColumn("Advance"),
            "FINE": st.column_config.TextColumn("Fines", help="Traffic Violations Deducted"),
            "PAYABLE": st.column_config.TextColumn("Net Pay", help="Salary - Advance - Fine"),
            "AVG/SHIFT": st.column_config.TextColumn("Avg/Shift")
        }
    )
    
    total_rev = sum(float(row["REVENUE"].replace(",", "")) for row in rows)
    total_sal = sum(float(row["SALARY"].replace(",", "")) for row in rows)
    total_adv = sum(float(row["ADVANCE"].replace(",", "")) for row in rows)
    total_fine = sum(float(row["FINE"].replace(",", "")) for row in rows)
    total_pay = sum(float(row["PAYABLE"].replace(",", "")) for row in rows)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1: st.metric("Total Revenue", f"{total_rev:,.0f}")
    with col2: st.metric("Total Salary", f"{total_sal:,.0f}")
    with col3: st.metric("Total Advances", f"{total_adv:,.0f}")
    with col4: st.metric("Total Fines", f"{total_fine:,.0f}")
    with col5: st.metric("Net Payable", f"{total_pay:,.0f}")

# ==========================================
# 🔔 UI: NOTIFICATIONS (REJECT = REVERT TO ACTIVE FIX)
# ==========================================
def render_notifs():
    df = load_db('data')
    tdf = load_db('trans')
    
    # Sirf wo shifts dikhao jo Pending hain (Start ya End ke liye)
    pending_shifts = df[df['Status'].isin(['Pending_Start', 'Pending_End'])]
    pending_trans = tdf[tdf['Approval_Status'] == 'Pending']
    
    total_pending = len(pending_shifts) + len(pending_trans)
    
    if total_pending > 0:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
            <div class="notification-badge">{total_pending}</div>
            <span style="color:#fff; font-size:16px; font-family:'Orbitron';">PENDING APPROVALS</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 REVIEW REQUESTS", expanded=True):
            # --- 1. SHIFT REQUESTS ---
            if not pending_shifts.empty:
                st.markdown("#### 🚗 SHIFT REQUESTS")
                for idx, shift in pending_shifts.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Display Logic
                        if shift['Status'] == 'Pending_Start':
                            st.write(f"**🟢 START REQUEST:** {shift['Driver']} - {shift['Car']}")
                            st.caption(f"Start Time: {shift['Start_Time']}")
                        else:
                            st.write(f"**🔴 END REQUEST:** {shift['Driver']} - {shift['Car']}")
                            # Earnings show karo taake admin dekh sake sahi hai ya nahi
                            earn = shift['Total_Earnings'] if 'Total_Earnings' in shift else 0
                            cash = shift['Cash_Collected'] if 'Cash_Collected' in shift else 0
                            st.caption(f"Earnings: {earn} | Cash Handover: {cash}")
                    
                    # ✅ APPROVE BUTTON
                    with col2:
                        if st.button("✅", key=f"approve_s_{idx}", help="Approve"):
                            if shift['Status'] == 'Pending_Start':
                                df.at[idx, 'Status'] = 'Active'
                            else:
                                df.at[idx, 'Status'] = 'Completed'
                            
                            df.at[idx, 'Approval_Status'] = 'Approved'
                            save_db('data', df)
                            st.success(f"Approved for {shift['Driver']}")
                            time.sleep(1)
                            st.rerun()
                    
                    # ❌ REJECT BUTTON (THE FIX)
                    with col3:
                        if st.button("❌", key=f"reject_s_{idx}", help="Reject & Revert"):
                            if shift['Status'] == 'Pending_Start':
                                # Case 1: Start hi ghalat tha -> Delete row
                                df = df.drop(idx)
                                st.warning(f"Start Request Deleted for {shift['Driver']}")
                            else:
                                # Case 2: End Request Reject hui -> REVERT TO ACTIVE
                                # Wapis purani halat mein le aao
                                df.at[idx, 'Status'] = 'Active'           # Wapis Active
                                df.at[idx, 'Approval_Status'] = 'Approved' # Active maane Approved Start
                                
                                # End data saaf kar do
                                df.at[idx, 'End_Time'] = ''
                                df.at[idx, 'Duration'] = 0
                                df.at[idx, 'Total_Earnings'] = 0
                                df.at[idx, 'Cash_Collected'] = 0
                                df.at[idx, 'End_Wallet'] = 0
                                df.at[idx, 'End_Fuel'] = 0
                                
                                st.info(f"Session Reverted to ACTIVE for {shift['Driver']}")
                            
                            save_db('data', df)
                            time.sleep(1)
                            st.rerun()
                    
                    st.divider()
            
            # --- 2. TRANSACTION REQUESTS (As it is) ---
            if not pending_trans.empty:
                st.markdown("#### 💰 TRANSACTION REQUESTS")
                for idx, trans in pending_trans.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{trans['Type']}:** {trans['Driver']}")
                        st.caption(f"Amount: {trans['Amount']} | {trans['Notes']}")
                    
                    with col2:
                        if st.button("✅", key=f"approve_t_{idx}"):
                            tdf.at[idx, 'Approval_Status'] = 'Approved'
                            save_db('trans', tdf)
                            st.rerun()
                    
                    with col3:
                        if st.button("❌", key=f"reject_t_{idx}"):
                            tdf = tdf.drop(idx) # Transaction reject matlab delete
                            save_db('trans', tdf)
                            st.rerun()
                    st.divider()

# ==========================================
# 10. MAIN APPLICATION (FINAL ERROR-FREE VERSION)
# ==========================================
def main():
    user_data = check_session()
    
    if not user_data:
        render_login()
        return
    
    name = user_data['name']
    role = user_data.get('role', 'driver')
    
    # Header Section
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col1:
        display_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%I:%M:%S %p")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #001a00 0%, #000 100%); 
            border: 1px solid #00ff41; border-radius: 4px; padding: 15px 0; 
            text-align: center; box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);">
            <div style="font-size:10px; color:#888;">SYSTEM TIME</div>
            <div style="font-family:'Orbitron'; color:#00ff41; font-size:18px; font-weight:bold;">
                {display_time}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h1 style='margin:0; text-align:center;'>⚡NOMORE\nCOMMAND</h1>", unsafe_allow_html=True)
        # Role Badge
        role_display = "👑 CEO" if role == "ceo" else role.upper()
        st.markdown(f"<p style='color:#888; margin:0; font-size:14px; text-align:center;'>User: {name} | Role: {role_display} | System: ONLINE</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 LOGOUT", use_container_width=True): logout()
    
    st.markdown("---")
    
    # ==================================
    # 🚗 DRIVER VIEW
    # ==================================
    if role == "driver":
        render_js_timer(name); render_driver_hud(name)
        
        col1, col2 = st.columns([2, 1])
        with col1: render_fleet("driver"); 
        with col2: render_leaderboard()
        
        tab1, tab2 = st.tabs(["⚙️ OPERATIONS", "📜 HISTORY"])
        with tab1: render_ops(name, role, unique_key="driver_ops")
        # 👇 Unique Key: 'driver_hist'
        with tab2: render_history_logs(name, role, unique_key="driver_hist")
    
    # ==================================
    # 👑 CEO VIEW (READ ONLY)
    # ==================================
    elif role == "ceo":
        render_manager_stats()
        
        c1, c2 = st.columns([2, 1])
        with c1: 
            st.info("📡 LIVE FLEET MONITORING (READ-ONLY)")
            render_fleet("admin") 
        with c2: 
            render_leaderboard()
            
        render_analytics(name, role)
        
        t1, t2, t3, t4 = st.tabs(["🖨️ REPORTS", "💰 SALARY SHEET", "📜 SHIFT & TRANS LOGS"])
        
        with t1: render_reports_tab() 
        with t2: render_salary()      
        with t3: 
            st.markdown("### 🚙 SHIFT HISTORY")
            # 👇 Unique Key: 'ceo_shift_view' (Different from transaction tab)
            render_history_logs(name, "admin", unique_key="ceo_shift_view") 

    # ==================================
    # 🛠️ ADMIN VIEW (FULL CONTROL)
    # ==================================
    else:
        render_fleet("admin"); render_manager_stats(); render_notifs()
        
        col1, col2 = st.columns(2)
        with col1: render_analytics(name, role)
        with col2: render_leaderboard()
        
        t1, t2, t3, t4, t5 = st.tabs(["⚙️ OPS", "💰 PAYROLL", "📜 LOGS", "🔧 SERVICES", "🖨️ REPORTS"])
        
        with t1: render_ops(name, role, unique_key="admin_ops")
        with t2: render_salary()
        # 👇 Unique Key: 'admin_hist'
        with t3: render_history_logs(name, role, unique_key="admin_hist")
        with t4: render_services_tab("service_key_main")
        with t5: render_reports_tab()
# ==========================================
# 🖨️ UI: REPORT GENERATOR (HH:MM TIME FORMAT)
# ==========================================
def render_reports_tab():
    import matplotlib.pyplot as plt
    import io

    st.markdown("### 🖨️ GENERATE REPORT CARD")
    
    # 1. Inputs
    c1, c2 = st.columns(2)
    with c1:
        driver_opts = ["🚀 ALL TEAM (Combined)"] + DRIVERS
        driver = st.selectbox("SELECT TARGET", driver_opts, key="rep_driver")
    with c2:
        rtype = st.selectbox("REPORT TYPE", ["📅 SPECIFIC DATE (Daily)", "🗓️ THIS MONTH (Monthly)", "♾️ FULL HISTORY (Overall)"], key="rep_type")

    # Date Picker
    target_date = datetime.now().date()
    if "DAILY" in rtype or "DATE" in rtype:
        target_date = st.date_input("SELECT DATE", datetime.now())

    # Helper function
    def clean_duration_value(val):
        try:
            val_str = str(val).strip()
            if ":" in val_str:
                parts = val_str.split(":")
                h = float(parts[0])
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                return h + (m/60) + (s/3600)
            else:
                return float(val)
        except:
            return 0.0

    if st.button("📄 GENERATE REPORT", use_container_width=True):
        df = load_db('data')
        tdf = load_db('trans')
        
        # --- FIXES ---
        if 'Shift_ID' in df.columns: df = df.drop_duplicates(subset=['Shift_ID'], keep='last')
        if 'Trans_ID' in tdf.columns: tdf = tdf.drop_duplicates(subset=['Trans_ID'], keep='last')
        if 'Duration' in df.columns: df['Duration'] = df['Duration'].apply(clean_duration_value)

        cols_to_fix = ['Total_Earnings', 'Cash_Collected', 'End_Wallet', 'Start_Wallet']
        for c in cols_to_fix:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        tdf['Amount'] = pd.to_numeric(tdf['Amount'], errors='coerce').fillna(0)
        
        # --- FILTERING ---
        if "ALL TEAM" in driver:
            target_df = df; target_trans = tdf; driver_label = "ALL TEAM (FLEET)"
        else:
            target_df = df[df['Driver'] == driver]; target_trans = tdf[tdf['Driver'] == driver]; driver_label = driver.upper()

        comp = target_df[(target_df['Status'] == 'Completed')]
        trans = target_trans[(target_trans['Approval_Status'] == 'Approved')]
        
        # Date Prep
        comp['Date'] = pd.to_datetime(comp['Start_Time']).dt.date
        trans['Date_Only'] = pd.to_datetime(trans['Date']).dt.date
        comp['Month'] = pd.to_datetime(comp['Start_Time']).dt.month
        trans['Month'] = pd.to_datetime(trans['Date']).dt.month
        
        report_data = {}; title = ""
        
        # --- REPORT LOGIC ---
        if "DAILY" in rtype or "DATE" in rtype:
            day_comp = comp[comp['Date'] == target_date]
            day_trans = trans[trans['Date_Only'] == target_date]
            title = f"DAILY REPORT | {target_date.strftime('%d-%b-%Y')}"
            report_data = {
                "SHIFTS": len(day_comp), "REVENUE": day_comp['Total_Earnings'].sum(),
                "DURATION": day_comp['Duration'].sum(), "ADVANCE": day_trans[day_trans['Type'] == 'Advance']['Amount'].sum(),
                "FINE": day_trans[day_trans['Type'] == 'Challan']['Amount'].sum()
            }
        elif "THIS MONTH" in rtype:
            curr_month = datetime.now().month
            m_comp = comp[comp['Month'] == curr_month]; m_trans = trans[trans['Month'] == curr_month]
            title = f"MONTHLY REPORT | {datetime.now().strftime('%B %Y')}"
            report_data = {
                "SHIFTS": len(m_comp), "REVENUE": m_comp['Total_Earnings'].sum(),
                "DURATION": m_comp['Duration'].sum(), "ADVANCE": m_trans[m_trans['Type'] == 'Advance']['Amount'].sum(),
                "FINE": m_trans[m_trans['Type'] == 'Challan']['Amount'].sum()
            }
        else: # Overall
            title = f"LIFETIME PERFORMANCE"
            report_data = {
                "SHIFTS": len(comp), "REVENUE": comp['Total_Earnings'].sum(),
                "DURATION": comp['Duration'].sum(), "ADVANCE": trans[trans['Type'] == 'Advance']['Amount'].sum(),
                "FINE": trans[trans['Type'] == 'Challan']['Amount'].sum()
            }
            
        # Calculations
        rev = float(report_data['REVENUE']); fine = float(report_data['FINE'])
        adv = float(report_data['ADVANCE']); dur = float(report_data['DURATION'])
        net_gen = rev - fine
        
        # 👇 NEW: Format Duration (Decimal -> HH:MM)
        # Is hisab se: 2.8 Hours -> 2:48
        total_mins = int(dur * 60)
        hours = total_mins // 60
        minutes = total_mins % 60
        dur_str = f"{hours}:{minutes:02d}" # Output format: 2:48
        
        # --- 1. DISPLAY ON SCREEN (HTML) ---
        st.markdown(f"""
        <div class="receipt-box" style="border-color:#0088ff; color:#fff; padding:15px;">
            <h3 style="margin:0; text-align:center; color:#0088ff; font-size:18px;">📊 {title}</h3>
            <div style="text-align:center; font-size:12px; color:#888; margin-bottom:10px;">TARGET: {driver_label}</div>
            <hr style="border-color:#333; margin: 5px 0;">
            <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:14px;"><span>TOTAL SHIFTS:</span><span>{report_data['SHIFTS']}</span></div>
            <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:14px;"><span>TOTAL HOURS:</span><span>{dur_str} HRS</span></div>
            <hr style="border-color:#333; margin: 5px 0;">
            <div style="display:flex; justify-content:space-between; color:#00ff41; margin:2px 0; font-size:14px;"><span>GROSS REVENUE:</span><span>{rev:,.0f}</span></div>
            <div style="display:flex; justify-content:space-between; color:#ff0055; margin:2px 0; font-size:14px;"><span>TOTAL FINES:</span><span>-{fine:,.0f}</span></div>
            <div style="display:flex; justify-content:space-between; color:#ffaa00; margin:2px 0; font-size:14px;"><span>TOTAL ADVANCE:</span><span>{adv:,.0f}</span></div>
            <hr style="border-color:#fff; margin: 10px 0;">
            <h2 style="text-align:center; margin-top:5px; font-size:22px;">NET REVENUE: {net_gen:,.0f} SAR</h2>
        </div>
        """, unsafe_allow_html=True)

        # --- 2. GENERATE PNG IMAGE (UPDATED TIME FORMAT) ---
        fig, ax = plt.subplots(figsize=(5, 6)) 
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.axis('off')

        # Header
        plt.text(0.5, 0.93, "NOMORE MANAGEMENT", ha='center', color='#00ff41', fontsize=14, weight='bold', fontname='monospace')
        plt.text(0.5, 0.88, title, ha='center', color='white', fontsize=10, fontname='monospace')
        plt.text(0.5, 0.84, f"TARGET: {driver_label}", ha='center', color='gray', fontsize=9, fontname='monospace')
        
        # Line 1
        plt.plot([0.05, 0.95], [0.80, 0.80], color='white', lw=1, ls='--')

        # Stats Block
        plt.text(0.05, 0.74, "TOTAL SHIFTS:", color='white', fontsize=11, fontname='monospace')
        plt.text(0.95, 0.74, f"{report_data['SHIFTS']}", color='white', ha='right', fontsize=11, fontname='monospace')

        plt.text(0.05, 0.68, "TOTAL HOURS:", color='white', fontsize=11, fontname='monospace')
        plt.text(0.95, 0.68, f"{dur_str} HRS", color='white', ha='right', fontsize=11, fontname='monospace')

        # Line 2
        plt.plot([0.05, 0.95], [0.62, 0.62], color='gray', lw=0.5)

        # Financials Block
        plt.text(0.05, 0.55, "GROSS REVENUE:", color='#00ff41', fontsize=11, fontname='monospace')
        plt.text(0.95, 0.55, f"{rev:,.0f}", color='#00ff41', ha='right', fontsize=11, fontname='monospace')

        plt.text(0.05, 0.49, "TOTAL FINES:", color='#ff0055', fontsize=11, fontname='monospace')
        plt.text(0.95, 0.49, f"-{fine:,.0f}", color='#ff0055', ha='right', fontsize=11, fontname='monospace')

        plt.text(0.05, 0.43, "TOTAL ADVANCE:", color='#ffaa00', fontsize=11, fontname='monospace')
        plt.text(0.95, 0.43, f"{adv:,.0f}", color='#ffaa00', ha='right', fontsize=11, fontname='monospace')

        # Final Line
        plt.plot([0.05, 0.95], [0.36, 0.36], color='white', lw=2)

        # Net Total Block
        plt.text(0.5, 0.28, "NET REVENUE", ha='center', color='white', fontsize=10, fontname='monospace')
        plt.text(0.5, 0.18, f"{net_gen:,.0f} SAR", ha='center', color='white', fontsize=22, weight='bold', fontname='monospace')
        
        plt.text(0.5, 0.05, "GENERATED BY SYSTEM MANAGEMENT", ha='center', color='gray', fontsize=7, fontname='monospace')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', facecolor='black', pad_inches=0.2)
        buf.seek(0)
        
        fname = f"Receipt_{driver_label.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.png"
        st.download_button(
            label="💾 DOWNLOAD PNG RECEIPT",
            data=buf,
            file_name=fname,
            mime="image/png",
            use_container_width=True
        )

# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"System Error: {str(e)}")
        st.info("Please refresh the page or contact system administrator.")


