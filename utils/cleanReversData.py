import pandas as pd

# 1. Load Data
file_path = "data/bengkel_honda_jateng.csv"
try:
    df = pd.read_csv(file_path)
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='latin1')

print("--- Memulai Proses Pembersihan Data ---")

if 'Wilayah' in df.columns:
    print("Sedang membersihkan teks pada kolom Wilayah...")
    # lstrip(',') menghapus koma di awal, replace menghapus teks provinsi, strip menghapus spasi
    df['Wilayah'] = df['Wilayah'].str.lstrip(',').str.replace(', Jawa Tengah', '', case=False).str.strip()
else:
    print("Peringatan: Kolom 'Wilayah' tidak ditemukan!")

# 3. Fungsi Perbaikan Koordinat (Menukar Lat/Lon jika terbalik)
def bersihkan_koordinat(row):
    lat = row['Latitude']
    lon = row['Longitude']
    
    # Jika data kosong, biarkan saja
    if pd.isna(lat) or pd.isna(lon):
        return pd.Series([lat, lon])

    # Logika: Latitude di Indonesia (khususnya Jateng) harusnya di kisaran -6 s/d -8
    # Jika angkanya > 90 (misal 110), berarti itu sebenarnya Longitude yang tertukar
    if abs(lat) > 90:
        actual_lat = lon
        actual_lon = lat
    else:
        actual_lat = lat
        actual_lon = lon
        
    return pd.Series([actual_lat, actual_lon])

print("Sedang memperbaiki koordinat yang terbalik secara otomatis...")
df[['Latitude', 'Longitude']] = df.apply(lambda row: bersihkan_koordinat(row), axis=1)

# 4. Simpan ke File Baru
output_file = "bengkel_honda_jateng_bersih_final2.csv"
df.to_csv(output_file, index=False)

print("-" * 50)
print(f"Selesai! File bersih disimpan sebagai: {output_file}")
print(f"Total data diproses: {len(df)}")