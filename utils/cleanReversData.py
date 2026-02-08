import pandas as pd

file_path = "data/bengkel_honda_jateng.csv"
try:
    df = pd.read_csv(file_path)
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='latin1')

print("--- Memulai Proses Pembersihan Data ---")

if 'Wilayah' in df.columns:#cek apakah kolom wilayah ada atau tidak
    print("Sedang membersihkan teks pada kolom Wilayah...")
    df['Wilayah'] = df['Wilayah'].str.lstrip(',').str.replace(', Jawa Tengah', '', case=False).str.strip()
    #lstrip untuk menghapus koma di awal, replace untuk menghapus ', Jawa Tengah' dan strip untuk menghapus spasi di awal dan akhir
else:
    print("Peringatan: Kolom 'Wilayah' tidak ditemukan!")

def bersihkan_koordinat(row):
    lat = row['Latitude']
    lon = row['Longitude']
    
    if pd.isna(lat) or pd.isna(lon):
        return pd.Series([lat, lon])

    if abs(lat) > 90:#kalo nilai mutlak lat lebih besar dari 90 maka kemungkinan terbalik maka di balioakn
        actual_lat = lon
        actual_lon = lat
    else:
        actual_lat = lat
        actual_lon = lon
        
    return pd.Series([actual_lat, actual_lon])#untuk membersihkan koordinat yang terbalik dengan memeriksa nilai mutlak latitude, jika lebih besar dari 90 maka dianggap terbalik dan ditukar

print("Sedang memperbaiki koordinat yang terbalik secara otomatis...")
df[['Latitude', 'Longitude']] = df.apply(lambda row: bersihkan_koordinat(row), axis=1)
#menerapkan fungsi bersih untuk ke steiap baris di dataset

output_file = "bengkel_honda_jateng_bersih_final.csv"
df.to_csv(output_file, index=False)

print("-" * 50)
print(f"Selesai! File bersih disimpan sebagai: {output_file}")
print(f"Total data diproses: {len(df)}")