import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap 
import numpy as np

st.set_page_config(
    page_title="GIS Bengkel Honda Jateng",
    layout="wide",
    initial_sidebar_state="expanded"
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    return distance

def load_data():
    df = pd.read_csv('data/bengkel_honda_jateng_final.csv')
    return df

try:
    df = load_data()
except:
    st.error("File 'bengkel_honda_jateng_final.csv' tidak ditemukan.")
    df = pd.DataFrame()

# CSS CUSTOM
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .main .block-container { padding: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Sistem Informasi Geografis Bengkel Honda")
st.caption("Visualisasi Data Bengkel Resmi Wilayah Jawa Tengah")

# Sidebar
with st.sidebar:
    st.header("📍 Lokasi Pengguna")
    user_lat = st.number_input("Latitude", value=-7.15097500, format="%.8f")
    user_lon = st.number_input("Longitude", value=110.14025940, format="%.8f")
    st.divider()
    st.info("Koordinat di atas digunakan sebagai titik pusat pencarian bengkel terdekat.")

# Logic hitung lokasi terdekat
if not df.empty:
    df['Jarak_KM'] = df.apply(
        lambda row: haversine(user_lat, user_lon, row['Latitude'], row['Longitude']), 
        axis=1
    )
    df_terdekat = df.sort_values('Jarak_KM').head(3)

# Main Layout
st.subheader("Peta Persebaran")
m = folium.Map(location=[user_lat, user_lon], zoom_start=9)

# 1. HEATMAP (Layer Paling Bawah)
if not df.empty:
    heat_data = [[row['Latitude'], row['Longitude']] for _, row in df.iterrows() if abs(row['Latitude']) <= 90]
    HeatMap(heat_data, radius=15, blur=10, max_zoom=13).add_to(m)

# 2. MARKER PENGGUNA
folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Lokasi Anda Sekarang</b>",
    icon=folium.Icon(color='red', icon='user', prefix='fa')
).add_to(m)

# 3. MARKER BENGKEL 
if not df.empty:
    for i, row in df.iterrows():
        if pd.isna(row['Latitude']) or abs(row['Latitude']) > 90:
            continue
            
        warna = 'green' if row['Nama'] in df_terdekat['Nama'].values else 'blue'

        popup_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 12px; width: 200px;">
                <b style="font-size:14px; color:#c0392b;">{row['Nama']}</b><br>
                <b>Alamat:</b> {row['Alamat']}<br>
                <b>Wilayah:</b> {row['Kabupaten']}<br>
                <hr style="margin:5px 0;">
                <b>Jarak:</b> {row['Jarak_KM']:.2f} KM
            </div>
        """

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=warna)
        ).add_to(m)

st_folium(m, width="100%", height=500)

st.divider()
st.header(" 3 Bengkel Terdekat")

if not df.empty:
    cols = st.columns(3)
    for idx, (i, row) in enumerate(df_terdekat.iterrows()):
        with cols[idx]:
            st.success(f"**{row['Nama']}**")
            st.write(f"{row['Alamat']}")
            st.write(f"Jarak: **{row['Jarak_KM']:.2f} KM**")
            st.caption(f"Wilayah: {row['Kabupaten']}")

st.divider()
col_stats, col_table = st.columns([1, 2])

with col_stats:
    st.subheader("Statistik")
    st.metric(label="Total Bengkel Terdata", value=len(df))
    st.bar_chart(df['Kabupaten'].value_counts().head(5))

with col_table:
    st.subheader("Data Lengkap")
    st.dataframe(df[['Nama', 'Kabupaten', 'Jarak_KM']].sort_values('Jarak_KM'), use_container_width=True)