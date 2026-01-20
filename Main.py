import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Konfigurasi Halaman
st.set_page_config(
    page_title="GIS Bengkel Honda Jabar",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI LOAD DATA ---

def load_data():
    df = pd.read_csv('data/bengkel_honda_jabar.csv')
    return df

try:
    df = load_data()
except:
    st.error("File 'bengkel_honda_jabar.csv' tidak ditemukan. Pastikan file ada di folder yang sama.")
    df = pd.DataFrame()

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .main .block-container { padding: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- JUDUL ---
st.title("Sistem Informasi Geografis Bengkel Honda")
st.caption("Visualisasi Data Bengkel Resmi Wilayah Jawa Barat")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Lokasi Pengguna")
    user_lat = st.number_input("Latitude", value=-6.9175)
    user_lon = st.number_input("Longitude", value=107.6191)
    
    st.divider()
    st.header("3 Terdekat")
    st.info("Fitur hitung jarak dikerjakan berdasarkan lokasi pengguna di sini.")

# --- MAIN LAYOUT ---
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("Peta Persebaran")
    
    # Inisialisasi Peta
    m = folium.Map(location=[user_lat, user_lon], zoom_start=9)
    
    # POINT 1: TAMPILKAN DATA DARI CSV KE PETA
    if not df.empty:
        for i, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"<b>{row['Nama']}</b><br>{row['Alamat']}",
                icon=folium.Icon(color='blue')
            ).add_to(m)

    st_folium(m, width="100%", height=450)

with col_stats:
    st.subheader("Statistik")
    st.metric(label="Total Bengkel di CSV", value=len(df))
    st.write("Grafik per kabupaten dikerjakan di sini.")

# --- FOOTER / DATA TABLE (POINT 1: TAMPILKAN DATA CSV) ---
st.divider()
st.subheader("Daftar Seluruh Bengkel (Data CSV)")

if not df.empty:
    # Menampilkan tabel data langsung dari file CSV
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Data kosong atau file belum terbaca.")