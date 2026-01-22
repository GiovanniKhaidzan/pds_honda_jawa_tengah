import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

file_path = "data/bengkel_honda_jateng_bersih.csv"

df = pd.read_csv(file_path)

geolocator = Nominatim(user_agent="my_request_honda_app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

total_data = len(df)
counter = 0

def get_kabupaten(lat, lon, nama_bengkel):
    global counter
    counter += 1
    try:
        print(f"[{counter}/{total_data}] Mencari wilayah untuk: {nama_bengkel}...", end="\r")
        
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        if location:
            address = location.raw.get('address', {})
            kabupaten = address.get('city') or address.get('town') or address.get('county') or address.get('city_district')
            print(f"[{counter}/{total_data}] Selesai: {nama_bengkel} -> {kabupaten}          ")
            return kabupaten
        
        print(f"[{counter}/{total_data}] Gagal: {nama_bengkel} (Lokasi tidak ditemukan)")
        return "Tidak Ditemukan"
    except Exception as e:
        print(f"[{counter}/{total_data}] Error pada {nama_bengkel}: {e}")
        return None

print(f"Memulai pengolahan {total_data} data...")
print("-" * 50)

df['Kabupaten'] = df.apply(lambda row: get_kabupaten(row['Latitude'], row['Longitude'], row['Nama']), axis=1)

print("-" * 50)
output_file = 'bengkel_honda_jateng_final.csv'
df.to_csv(output_file, index=False)
print(f"Selesai! Semua data telah diproses dan disimpan ke: {output_file}")