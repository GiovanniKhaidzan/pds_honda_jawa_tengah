import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap 
from streamlit_js_eval import get_geolocation
import numpy as np
import matplotlib.pyplot as plt
import time
loc = get_geolocation() 

st.set_page_config(
    page_title="GIS Bengkel Honda Jateng",
    layout="wide",
    initial_sidebar_state="expanded"
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 #Radius bumi dalam kilometer
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])#konversi derajat ke radian untuk perhitungan trigonometri
    dlat = lat2 - lat1#selisih latitud antara dua titik
    dlon = lon2 - lon1#selisih longitud antara dua titik
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2#rumus haversine untuk menghitung jarak antara dua titik di permukaan bumi berdasarkan koordinat latitud dan longitud
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))   #menghitung sudut sentral antara dua titik berdasarkan nilai a yang dihitung sebelumnya
    distance = R * c#menghitung jarak sebenarnya antara dua titik dengan mengalikan sudut sentral (c) dengan radius bumi (R) untuk mendapatkan hasil dalam kilometer
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
    DEFAULT_LAT = -6.99049680
    DEFAULT_LON = 110.42294450

    if 'user_lat' not in st.session_state:#kalo user_lat tidak ada di session state maka di set ke default
        st.session_state.user_lat = DEFAULT_LAT
    if 'user_lon' not in st.session_state:
        st.session_state.user_lon = DEFAULT_LON

    if st.button("Gunakan Lokasi GPS Saya", use_container_width=True):#kalo tombol di klik maka akan mencoba mengambil lokasi gps
        time.sleep#delay
        
        with st.status("Sedang mengambil koordinat GPS", expanded=False) as status:#status untuk menampilkan status saat mengambil koordinat gps
            if loc and isinstance(loc, dict) and 'coords' in loc:# apakah loc ada isinya dan ada acoord di dalam nya
                #jadi kalo masuk bowrser lalu klik bagfian si lokasi gpos saya nanti ada allow lokasi
                #nah itu kalo kita klik allow browser akan memberikan 
                # data format nya json lalu di simoab di loc
                st.session_state.user_lat = loc['coords']['latitude']
                st.session_state.user_lon = loc['coords']['longitude']
                status.update(label="Lokasi berhasil diperbarui!", state="complete", expanded=False)
                st.success("Koordinat diperbarui!")
                st.rerun()
            else:
                status.update(label="Gagal mengambil lokasi!", state="error", expanded=True)
                st.error("""
                    **Akses Ditolak/Gagal.** 1. Pastikan 'Location' di Windows Settings sudah **ON**.
                    2. Berikan izin (Allow) saat browser meminta akses lokasi.
                    3. Klik tombol lagi setelah memberikan izin.
                """)

    user_lat = st.number_input("Latitude", 
                               value=st.session_state.user_lat, 
                               format="%.8f")
    user_lon = st.number_input("Longitude", 
                               value=st.session_state.user_lon, 
                               format="%.8f")
    
    if user_lat != st.session_state.user_lat or user_lon != st.session_state.user_lon:#kalo user_lat atau user_lon berubah maka di update ke session state
        st.session_state.user_lat = user_lat
        st.session_state.user_lon = user_lon

    st.divider()
    st.info("Koordinat di atas digunakan sebagai titik pusat pencarian bengkel terdekat.")
    show_heatmap = st.checkbox("Tampilkan Heatmap", value=True)
    show_markers = st.checkbox("Tampilkan Marker Bengkel", value=True)
    


# Logic hitung lokasi terdekat
if not df.empty:
    df['Jarak_KM'] = df.apply(
        lambda row: haversine(user_lat, user_lon, row['Latitude'], row['Longitude']), #menghitung jarak antara lokasi pengguna dengan setiap 
        #bengkel menggunakan fungsi haversine yang sudah didefinisikan sebelumnya, hasilnya disimpan di kolom baru 'Jarak_KM'
        axis=1#menerapkan fungsi ke setiap baris di dataset
    )
    df_terdekat = df.sort_values('Jarak_KM').head(3)#cari 3 bengkel terdekat dengan mengurutkan berdasarkan kolom 'Jarak_KM' dan mengambil 3 baris teratas

# Main Layout
st.subheader("Peta Persebaran")
m = folium.Map(location=[user_lat, user_lon], zoom_start=9)#

# 1. HEATMAP 
if show_heatmap and not df.empty:
    df_kab = (
        df.groupby("Wilayah")
        .agg({
            "Latitude": "mean",#menghitung rata-rata latitude untuk setiap wilayah
            "Longitude": "mean",#menghitung rata-rata longitude untuk setiap wilayah
            "Nama": "count"#menghitung jumlah bengkel di setiap wilayah 
        })
        .reset_index()
        .rename(columns={"Nama": "Jumlah_Bengkel"})
    )

    heat_data = [
        [row["Latitude"], row["Longitude"], row["Jumlah_Bengkel"]]
        for _, row in df_kab.iterrows()#membuat list heat_data yang berisi koordinat latitude, longitude, dan jumlah bengkel untuk setiap wilayah dengan iterasi melalui setiap baris di df_kab menggunakan iterrows()
    ]
