import streamlit as st
from utils import login, api_request, load_css

import subprocess
import sys
import time
import os

# --- HACK BUAT DEPLOY DI STREAMLIT ---
# Nyalain backend otomatis biar ga ribet jalanin 2 terminal
# ---------------------------------------
def start_backend():
    import socket
    import threading
    import uvicorn
    
    # 1. Cari folder backend otomatis
    target_dir = None
    start_dir = os.getcwd()
    
    for root, dirs, files in os.walk(start_dir):
        if "backend" in dirs:
            target_dir = root
            break
            
    if target_dir:
        # Masukin ke path biar bisa di-import
        if target_dir not in sys.path:
            sys.path.append(target_dir)
        print(f"Ketemu folder backend di: {target_dir}")
    else:
        st.error(f"Waduh, folder 'backend' gak ketemu nih. Cek lagi struktur foldernya.")
        return

    # 2. Cek dulu, backend udah jalan belum?
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result != 0:
        print("Backend belum jalan, gaspol nyalain sekarang...")
        
        try:
            from backend.main import app as backend_app
        except ImportError as e:
            st.error(f"Gagal import backend: {e}")
            st.stop()

        def run_server():
            # Jalanin uvicorn langsung di thread
            uvicorn.run(backend_app, host="127.0.0.1", port=8000, log_level="info", use_colors=False)

        t = threading.Thread(target=run_server, daemon=True)
        t.start()
        
        # 3. Tunggu bentar sampe backend siap
        st.caption("🚀 Lagi manasin mesin backend... sabar ya")
        progress_bar = st.progress(0)
        
        for i in range(15):
            time.sleep(1)
            progress_bar.progress((i + 1) * 6)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            res = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            
            if res == 0:
                progress_bar.empty()
                st.success("System Connected!")
                time.sleep(0.5)
                st.rerun()
                return
        
        st.error("❌ System failed to start. Check logs.")

start_backend()
# -------------------------------------------
# -------------------------------------------

st.set_page_config(page_title="Smart POS System", layout="wide", page_icon="🛍️")
load_css()

if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

def main():

    if not st.session_state.token:
        # Langsung sembunyiin sidebar pas di halaman login biar rapi
        from utils import hide_sidebar
        hide_sidebar()
        
        # Kasih jarak dikit biar pas di tengah
        st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
        
        # Kartu login yang di-tengahin
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("""
<div class='login-card'>
    <div style='text-align: center; margin-bottom: 32px;'>
        <div style='
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            width: 90px;
            height: 90px;
            border-radius: 20px;
            margin: 0 auto 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        '>
            🛍️
        </div>
        <h2 style='margin: 0; font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #fff, #e5e7eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Smart POS</h2>
        <p style='margin: 8px 0 0 0; color: #9ca3af; font-size: 0.95rem;'>Masuk dulu untuk akses dashboard</p>
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="color: #9ca3af; font-size: 0.75rem; font-weight: 700; margin-bottom: 5px; text-transform: uppercase;">DI BUAT OLEH : BUDIONO SIREGAR</p>
            <div style="color: #6b7280; font-size: 0.75rem;">
                <div style="margin-bottom: 2px;">1. ISA ALI ARRUMY (24.83.1056)</div>
                <div style="margin-bottom: 2px;">2. IHSANUL FIKRI (24.83.1084)</div>
                <div>3. MUHAMAD DARUS SALAM (24.83.1063)</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
            
            st.markdown("<p style='color: #e5e7eb; font-weight: 600; margin-bottom: 8px; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;'>USERNAME</p>", unsafe_allow_html=True)
            username = st.text_input("Username", label_visibility="collapsed", placeholder="Isi username...")
            
            st.markdown("<p style='color: #e5e7eb; font-weight: 600; margin-bottom: 8px; margin-top: 16px; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;'>PASSWORD</p>", unsafe_allow_html=True)
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Isi password...")
            
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            
            if st.button("Masuk →", use_container_width=True, type="primary"):
                result = login(username, password)
                if "access_token" in result:
                    st.session_state.token = result["access_token"]
                    # Ambil info user buat nentuin role (admin/kasir)
                    user_info = api_request("GET", "/auth/me")
                    if user_info:
                        st.session_state.role = user_info["role"]
                        st.session_state.username = user_info["username"]
                        st.rerun()
                    else:
                        st.error("Failed to fetch user info")
                else:
                    st.error(result.get("error", "Login Failed"))
            
            st.markdown("""
                <p style='text-align: center; color: #6b7280; font-size: 0.8rem; margin-top: 32px;'>
                    © 2026 Smart POS - Point of Sale System
                </p>
            """, unsafe_allow_html=True)
    
    else:
        # ========== SIDEBAR NAVIGASI (pake fungsi dari utils biar rapi) ==========
        from utils import render_sidebar
        render_sidebar()

        st.title("Selamat Datang di Smart POS")
        
        # Dashboard Overview for Landing Page
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("### Aksi Cepat")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Buka Kasir POS 🛒", use_container_width=True):
                st.switch_page("pages/2_Cashier_POS.py")
        with c2:
            if st.session_state.role == "admin":
                if st.button("Buka Dashboard Admin 📊", use_container_width=True):
                    st.switch_page("pages/1_Admin_Dashboard.py")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
