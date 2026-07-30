import streamlit as st
import extra_streamlit_components as stx
import json
import time
from datetime import datetime, timedelta
from sqlalchemy import text

# Import utiliti
from database_utils import get_engine, init_db, check_password, hash_password, get_malaysia_time, delete_item
from form_components import render_apc_evaluation_form
from admin_logic import render_dashboard, render_management
from reviewer_logic import render_review_form
from reporting_logic import render_reporting 

# --- 1. SET PAGE CONFIG (WAJIB PALING ATAS) ---
st.set_page_config(page_title="Penilaian APC ASM", layout="wide")

# --- 2. ENGINE & DB INIT (TURBO CACHE) ---
engine = get_engine()

@st.cache_resource
def startup_sequence():
    init_db.__wrapped__() # Bypass cache to ensure ALTER TABLE runs
    # Cache invalidated for has_consented DB schema update
    return True

startup_sequence()

# --- 3. SESSION & COOKIE MANAGER ---
if 'cookie_manager' not in st.session_state:
    st.session_state.cookie_manager = stx.CookieManager(key="rbs_mgr")
cookie_manager = st.session_state.cookie_manager

# --- 4. PERSISTENCE LOGIC (PUNCA LOGOUT FIX) ---
def sync_auth():
    # A. Jika dah memang authenticated dalam session, lepas terus (Paling utama)
    if st.session_state.get('authenticated'):
        return True

    # B. Cuma sekat "Auto-Login" dari kuki/URL kalau baru lepas klik Logout
    if st.session_state.get('logout_in_progress'):
        return False

    # C. Check URL Params
    params = st.query_params
    if "u" in params and "r" in params:
        st.session_state.update({
            "authenticated": True,
            "username": params["u"],
            "role": params["r"],
            "full_name": params.get("n", params["u"])
        })
        return True

    # D. Check Cookies
    val = cookie_manager.get('rbs_session')
    if val:
        try:
            if isinstance(val, str): val = json.loads(val)
            st.session_state.update({
                "authenticated": True,
                "username": val['u'], "role": val['r'], "full_name": val['n']
            })
            return True
        except: pass
    
    return False
    
# Jalankan sync_auth
is_auth = sync_auth()

# --- 5. LOGIN INTERFACE ---
if not is_auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("asm-logo.png", width=250)
        st.subheader("🔐 Log masuk Penilaian 360 Darjah untuk calon APC-2025")
        with st.form("login_form"):
            u_input = st.text_input("Nama Pengguna (Username)").strip()
            p_input = st.text_input("Kata Laluan (Password)", type="password")
            
            if st.form_submit_button("Log Masuk", use_container_width=True):
                with engine.connect() as conn:
                    # Semak kalau ini adalah Admin (jadual users)
                    res_admin = conn.execute(text("SELECT password_hash, full_name, username FROM users WHERE LOWER(username) = LOWER(:u)"), {"u": u_input}).fetchone()
                    
                    if res_admin and check_password(p_input, res_admin[0]):
                        role = "Admin"
                        real_username = res_admin[2]
                        st.session_state.update({"authenticated": True, "username": real_username, "role": role, "full_name": res_admin[1]})
                        st.query_params.update({"u": real_username, "r": role, "n": res_admin[1]})
                        cookie_manager.set('rbs_session', json.dumps({"u": real_username, "r": role, "n": res_admin[1]}), expires_at=datetime.now() + timedelta(days=1))
                        st.success("Log masuk Admin berjaya!"); time.sleep(0.5); st.rerun()
                    else:
                        # Semak kalau ini adalah Penilai (jadual reviewers)
                        res_rev = conn.execute(text("SELECT password_hash, full_name, username FROM reviewers WHERE LOWER(username) = LOWER(:u)"), {"u": u_input}).fetchone()
                        
                        if res_rev and check_password(p_input, res_rev[0]):
                            role = "Reviewer"
                            real_username = res_rev[2]
                            st.session_state.update({"authenticated": True, "username": real_username, "role": role, "full_name": res_rev[1]})
                            st.query_params.update({"u": real_username, "r": role, "n": res_rev[1]})
                            cookie_manager.set('rbs_session', json.dumps({"u": real_username, "r": role, "n": res_rev[1]}), expires_at=datetime.now() + timedelta(days=1))
                            st.success("Log masuk berjaya!"); time.sleep(0.5); st.rerun()
                        else:
                            st.error("Butiran log masuk tidak sah.")
    st.stop()

# --- 6. SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.image("asm-logo.png", use_container_width=True)
    
    # Tukar paparan nama dan peranan untuk Admin
    fn = st.session_state.get('full_name')
    if fn == "System Admin": fn = "Pentadbir Sistem"
    st.title(f"👤 {fn}")
    
    if st.session_state.get('role') == "Reviewer":
        display_role = "Penilai"
    elif st.session_state.get('role') == "Admin":
        display_role = "Pentadbir"
    else:
        display_role = st.session_state.get('role')
        
    st.caption(f"Peranan: {display_role}")

    def clear_transient_states():
        st.session_state.report_card_app = None

    if st.session_state.role == "Admin":
        menu = st.radio("Navigasi", ["Papan Pemuka", "Laporan", "Pengurusan Penilaian", "Pengurusan Penilai"], on_change=clear_transient_states)
    else:
        menu = st.radio("Navigasi", ["Penilaian"], on_change=clear_transient_states)

    st.divider()
    if st.button("Log Keluar", type="primary", use_container_width=True):
        # 1. Set flag logout
        st.session_state.logout_in_progress = True
        
        # 2. Padam kuki dengan cara selamat (Try-Except)
        try:
            # Kita check dulu kalau kuki tu ada, baru delete
            if cookie_manager.get('rbs_session'):
                cookie_manager.delete('rbs_session')
        except Exception:
            # Jika ralat (KeyError), abaikan saja sebab kuki memang dah takde
            pass
            
        # 3. Padam URL params
        st.query_params.clear()
        
        # 4. Reset data session
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.full_name = None
        
        # 5. Rerun
        time.sleep(0.2)
        st.rerun()

# --- 7. MODULE ROUTING ---

# Guna engine sedia ada (connection pool)
if menu == "Papan Pemuka": render_dashboard(engine)
elif menu == "Laporan": render_reporting(engine)
elif menu in ["Pengurusan Penilai", "Pengurusan Penilaian"]: 
    render_management(menu, engine, hash_password, delete_item)
elif menu == "Penilaian":
    render_review_form(engine, get_malaysia_time, render_apc_evaluation_form)
