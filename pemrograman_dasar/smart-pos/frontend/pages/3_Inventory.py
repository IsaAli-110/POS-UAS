import streamlit as st
import pandas as pd
from utils import api_request, load_css, render_sidebar

st.set_page_config(page_title="Inventory Management", layout="wide", page_icon="📦")
load_css()
render_sidebar()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("app.py")

if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("Maaf, halaman ini khusus Admin.")
    st.stop()

st.title("📦 Manajemen Inventaris")
st.markdown("<p style='color: #9ca3af; margin-top: -10px;'>Tambah, hapus, dan edit stok barang di sini.</p>", unsafe_allow_html=True)
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Navigasi Tab (Produk & Kategori)
tab1, tab2 = st.tabs(["📦 Produk", "🏷️ Kategori"])

# ========== TAB 1: PRODUK ==========
with tab1:
    # Layout 2 Kolom (Kiri: Form, Kanan: Tabel)
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        # --- Bagian Form Tambah/Edit ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Fetch categories for dropdown
        categories = api_request("GET", "/products/categories/")
        cat_options = {c["name"]: c["id"] for c in categories} if categories else {}
        
        # Add New Product
        with st.expander("➕ Tambah Produk Baru", expanded=True):
            col_form1, col_form2 = st.columns(2)
            with col_form1:
                new_name = st.text_input("Nama Produk", key="prod_name")
                new_barcode = st.text_input("Barcode", key="prod_barcode")
                new_price = st.number_input("Harga (Rp)", min_value=0.0, step=100.0, key="prod_price")
            with col_form2:
                new_stock = st.number_input("Stok Awal", min_value=0, step=1, key="prod_stock")
                
                if cat_options:
                    selected_cat_name = st.selectbox("Kategori", list(cat_options.keys()), key="prod_cat")
                    selected_cat_id = cat_options.get(selected_cat_name)
                else:
                    st.warning("⚠️ Kategori kosong. Buat dulu di tab sebelah.")
                    selected_cat_id = None

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            if st.button("Simpan Produk", type="primary", key="add_prod_btn", use_container_width=True):
                if new_name and new_barcode and selected_cat_id:
                    data = {
                        "name": new_name,
                        "barcode": new_barcode,
                        "price": new_price,
                        "stock": new_stock,
                        "category_id": selected_cat_id
                    }
                    res = api_request("POST", "/products/", data=data)
                    if res:
                        st.toast("✅ Produk berhasil disimpan!")
                        st.rerun()
                else:
                    st.error("Isi semua data dulu ya, termasuk kategorinya.")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # --- Bagian Tabel Produk ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Daftar Produk")
        
        products = api_request("GET", "/products/")
        if products:
            p_df = pd.DataFrame(products)
            
            # Fitur Pencarian
            search_query = st.text_input("🔍 Cari Barang", placeholder="Nama atau Barcode...", key="search_prod_list")
            if search_query:
                p_df = p_df[p_df['name'].str.contains(search_query, case=False) | p_df['barcode'].str.contains(search_query, case=False)]
            
            # Tampilkan Tabel (pake st.dataframe biar lebih interaktif)
            st.dataframe(
                p_df[['barcode', 'name', 'price', 'stock']],
                column_config={
                    "barcode": "Barcode",
                    "name": "Nama Produk",
                    "price": st.column_config.NumberColumn("Harga (Rp)", format="Rp %d"),
                    "stock": "Stok"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Tombol Aksi (Edit & Hapus) di bawah tabel
            st.markdown("### Aksi Produk")
            
            # Pake expander biar ga menuuhin layar
            with st.expander("🛠️ Klik untuk Edit/Hapus Produk"):
                selected_barcode = st.selectbox("Pilih Produk:", p_df['barcode'].tolist(), format_func=lambda x: f"{x} - {p_df[p_df['barcode'] == x]['name'].iloc[0]}")
                
                if selected_barcode:
                    selected_prod = p_df[p_df['barcode'] == selected_barcode].iloc[0]
                    
                    c_act1, c_act2 = st.columns(2)
                    with c_act1:
                         # --- Mode Edit (Simulasi aja karena butuh form edit stateful) ---
                        if st.button("✏️ Edit Stock / Harga", use_container_width=True):
                             st.info(f"Produk terpilih: {selected_prod['name']}. Silakan hubungi admin untuk edit detail.")
                    
                    with c_act2:
                        # --- Tombol Hapus ---
                        if st.button("🗑️ Hapus Produk", type="primary", use_container_width=True):
                            res = api_request("DELETE", f"/products/{selected_prod['id']}")
                            if res:
                                st.success(f"Produk {selected_prod['name']} dihapus.")
                                st.rerun()
        else:
            st.info("Belum ada data produk nih.")
        
        st.markdown("</div>", unsafe_allow_html=True)


# ========== TAB 2: KATEGORI ==========
with tab2:
    st.subheader("🏷️ Manajemen Kategori")
    
    # Form Tambah Kategori
    with st.expander("➕ Tambah Kategori Baru", expanded=True):
        new_cat_name = st.text_input("Nama Kategori", placeholder="Contoh: Elektronik, Makanan, Minuman", key="cat_name")
        if st.button("Simpan Kategori", type="primary", key="add_cat_btn"):
            if new_cat_name.strip():
                data = {"name": new_cat_name.strip()}
                res = api_request("POST", "/products/categories/", data=data)
                if res:
                    st.toast("✅ Kategori berhasil disimpan!")
                    st.rerun()
            else:
                st.error("Nama kategori gaboleh kosong ya.")
    
    st.markdown("---")
    
    # List Kategori
    categories = api_request("GET", "/products/categories/")
    if categories:
        st.subheader("📋 Semua Kategori")
        
        c1, c2, c3 = st.columns([1, 4, 1])
        c1.markdown("**ID**")
        c2.markdown("**Nama Kategori**")
        c3.markdown("**Aksi**")
        
        for cat in categories:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 1])
                c1.write(cat['id'])
                c2.write(cat['name'])
                with c3:
                    if st.button("🗑️", key=f"del_cat_{cat['id']}", help="Hapus Kategori"):
                        # Cek dulu ada produknya ga
                        all_products = api_request("GET", "/products/")
                        has_products = any(p.get('category', {}).get('id') == cat['id'] for p in (all_products or []))
                        
                        if has_products:
                            st.error("⚠️ Gabisa dihapus, masih ada produk di kategori ini!")
                        else:
                            res = api_request("DELETE", f"/products/categories/{cat['id']}")
                            if res:
                                st.toast("🗑️ Kategori dihapus")
                                st.rerun()
    else:
        st.info("📭 Belum ada kategori. Bikin dulu di atas ya!")