#ddd
    HeatMap(
        heat_data,
        radius=40,#kalo radius semakin besar maka area panas akan semakin luas, tapi detail titik panas akan berkurang
        blur=25,
        max_zoom=10
    ).add_to(m)


# 2. MARKER PENGGUNA

folium.Marker(
    location=[user_lat, user_lon],
    popup="<b>Lokasi Anda Sekarang</b>",
    icon=folium.Icon(color='red', icon='user', prefix='fa'),
    z_index_offset=1000
).add_to(m)

# 3. MARKER BENGKEL 
if show_markers and not df.empty:
    for i, row in df.iterrows():
        if pd.isna(row['Latitude']) or abs(row['Latitude']) > 90:#kalo latitude kosong atau nilai
            #latitude lebih besar dari 90 maka data dianggap tidak valid dan di skip
            continue
            
        warna = 'green' if row['Nama'] in df_terdekat['Nama'].values else 'blue'
        #kalo nama bengkel ada di daftar bengkel terdekat maka warna marker nya hijau, kalo tidak maka warna marker nya biru
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{
            #bagian userlat lot lokasi user kalo rrow latitude longtiutde bagian bengkel
            user_lon}&destination={row['Latitude']},{row['Longitude']}&travelmode=driving"
            #gimana ya ini tu jadi kaya kita rancang href kita sendiri pake lat lot yang uda di tentuin
            #jadi nanti kalo kita klik petunjuk arah dia akan bawa kita ke google maps dengan tujuan koordinat bengkel yang di klik dan asalnya koordinat pengguna
            #travelmode=driving untuk menentukan mode perjalanan sebagai openegmudi nmotot

        popup_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 12px; width: 200px; color: canvastext; 
            background-color: canvas;">
            <b style="font-size:14px; color:#e74c3c;">{row['Nama']}</b><br>
            <b>Alamat:</b> {row['Alamat']}<br>
            <b>Wilayah:</b> {row['Wilayah']}<br>
            <hr style="margin:5px 0; border: 0; border-top: 1px solid #ccc;">
            <b>Jarak:</b> {row['Jarak_KM']:.2f} KM<br><br>
            
            <a href="{google_maps_url}" target="_blank" 
            style="display: block; text-align: center; 
                    background-color: #2980b9; color: white; 
                    padding: 8px; border-radius: 5px; 
                    text-decoration: none; font-weight: bold;">
                Petunjuk Arah (Maps)
            </a>
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
    cols = st.columns(3)#buat 3 kolom sejajar kesamping
    for idx, (i, row) in enumerate(df_terdekat.iterrows()):#ambil dari satu satu dari 3 bengkel terdekat
        with cols[idx]:#index 0 1 2
            st.markdown(f"""
                <div style="
                    background-color: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 10px; 
                    min-height: 250px;
                    margin-bottom: 10px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                ">
                    <h4 style="color: #3BB143; margin-top: 0;">{row['Nama']}</h4>
                    <p style="font-size: 13px; color: #555; height: 50px; overflow: hidden;">
                        {row['Alamat']}
                    </p>
                    <p style="margin-bottom: 5px;">Jarak: <b>{row['Jarak_KM']:.2f} KM</b></p>
                    <small style="color: #888;">{row['Wilayah']}</small>
                </div>
            """, unsafe_allow_html=True)
            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={row['Latitude']},{row['Longitude']}&travelmode=driving"
            st.link_button("Buka Google Maps", google_maps_url, use_container_width=True)


