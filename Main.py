import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap 
import numpy as np
import matplotlib.pyplot as plt

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
    st.header("Lokasi Pengguna")
    user_lat = st.number_input("Latitude", value=-6.99049680, format="%.8f")
    user_lon = st.number_input("Longitude", value=110.42294450, format="%.8f")
    st.divider()
    st.info("Koordinat di atas digunakan sebagai titik pusat pencarian bengkel terdekat.")
    show_heatmap = st.checkbox("Tampilkan Heatmap", value=True)
    show_markers = st.checkbox("Tampilkan Marker Bengkel", value=True)
    

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
if show_heatmap and not df.empty:
    df_kab = (
        df.groupby("Kabupaten")
        .agg({
            "Latitude": "mean",
            "Longitude": "mean",
            "Nama": "count"
        })
        .reset_index()
        .rename(columns={"Nama": "Jumlah_Bengkel"})
    )

    heat_data = [
        [row["Latitude"], row["Longitude"], row["Jumlah_Bengkel"]]
        for _, row in df_kab.iterrows()
    ]

    HeatMap(
        heat_data,
        radius=40,
        blur=25,
        max_zoom=10
    ).add_to(m)


# 2. MARKER PENGGUNA

folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Lokasi Anda Sekarang</b>",
    icon=folium.Icon(color='red', icon='user', prefix='fa')
).add_to(m)

# 3. MARKER BENGKEL 
if show_markers and not df.empty:
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
with st.expander("Lihat Statistik dan Analisis Data Spasial", expanded=False):
    st.markdown("Ringkasan Strategis")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric(label="Total Bengkel Terdata", value=len(df))
    with col_kpi2:
        jarak_min = df['Jarak_KM'].min()
        st.metric(label="Bengkel Terdekat", value=f"{jarak_min:.2f} KM")
    with col_kpi3:
        max_kab = df['Kabupaten'].value_counts().idxmax()
        st.metric(label="Pusat Kepadatan Bengkel", value=max_kab)

    st.divider()
    st.markdown("Analisis Kesenjangan Wilayah")
    col_kab1, col_kab2 = st.columns(2)
    
    with col_kab1:
        st.write("5 Wilayah Dengan Bengkel Terpadat")
        data_kab_top = df['Kabupaten'].value_counts().head(5)
        st.bar_chart(data_kab_top)
    
    with col_kab2:
        st.write("5 Wilayah dengan Potensi Pengembangan Tinggi")
        data_kab_bottom = df['Kabupaten'].value_counts().tail(5).sort_values(ascending=True)
        fig_gap, ax_gap = plt.subplots(figsize=(10, 6.5)) 
        bars = ax_gap.barh(data_kab_bottom.index, data_kab_bottom.values, color='orange')
        ax_gap.bar_label(bars, padding=3)
        ax_gap.set_xlabel("Jumlah Bengkel Resmi")
        ax_gap.set_title("Wilayah dengan Cakupan Layanan Terendah")
        st.pyplot(fig_gap)

    st.divider()

    #analsisi spasial
    st.markdown("Analisis Jangkauan & Aksesibilitas")
    col_dist1, col_dist2 = st.columns(2)

    with col_dist1:
        st.write("Kepadatan Jangkauan (Histogram)")
        fig_dist, ax_dist = plt.subplots()
        ax_dist.hist(df['Jarak_KM'], bins=20, color='skyblue', edgecolor='black')
        ax_dist.set_xlabel("Jarak (KM)")
        ax_dist.set_ylabel("Frekuensi")
        st.pyplot(fig_dist)
        
        st.write("Sebaran Outlier Jarak (Box Plot)")
        fig_box, ax_box = plt.subplots(figsize=(10, 3))
        ax_box.boxplot(df['Jarak_KM'], vert=False, patch_artist=True, 
                        boxprops=dict(facecolor='lightgreen'))
        ax_box.set_xlabel("Jarak (KM)")
        st.pyplot(fig_box)

    with col_dist2:
        st.write("Kurva Aksesibilitas Kumulatif")
        df_sorted = df.sort_values('Jarak_KM')
        df_sorted['Kumulatif_Bengkel'] = range(1, len(df_sorted) + 1)
        st.line_chart(df_sorted.set_index('Jarak_KM')['Kumulatif_Bengkel'])
        st.caption("Melihat seberapa cepat user mendapatkan akses ke banyak bengkel berdasarkan radius.")
        st.write("Data Bengkel Dalam Radius Dekat (< 10 KM)")
        bengkel_dekat = df[df['Jarak_KM'] <= 10][['Nama', 'Jarak_KM']].sort_values('Jarak_KM')
        st.dataframe(bengkel_dekat, use_container_width=True, height=300)