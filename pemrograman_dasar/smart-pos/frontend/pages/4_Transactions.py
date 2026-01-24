import streamlit as st
import pandas as pd
from datetime import datetime
from utils import api_request, load_css, render_sidebar

st.set_page_config(page_title="Transaction History", layout="wide", page_icon="📜")
load_css()
render_sidebar()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("app.py")

if "role" not in st.session_state:
    st.warning("Eits, login dulu dong.")
    st.stop()
    
# Layout Header
col1, col2 = st.columns([2, 1])
with col1:
    st.title("📜 Riwayat Transaksi")
    st.markdown("<p style='color: #9ca3af; margin-top: -10px;'>Cek semua penjualan yang udah masuk di sini.</p>", unsafe_allow_html=True)
with col2:
    # Filter Tanggal (Biar gampang cari data berdasarkan waktu)
    selected_date = st.date_input("📅 Filter Tanggal", value=datetime.now())

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Ambil data transaksi dari API
transactions = api_request("GET", "/transactions/")

if transactions:
    # Ubah ke DataFrame biar enak diolah pake Pandas
    df = pd.DataFrame(transactions)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at', ascending=False)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # --- Bagian Pencarian & Filter ---
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Cari Transaksi", placeholder="Ketik ID Order atau nominal...", key="search_tx")
    with col_filter:
        date_filter = st.selectbox("Rentang Waktu", ["Semua", "Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir"], key="filter_date")
    
    # Logic Filter Data
    filtered_df = df.copy()
    
    # 1. Filter Pencarian Teks
    if search_term:
        filtered_df = filtered_df[
            filtered_df['id'].astype(str).str.contains(search_term, case=False) |
            filtered_df['total_amount'].astype(str).str.contains(search_term, case=False)
        ]
    
    # 2. Filter Tanggal (Override selected_date di atas kalo dropdown dipake, atau combine logicnya)
    # Disini kita pake logic dropdown date_filter aja biar lebih clean
    if date_filter == "Hari Ini":
        today = datetime.now().date()
        filtered_df = filtered_df[filtered_df['created_at'].dt.date == today]
    elif date_filter == "7 Hari Terakhir":
        week_ago = datetime.now() - pd.Timedelta(days=7)
        filtered_df = filtered_df[filtered_df['created_at'] >= week_ago]
    elif date_filter == "30 Hari Terakhir":
        month_ago = datetime.now() - pd.Timedelta(days=30)
        filtered_df = filtered_df[filtered_df['created_at'] >= month_ago]
    
    # Kalo user pilih tanggal specific di date picker atas, kita bisa filter lagi (opsional)
    # filtered_df = filtered_df[filtered_df['created_at'].dt.date == selected_date] 
    
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"📋 Daftar Order ({len(filtered_df)})")
        
        # Header Tabel
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 2, 1.5, 1, 1])
        c1.markdown("**ID Order**")
        c2.markdown("**Waktu**")
        c3.markdown("**Kasir**")
        c4.markdown("**Jumlah Item**")
        c5.markdown("**Total (Rp)**")
        c6.markdown("**Detail**")
        c7.markdown("**Hapus**")
        
        # Baris Tabel
        for idx, row in filtered_df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 2, 1.5, 1, 1])
                
                # ID dengan badge
                c1.markdown(f"<span class='badge badge-blue'>#{row['id']}</span>", unsafe_allow_html=True)
                
                # Waktu
                c2.write(row['created_at'].strftime('%d %b %Y, %H:%M'))
                
                # Nama Kasir
                cashier_name = row.get('cashier', {}).get('username', f"User #{row['cashier_id']}")
                c3.write(cashier_name)
                
                # Jumlah Item
                item_count = len(row.get('items', []))
                c4.write(f"{item_count} barang")
                
                # Total Harga (Hijau biar cuan)
                c5.markdown(f"<span style='color: #22c55e; font-weight: 700;'>Rp {row['total_amount']:,.0f}</span>", unsafe_allow_html=True)
                
                # Tombol Detail
                with c6:
                    if st.button("👁️", key=f"view_{row['id']}", help="Lihat Detail"):
                        st.session_state[f"show_detail_{row['id']}"] = not st.session_state.get(f"show_detail_{row['id']}", False)
                
                # Tombol Delete
                with c7:
                    if st.button("🗑️", key=f"del_{row['id']}", help="Hapus Transaksi", type="primary"):
                        res = api_request("DELETE", f"/transactions/{row['id']}")
                        if res:
                            st.toast(f"✅ Transaksi #{row['id']} berhasil dihapus")
                            st.rerun()
                        else:
                            st.error("Gagal menghapus transaksi")
                
                # Tampilkan detail kalo diklik
                if st.session_state.get(f"show_detail_{row['id']}", False):
                    st.markdown("---")
                    st.markdown("**📦 Barang yang dibeli:**")
                    
                    if 'items' in row and row['items']:
                        for item in row['items']:
                            product_name = item.get('product', {}).get('name', f"Product #{item['product_id']}")
                            st.markdown(f"""
                                <div style='background: rgba(99, 102, 241, 0.05); padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #6366f1;'>
                                    <b>{product_name}</b><br>
                                    <span style='color: #9ca3af;'>Qty: {item['quantity']} × Rp {item['price_at_sale']:,.0f} = Rp {item['quantity'] * item['price_at_sale']:,.0f}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div style='text-align: right; margin-top: 16px;'>
                                <span style='font-size: 1.2rem; color: #22c55e; font-weight: 700;'>Total Bayar: Rp {row['total_amount']:,.0f}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption("Detail barang ga kebaca nih.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Ga nemu transaksi yang dicari.")

else:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.info("📭 Belum ada transaksi sama sekali. Yuk jualan dulu!")
    st.markdown("</div>", unsafe_allow_html=True)