st.divider()
with st.expander("Lihat Statistik dan Analisis Data Spasial", expanded=False):
    st.markdown("Ringkasan Strategis")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric(label="Total Bengkel Terdata", value=len(df))
        #menampilkan total jumlah bengkel yang terdata di dataset dengan menggunakan st.metric untuk menampilkan angka tersebut dengan label "Total Bengkel Terdata"
    with col_kpi2:
        jarak_min = df['Jarak_KM'].min()
        st.metric(label="Bengkel Terdekat", value=f"{jarak_min:.2f} KM")
        #menampilkan jarak terdekat dari lokasi pengguna ke bengkel terdekat dengan mengambil nilai minimum dari kolom 'Jarak_KM' dan menampilkannya dengan label "Bengkel Terdekat"
    with col_kpi3:
        max_kab = df['Wilayah'].value_counts().idxmax()
        st.metric(label="Pusat Kepadatan Bengkel", value=max_kab)
        #menampilkan wilayah dengan jumlah bengkel terbanyak dengan menggunakan value_counts untuk menghitung jumlah bengkel di setiap wilayah dan idxmax untuk mendapatkan nama wilayah dengan jumlah terbanyak, lalu menampilkannya dengan label "Pusat Kepadatan Bengkel"

    st.divider()
    st.markdown("Analisis Kesenjangan Wilayah")
    col_kab1, col_kab2 = st.columns(2)#buat dua kolom sejajar untuk menampilkan analisis kesenjangan wilayah
    
    with col_kab1:
        st.write("5 Wilayah Dengan Bengkel Terpadat")
        data_kab_top = df['Wilayah'].value_counts().head(5)#menghitung jumlah bengkel di setiap wilayah dengan value_counts lalu mengambil 5 wilayah teratas dengan head(5)
        st.bar_chart(data_kab_top)
    
    with col_kab2:
        st.write("5 Wilayah dengan Potensi Pengembangan Tinggi")
        data_kab_bottom = df['Wilayah'].value_counts().tail(5).sort_values(ascending=True)#menghitung jumlah bengkel di setiap wilayah dengan value_counts lalu mengambil 5 wilayah terbawah dengan tail(5) dan mengurutkannya secara ascending untuk menampilkan wilayah dengan jumlah bengkel paling sedikit di atas
        fig_gap, ax_gap = plt.subplots(figsize=(10, 6.5)) #buat figure dan axis untuk menampilkan grafik gap wilayah dengan ukuran yang lebih besar agar lebih jelas
        bars = ax_gap.barh(data_kab_bottom.index, data_kab_bottom.values, color='orange')
        ax_gap.bar_label(bars, padding=3)
        ax_gap.set_xlabel("Jumlah Bengkel Resmi")
        ax_gap.set_title("Wilayah dengan Cakupan Layanan Terendah")
        st.pyplot(fig_gap)

    st.divider()

    #analsisi spasial
    st.markdown("Analisis Jangkauan & Aksesibilitas")
    col_dist1, col_dist2 = st.columns(2)#buat dua kolom sejajar untuk menampilkan analisis jangkauan dan aksesibilitas

    with col_dist1:
        st.write("Kepadatan Jangkauan (Histogram)")
        fig_dist, ax_dist = plt.subplots()
        ax_dist.hist(df['Jarak_KM'], bins=20, color='skyblue', edgecolor='black')#membuat histogram untuk menampilkan distribusi jarak bengkel dengan menggunakan kolom 'Jarak_KM' dengan 20 bin, warna biru muda, dan garis tepi hitam untuk membedakan setiap bar
        ax_dist.set_xlabel("Jarak (KM)")
        ax_dist.set_ylabel("Frekuensi")
        st.pyplot(fig_dist)
        
        st.write("Sebaran Outlier Jarak (Box Plot)")
        fig_box, ax_box = plt.subplots(figsize=(10, 3))
        ax_box.boxplot(df['Jarak_KM'], vert=False, patch_artist=True, 
                        boxprops=dict(facecolor='lightgreen'))#membuat box plot untuk menampilkan sebaran jarak bengkel dengan menggunakan kolom 'Jarak_KM', orientasi horizontal, warna hijau muda untuk kotak, dan menampilkan garis median di dalam kotak
        ax_box.set_xlabel("Jarak (KM)")
        st.pyplot(fig_box)

    with col_dist2:
        st.write("Kurva Aksesibilitas Kumulatif")
        df_sorted = df.sort_values('Jarak_KM')
        df_sorted['Kumulatif_Bengkel'] = range(1, len(df_sorted) + 1)#membuat kolom baru 'Kumulatif_Bengkel' yang berisi angka urut dari 1 hingga jumlah total bengkel untuk menunjukkan jumlah kumulatif bengkel yang dapat diakses dalam jarak tertentu
        st.line_chart(df_sorted.set_index('Jarak_KM')['Kumulatif_Bengkel'])#membuat grafik garis untuk menampilkan kurva aksesibilitas kumulatif dengan menggunakan kolom 'Jarak_KM' sebagai sumbu x dan 'Kumulatif_Bengkel' sebagai sumbu y, sehingga dapat melihat bagaimana jumlah bengkel yang dapat diakses meningkat seiring bertambahnya jarak
        st.write("Data Bengkel Dalam Radius Dekat (< 10 KM)")
        bengkel_dekat = df[df['Jarak_KM'] <= 10][['Nama', 'Jarak_KM']].sort_values('Jarak_KM')#membuat dataframe baru 'bengkel_dekat
        if not bengkel_dekat.empty:
            st.dataframe(bengkel_dekat, use_container_width=True, height=200)
        else:
            st.warning(f"Tidak ada bengkel ditemukan dalam radius 10 KM dari lokasi ({user_lat:.4f}, {user_lon:.4f}).")
            st.info("Coba pindahkan lokasi atau gunakan GPS jika tersedia.")