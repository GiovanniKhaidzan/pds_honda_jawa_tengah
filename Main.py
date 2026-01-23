import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

st.set_page_config(
    page_title="GIS Bengkel Honda Jateng",
    layout="wide",
    initial_sidebar_state="expanded"
)

def haversine(lat1, lon1, lat2, lon2):
    # radius bumi dalam kilometer
    R = 6371.0
    # ubah derajat ke radian
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # rumus
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

#sidebar
with st.sidebar:
    st.header("Lokasi Pengguna")
    user_lat = st.number_input("Latitude", value=-7.15097500, format="%.8f")
    user_lon = st.number_input("Longitude", value=110.14025940, format="%.8f")
    st.divider()
    st.info("Koordinat di atas digunakan sebagai titik pusat pencarian bengkel terdekat.")

#logic hitung lokasi terdekat
if not df.empty:
    df['Jarak_KM'] = df.apply(
        lambda row: haversine(user_lat, user_lon, row['Latitude'], row['Longitude']), 
        axis=1
    )
    df_terdekat = df.sort_values('Jarak_KM').head(3)

#mainlayout
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("Peta Persebaran")
    m = folium.Map(location=[user_lat, user_lon], zoom_start=9)
    
    # Marker Pengguna
    folium.Marker(
        location=[user_lat, user_lon],
        popup="<b>Lokasi Anda Sekarang</b>",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)

    # Marker Bengkel
if not df.empty:
    for i, row in df.iterrows():
        warna = 'green' if row['Nama'] in df_terdekat['Nama'].values else 'blue'
       
        popup_html = f"""
        <div style="
            font-family: Arial, sans-serif;
            font-size: 13px;
            line-height: 1.4;
            width: 220px;
        ">
            <b style="font-size:14px;">{row['Nama']}</b><br>
            <span>{row['Alamat']}</span><br>
            <span>{row['Kabupaten']}</span>
            <hr style="margin:6px 0;">
            <span><b>Jarak:</b> {row['Jarak_KM']:.2f} KM</span>
        </div>
        """

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=warna)
        ).add_to(m)

               

    st_folium(m, width="100%", height=450)

with col_stats:
    st.subheader("Statistik")
    st.metric(label="Total Bengkel di CSV", value=len(df))


st.divider()
st.header("Bengkel Terdekat dari Lokasi Anda")

if not df.empty:
    cols = st.columns(3)
    for idx, (i, row) in enumerate(df_terdekat.iterrows()):
        with cols[idx]:
            st.success(f"**{row['Nama']}**")
            st.write(f"{row['Alamat']}")
            st.write(f"Jarak: **{row['Jarak_KM']:.2f} KM**")
            st.caption(f"Wilayah: {row['Kabupaten']}")

# FOOTER DATA TABLE
st.divider()
