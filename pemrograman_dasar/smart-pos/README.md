# 🛍️ Smart POS System

Sistem Point of Sale (POS) modern yang dibangun dengan **FastAPI** (Backend) dan **Streamlit** (Frontend). Aplikasi ini dirancang untuk mempermudah manajemen toko dengan fitur lengkap mulai dari kasir, inventaris, hingga laporan penjualan.

---

## 👨‍💻 Tim Pengembang

**Dibuat Oleh: BUDIONO SIREGAR**

### Anggota Kelompok:
1. **ISA ALI ARRUMY** - 24.83.1056
2. **IKHSANUL FIKRI** - 24.83.1084
3. **MUHAMAD DARUS SALAM** - 24.83.1063

---

## ✨ Fitur Utama

### 🔐 Autentikasi
- Login dengan role **Admin** dan **Kasir**
- Session management yang aman
- Auto-redirect ke login saat refresh

### 📦 Manajemen Produk
- CRUD lengkap untuk produk
- Kategori produk
- Tracking stok real-time
- Barcode support

### 💳 Sistem Kasir
- Keranjang belanja interaktif
- Validasi stok otomatis
- Cetak struk transaksi
- Pencarian produk cepat

### 📊 Dashboard & Laporan
- Grafik tren penjualan
- Statistik revenue & profit
- Alert stok rendah
- Riwayat transaksi lengkap

### 🎨 UI/UX Premium
- Dark mode dengan tema modern
- Animasi transisi halus
- Glassmorphism design
- Responsive layout

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
streamlit run frontend/app.py
```

> **Note:** Backend akan otomatis dijalankan saat aplikasi dimulai. Tunggu sampai muncul pesan "System Connected!" di browser.

### 3. Default Login
- **Admin**:
  - Username: `admin`
  - Password: `admin123`
- **Kasir**:
  - Username: `cashier`
  - Password: `cashier123`

---

## 📁 Struktur Folder

```
smart-pos/
  backend/
    routers/          # API endpoints
    models.py         # Database models
    schemas.py        # Pydantic schemas
    crud.py           # Database operations
    auth.py           # Authentication
    main.py           # FastAPI app
  frontend/
    pages/            # Streamlit pages
    app.py            # Main app
    utils.py          # Helper functions
  .streamlit/
    config.toml       # Streamlit config
```

---

## 🛠️ Teknologi yang Digunakan

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: Streamlit, Pandas, Plotly
- **Auth**: JWT (JSON Web Tokens)
- **UI**: Custom CSS, Glassmorphism

---



---

**© 2026 Smart POS - Point of Sale System**
