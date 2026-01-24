import streamlit as st
import pandas as pd
from utils import api_request, load_css, render_sidebar

st.set_page_config(page_title="Cashier POS", layout="wide", page_icon="🛒")
load_css()
render_sidebar()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("app.py")

# Allow both cashier and admin
if "role" not in st.session_state or st.session_state.role not in ["cashier", "admin"]:
    st.warning("Access Denied. Authorized personnel only.")
    st.stop()

# Helper to prevent widget key duplication
if "cart" not in st.session_state:
    st.session_state.cart = []

# Layout Aplikasi Kasir
col_left, col_right = st.columns([1.8, 1.2])

with col_left:
    st.title("🛒 Kasir POS")
    st.markdown("<p style='color: #9ca3af; margin-top: -10px;'>Pilih barang, masukkan keranjang, bayar!</p>", unsafe_allow_html=True)
    
    # Ambil data produk
    products = api_request("GET", "/products/")
    
    if products:
        # Kotak Pencarian Barang
        search = st.text_input("🔍 Search Product", "", placeholder="Name or Barcode...")
        filtered_products = [p for p in products if search.lower() in p['name'].lower() or search in p['barcode']]
        
        # Grid Layout
        cols = st.columns(3)
        for idx, p in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.write(f"**{p['name']}**")
                    st.write(f"Rp {p['price']:,.0f}")
                    st.caption(f"Stock: {p['stock']}")
                    
                    if p['stock'] > 0:
                        if st.button("Add", key=f"add_{p['id']}", use_container_width=True):
                            # Add to cart logic
                            existing = next((item for item in st.session_state.cart if item['product_id'] == p['id']), None)
                            if existing:
                                if existing['quantity'] + 1 <= p['stock']:
                                    existing['quantity'] += 1
                                    st.toast(f"Added another {p['name']}")
                                else:
                                    st.error("No more stock")
                            else:
                                st.session_state.cart.append({
                                    "product_id": p['id'],
                                    "name": p['name'],
                                    "price": p['price'],
                                    "quantity": 1
                                })
                                st.toast(f"Added {p['name']}")
                    else:
                        st.error("Out of Stock")
    else:
        st.info("No products available.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧾 Current Order")
    
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df['Total'] = cart_df['price'] * cart_df['quantity']
        
        # Display Cart Items
        for index, row in cart_df.iterrows():
            c1, c2, c3 = st.columns([3,1,1])
            with c1:
                st.write(f"**{row['name']}**")
                st.caption(f"@{row['price']:,.0f}")
            with c2:
                st.write(f"x{row['quantity']}")
            with c3:
                 st.write(f"{row['Total']:,.0f}")
        
        st.divider()
        total_amount = cart_df['Total'].sum()
        st.title(f"Rp {total_amount:,.0f}")
        
        if st.button("Charge / Checkout", type="primary", use_container_width=True):
            items_payload = [{"product_id": item['product_id'], "quantity": item['quantity']} for item in st.session_state.cart]
            payload = {"items": items_payload}
            
            # Save cart for receipt BEFORE clearing
            receipt_items = st.session_state.cart.copy()
            
            res = api_request("POST", "/transactions/", data=payload)
            if res:
                st.session_state.cart = []
                st.balloons()
                
                # Show Receipt
                st.success("✅ Transaction Successful!")
                with st.expander("🖨️ View Receipt", expanded=True):
                    st.markdown("""
                        <div style="background-color: white; color: black; padding: 20px; border-radius: 10px; font-family: monospace;">
                            <h3 style="text-align: center; color: black; margin: 0;">SMART POS SYSTEM</h3>
                            <p style="text-align: center; color: black; margin: 5px 0;">Jl. Teknologi Digital No. 123</p>
                            <p style="text-align: center; color: black; margin: 5px 0;">Tel: (021) 1234-5678</p>
                            <hr style="border-top: 1px dashed black;">
                    """, unsafe_allow_html=True)
                    
                    # Transaction details
                    st.markdown(f"""
                        <div style="background-color: white; color: black; font-family: monospace;">
                            <p style="color: black;"><b>Transaction ID:</b> #{res['id']}</p>
                            <p style="color: black;"><b>Cashier:</b> {st.session_state.username}</p>
                            <hr style="border-top: 1px dashed black;">
                    """, unsafe_allow_html=True)
                    
                    # Items
                    for item in receipt_items:
                        st.markdown(f"""
                            <div style="background-color: white; color: black; font-family: monospace; margin: 5px 0;">
                                <b style="color: black;">{item['name']}</b><br>
                                <span style="color: black;">{item['quantity']} x Rp {item['price']:,.0f} = Rp {item['quantity'] * item['price']:,.0f}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <hr style="border-top: 1px dashed black;">
                        <div style="background-color: white; color: black; font-family: monospace;">
                            <h3 style="color: black; text-align: right; margin: 10px 0;">TOTAL: Rp {res['total_amount']:,.0f}</h3>
                            <hr style="border-top: 1px dashed black;">
                            <p style="text-align: center; color: black; margin: 10px 0;">Thank you for shopping!</p>
                            <p style="text-align: center; color: black; font-size: 0.85rem;">Visit us again soon 😊</p>
                        </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("✅ Close Receipt", use_container_width=True):
                        st.rerun()

        
        if st.button("Clear Cart", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
    else:
        st.info("Cart is empty. Add products from the left.")
        
    st.markdown("</div>", unsafe_allow_html=True)
