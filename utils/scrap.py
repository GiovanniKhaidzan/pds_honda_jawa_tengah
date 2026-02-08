from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(), options=options)

url = "https://www.astra-honda.com/dealer"
driver.get(url)

print("=== SCRAPER BENGKEL HONDA JATENG ===")
print("SILAHKAN FILTER PROVINSI & KOTA DI BROWSER.")
input("Jika daftar sudah muncul, tekan ENTER untuk mulai...")

list_bengkel = []
halaman_sekarang = 1
nama_terakhir = "" 

try:
    while True:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='dealer-box']"))
        )#get class html dengan nama dealer-box
        time.sleep(2)#jeda dua detik 
        dealers = driver.find_elements(By.CSS_SELECTOR, "div[class*='dealer-box']")#simpan ke variable
        
        nama_pertama_halaman_ini = dealers[0].find_element(By.TAG_NAME, "h4").text#gert nama dealer pertama untuk di jadikan validasi
        if nama_pertama_halaman_ini == nama_terakhir:#kalo deales pertama sama dengan nama terakhir berarti halaman tidak berpindah
            print(f"Peringatan: Halaman {halaman_sekarang} tidak berpindah. Mencoba klik Next lagi...")
        else:
            nama_terakhir = nama_pertama_halaman_ini
            print(f"\n[HALAMAN {halaman_sekarang}]")
            print(f"Menemukan {len(dealers)} data di halaman ini.")
            #fungsi get data perhalaman 
            for i, dealer in enumerate(dealers, 1):
                try:
                    nama = dealer.find_element(By.TAG_NAME, "h4").text
                    alamat = dealer.find_element(By.CSS_SELECTOR, "div[class*='box-address']").text
                    kota_kab = dealer.find_element(By.CSS_SELECTOR, "div[class*='box-city']").text
                    link_href = dealer.find_element(By.TAG_NAME, "a").get_attribute("href")#bawa alamat url di a

                    lat, lon = None, None#definisi variavle kosong
                    if "destination=" in link_href:#kalo di destination ada linke href nyamaka
                        coords = link_href.split("destination=")[1].split("&")[0]
                        #dia bvakal motong link nya sampe destination- [1] lalu
                        #dia akan motong lagi sampe & [0] untuk mendapatkan koordinatnya saja
                        if "," in coords:
                            lat, lon = coords.split(",")
                            #lalu di potong lagi koodina nya jadi dua lat dan lon berdasarkan ,

                    list_bengkel.append({
                        'Nama': nama,
                        'Alamat': alamat,
                        'Wilayah': kota_kab,
                        'Latitude': lat,
                        'Longitude': lon
                    })    
                    print(f"✔Data {i}: {nama}") 
                except:
                    continue
        #fungsi button next
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button.paginate-btn.next")#get beradasrkan kelas
            
            if "disabled" in next_btn.get_attribute("class") or next_btn.get_attribute("disabled"):
                print("\nSudah mencapai halaman terakhir.")#kalo si clas para byttton nya itu berubah jadi disable atau
                #si class nya jadi disable maka mencapai akhir
                break
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            #scroll otomatis sampai terlihat button next nya berenti tepat di tengah 
            #scrool view yuntuk scriooll 
            time.sleep(1)#delay
            driver.execute_script("arguments[0].click();", next_btn)#klik halaman selanjutnya
            
            halaman_sekarang += 1
            time.sleep(4)#delay
            
        except Exception as e:
            print(f"\nBerhenti: {e}")
            break

finally:#kalo terjadi kiamat data akan tetap di simpan di bagian terakhir data di input
    if list_bengkel:
        df = pd.DataFrame(list_bengkel).drop_duplicates()
        df.to_csv('bengkel_honda_jateng_coba.csv', index=False)
        print(f"\nSELESAI! Total {len(df)} data unik disimpan.")

    driver.quit()#clos selenium