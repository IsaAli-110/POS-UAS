import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import api_request, load_css, render_sidebar

st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="📈")
load_css()
render_sidebar()

if "token" not in st.session_state or st.session_state.token is None:
    st.switch_page("app.py")

# Cek role dulu, kalo bukan admin tendang aja
if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("Access Denied. Admins only.")
    st.stop()

st.title("📈 Executive Dashboard")
st.markdown("<p style='color: #9ca3af; margin-top: -10px;'>Pantau semua statistik bisnis di sini</p>", unsafe_allow_html=True)

# Tarik data transaksi dari API
transactions = api_request("GET", "/transactions/")

if transactions:
    t_df = pd.DataFrame(transactions)
    t_df['created_at'] = pd.to_datetime(t_df['created_at'])
    
    # --- KPI Utama (Kartu-kartu di atas) ---
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
            <div class='metric-neutral'>
                <p style='color: #9ca3af; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 0;'>Total Transactions</p>
                <h2 style='color: #f3f4f6; font-size: 2.5rem; font-weight: 800; margin: 8px 0 0 0;'>{}</h2>
                <p style='color: #a5b4fc; font-size: 0.8rem; margin: 4px 0 0 0;'>Lifetime</p>
            </div>
        """.format(len(t_df)), unsafe_allow_html=True)
    
    with c2:
        revenue = t_df['total_amount'].sum()
        st.markdown("""
            <div class='metric-positive'>
                <p style='color: #86efac; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 0;'>Total Revenue</p>
                <h2 style='color: #22c55e; font-size: 2.5rem; font-weight: 800; margin: 8px 0 0 0;'>Rp {:,.0f}</h2>
                <p style='color: #86efac; font-size: 0.8rem; margin: 4px 0 0 0;'>Revenue records</p>
            </div>
        """.format(revenue), unsafe_allow_html=True)
    
    with c3:
        avg_order = t_df['total_amount'].mean()
        st.markdown("""
            <div class='metric-neutral'>
                <p style='color: #9ca3af; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 0;'>Avg. Order Value</p>
                <h2 style='color: #a5b4fc; font-size: 2.5rem; font-weight: 800; margin: 8px 0 0 0;'>Rp {:,.0f}</h2>
                <p style='color: #a5b4fc; font-size: 0.8rem; margin: 4px 0 0 0;'>Per transaction</p>
            </div>
        """.format(avg_order), unsafe_allow_html=True)
    
    with c4:
        profit = revenue * 0.3
        st.markdown("""
            <div class='metric-positive'>
                <p style='color: #86efac; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 0;'>Est. Profit</p>
                <h2 style='color: #22c55e; font-size: 2.5rem; font-weight: 800; margin: 8px 0 0 0;'>Rp {:,.0f}</h2>
                <p style='color: #86efac; font-size: 0.8rem; margin: 4px 0 0 0;'>~30% Margin</p>
            </div>
        """.format(profit), unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # --- Baris Grafik Chart ---
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Tren Pendapatan")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem; margin-top: -8px;'>Grafik pemasukan seiring waktu</p>", unsafe_allow_html=True)
        
        sales_over_time = t_df.set_index('created_at').resample('H')['total_amount'].sum().reset_index()
        
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=sales_over_time['created_at'], 
            y=sales_over_time['total_amount'],
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.2)',
            line=dict(color='#6366f1', width=3),
            mode='lines',
            name='Revenue'
        ))
        
        fig_area.update_layout(
            xaxis_title="Time", 
            yaxis_title="Revenue (Rp)", 
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#e5e7eb"),
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=False,
            hovermode='x unified'
        )
        st.plotly_chart(fig_area, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Category Sales")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem; margin-top: -8px;'>Product distribution</p>", unsafe_allow_html=True)
        
        products = api_request("GET", "/products/")
        if products:
            p_df = pd.DataFrame(products)
            p_df['category_name'] = p_df['category'].apply(lambda x: x['name'] if x else 'Uncategorized')
            cat_counts = p_df['category_name'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=cat_counts['Category'],
                values=cat_counts['Count'],
                hole=0.5,
                marker=dict(colors=['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']),
                textfont=dict(size=14, color='white')
            )])
            
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#e5e7eb"),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
                margin=dict(l=20, r=60, t=10, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Low Stock Alert Table ---
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔥 Inventory Alerts")
    st.markdown("<p style='color: #9ca3af; font-size: 0.85rem; margin-top: -8px;'>Low stock items requiring attention</p>", unsafe_allow_html=True)
    
    products = api_request("GET", "/products/")
    if products:
        p_df = pd.DataFrame(products)
        low_stock = p_df[p_df['stock'] < 10].sort_values('stock')
        
        if not low_stock.empty:
            st.warning(f"⚠️ {len(low_stock)} Products are Low on Stock!")
            st.dataframe(
                low_stock[['name', 'stock', 'price']],
                column_config={
                    "name": "Product Name",
                    "stock": st.column_config.ProgressColumn("Stock Level", min_value=0, max_value=20, format="%d"),
                    "price": st.column_config.NumberColumn("Price", format="Rp %d")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ All stock levels are healthy.")
            
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("📭 No transaction data available. Start selling in the POS!")
