import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def hide_sidebar():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)


def login(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/token", data={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()
        else:
            try:
                msg = response.json().get("detail", "Login failed")
            except ValueError:
                msg = f"Login failed ({response.status_code}): {response.text[:100]}"
            return {"error": msg}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def api_request(method, endpoint, data=None, params=None):
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 401:
            st.warning("Session expired. Please login again.")
            st.session_state.clear()
            st.rerun() # Use rerun in newer streamlit, or experimental_rerun
        else:
            st.error(f"Request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def load_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Gaya Aplikasi Utama - Tema Gelap Keren */
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #0f1729 50%, #1a1f3a 100%);
            color: #e5e7eb;
        }
        
        /* Gaya Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.1);
            box-shadow: 5px 0 20px rgba(0,0,0,0.4);
        }

        /* Gaya Kartu - Efek Kaca (Glassmorphism) */
        .card {
            background: rgba(26, 31, 58, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 28px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(99, 102, 241, 0.1);
            margin-bottom: 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        /* Kartu Login di Tengah */
        .login-card {
            background: rgba(26, 31, 58, 0.8);
            backdrop-filter: blur(24px);
            padding: 48px 40px;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(99, 102, 241, 0.2);
            max-width: 420px;
            margin: 0 auto;
        }
        
        /* Kartu Metrik - Variasi Warna */
        .metric-positive {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.05) 100%);
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(34, 197, 94, 0.1);
        }
        .metric-negative {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
        }
        .metric-neutral {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);
        }

        /* Komponen Badge/Label */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-green {
            background: linear-gradient(90deg, #10b981, #059669);
            color: white;
        }
        .badge-blue {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white;
        }
        .badge-purple {
            background: linear-gradient(90deg, #8b5cf6, #7c3aed);
            color: white;
        }
        .badge-red {
            background: linear-gradient(90deg, #ef4444, #dc2626);
            color: white;
        }
        .badge-yellow {
            background: linear-gradient(90deg, #f59e0b, #d97706);
            color: white;
        }
        
        /* Input & Text Area */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(15, 23, 42, 0.8) !important;
            color: #e5e7eb !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 0.95rem;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            outline: none;
        }
        
        /* Gaya Metrik Bawaan Streamlit */
        div[data-testid="stMetric"] {
            background: rgba(26, 31, 58, 0.6);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid rgba(99, 102, 241, 0.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        div[data-testid="stMetricLabel"] {
            color: #9ca3af !important;
            font-weight: 500;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetricValue"] {
            color: #f3f4f6 !important;
            font-weight: 700;
            font-size: 2rem;
        }
        
        /* Tombol Utama (Primary) */
        .stButton button[type="primary"] {
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            border: none;
            color: white;
            font-weight: 600;
            padding: 12px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 0.3px;
        }
        .stButton button[type="primary"]:hover {
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.6);
            transform: translateY(-2px);
            background: linear-gradient(90deg, #8b5cf6, #6366f1);
        }

        /* Tombol Sekunder */
        .stButton button:not([type="primary"]) {
            background-color: rgba(26, 31, 58, 0.6);
            color: #e5e7eb;
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 10px;
            transition: all 0.2s ease;
        }
        .stButton button:not([type="primary"]):hover {
            border-color: #6366f1;
            background-color: rgba(99, 102, 241, 0.1);
        }
        
        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #f3f4f6 !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #fff, #e5e7eb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: rgba(26, 31, 58, 0.6) !important;
            color: #e5e7eb !important;
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.1);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0e27;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.3);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.5);
        }

        /* Table Rows Hover */
        .stDataFrame tbody tr:hover {
            background-color: rgba(99, 102, 241, 0.05) !important;
        }

        /* Tombol Navigasi Sidebar Custom */
        .stButton button {
            background: transparent;
            border: 1px solid transparent;
            color: #9ca3af;
            font-size: 0.95rem;
            font-weight: 500;
            padding: 14px 16px;
            border-radius: 12px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: left;
        }
        
        .stButton button:hover {
            background: rgba(99, 102, 241, 0.08);
            border-color: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            transform: translateX(4px);
        }

        /* Make sidebar buttons full width and left aligned */
        section[data-testid="stSidebar"] .stButton {
            width: 100%;
        }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            justify-content: flex-start;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Tampilin sidebar kustom kita dan umpetin yang bawaan Streamlit."""
    with st.sidebar:
        # 1. HIDE Navigasi Bawaan (Wajib biar ga ganda)
        st.markdown("""
            <style>
            /* Navigasi Bawaan disembunyikan via config.toml, 
               tapi kita kasih backup hide biar aman */
            .stApp > header { display: none !important; }
            
            div[data-testid="stSidebarNav"] {
                display: none !important;
            }
            
            div[data-testid="stPageLink-NavLink"] {
                display: flex;
                align-items: center;
                padding: 12px 20px;
                border-radius: 12px;
                margin-bottom: 8px;
                background: transparent;
                border: none;
                color: #8f95b2; /* Abu-abu kalem */
                text-decoration: none;
                font-weight: 500;
                transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
            }
            
            div[data-testid="stPageLink-NavLink"]:hover {
                color: #ffffff;
                background: rgba(42, 46, 60, 0.5); /* Terang dikit pas hover */
            }
            
            /* Status Aktif - Background Biru/Ungu Gelap Solid (Mirip Referensi) */
            div[data-testid="stPageLink-NavLink"][aria-current="page"] {
                background: #2b2d42;
                background: linear-gradient(90deg, rgba(40, 40, 60, 1) 0%, rgba(35, 35, 55, 1) 100%);
                border: 1px solid rgba(139, 92, 246, 0.2);
                color: #ffffff;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            /* Warna Ikon */
            div[data-testid="stPageLink-NavLink"] i {
                color: inherit; 
                font-size: 1.2rem;
            }

            /* Umpetin tombol tersembunyi, jaga-jaga aja */
            .nav-hidden-btn { display: none; }
            </style>
        """, unsafe_allow_html=True)
        
        # 2. Header Sidebar (Logo & Tulisan Smart POS)
        st.markdown("""
            <div style='
                background: #1e1e2d;
                border-radius: 20px;
                padding: 30px 20px;
                margin-bottom: 30px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.05);
                box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.3);
            '>
                <div style='
                    background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
                    width: 64px;
                    height: 64px;
                    border-radius: 16px;
                    margin: 0 auto 16px auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 32px;
                    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
                '>
                    🛍️
                </div>
                <h3 style='
                    margin: 0;
                    color: #ffffff;
                    font-weight: 700;
                    font-size: 1.5rem;
                    letter-spacing: 0.5px;
                '>Smart POS</h3>
                <p style='
                    margin: 8px 0 0 0;
                    color: #6c7293;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                '>Point of Sale</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 3. Item Navigasi (Pake Material Icons biar modern)
        nav_items = []
        
        # Cek role user dulu
        role = st.session_state.get("role", None)

        if role == "admin":
            nav_items.append({
                "name": "Dashboard Admin",
                "page": "pages/1_Admin_Dashboard.py",
                "icon": ":material/analytics:" 
            })
            
            nav_items.append({
                "name": "Inventaris",
                "page": "pages/3_Inventory.py",
                "icon": ":material/inventory_2:"
            })
        
        nav_items.append({
            "name": "Kasir POS",
            "page": "pages/2_Cashier_POS.py",
            "icon": ":material/shopping_cart:"
        })
        
        nav_items.append({
            "name": "Transaksi",
            "page": "pages/4_Transactions.py",
            "icon": ":material/receipt_long:"
        })

        # Menambahkan menu 'App'
        nav_items.append({
            "name": "App",
            "page": "app.py", 
            "icon": ":material/apps:"
        })
        
        # 4. Render Links
        for item in nav_items:
            st.page_link(item['page'], label=item['name'], icon=item['icon'])
        
        # Spacer 
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True) 


