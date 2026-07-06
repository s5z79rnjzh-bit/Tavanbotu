import os
import requests
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

# Hisselerin resmi halka arz fiyatları ve hesaba düşen tahmini lot miktarları
HALKA_ARZ_VERILERI = {
    "BETAE": {"arz_fiyati": 42.50, "lot": 15, "tavan_serisi": 4},
    "ORZAX": {"arz_fiyati": 18.20, "lot": 35, "tavan_serisi": 0},
    "EKIM":  {"arz_fiyati": 85.00, "lot": 8, "tavan_serisi": 0},
    "ISVEA": {"arz_fiyati": 23.40, "lot": 25, "tavan_serisi": 0},
    "GOLDA": {"arz_fiyati": 12.80, "lot": 50, "tavan_serisi": 0}
}

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Hatası: {e}")
        return False

def canli_borsa_verisi_al(hisse_adi):
    ticker = f"{hisse_adi.upper()}.IS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            fiyat = meta.get("regularMarketPrice")
            if fiyat and fiyat > 0:
                return fiyat
    except Exception as e:
        print(f"{hisse_adi} fiyat çekme hatası: {e}")
    return None

def tavan_ve_kar_hesapla(hisse_adi, guncel_fiyat):
    arz_fiyati = HALKA_ARZ_VERILERI[hisse_adi]["arz_fiyati"]
    lot_miktari = HALKA_ARZ_VERILERI[hisse_adi]["lot"]
    
    if not guncel_fiyat:
        tavan_sayisi = HALKA_ARZ_VERILERI[hisse_adi]["tavan_serisi"]
        guncel_fiyat = arz_fiyati * (1.10 ** tavan_sayisi)
        not_canli = " (Tahmini)"
    else:
        not_canli = ""
        tavan_sayisi = 0
        gecici_fiyat = arz_fiyati
        while gecici_fiyat * 1.095 < guncel_fiyat:
            gecici_fiyat *= 1.10
            tavan_sayisi += 1
            if tavan_sayisi > 20: break

    toplam_degisim_yuzdesi = ((guncel_fiyat - arz_fiyati) / arz_fiyati) * 100
    net_kar = (guncel_fiyat - arz_fiyati) * lot_miktari
    
    if tavan_sayisi > 0:
        tavan_durumu = f"{tavan_sayisi}. Tavan{not_canli}"
    else:
        tavan_durumu = "Halka Arz Fiyatında" if not_canli == "" else "İşlem Bekliyor"
        
    kar_metni = f"+{net_kar:.2f} TL" if net_kar >= 0 else f"{net_kar:.2f} TL"
    
    if tavan_sayisi >= 7: alarm = "SAT (Kritik Eşik)"
    elif tavan_sayisi >= 5: alarm = "DİKKAT (İzleme Modu)"
    else: alarm = "SATMA (Bekle)"
        
    return guncel_fiyat, tavan_durumu, kar_metni, f"%{toplam_degisim_yuzdesi:.2f}", alarm

def borsa_tavan_takip_sistemi():
    """Her 10 dakikada bir çalışacak ana döngü"""
    while True:
        print("Otomatik borsa raporu hazırlanıyor...")
        hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
        rapor_mesaji = "📊 **10 Dk'lık Canlı Tavan ve Kâr Raporu**\n\n"
        
        for hisse in hisseler:
            api_fiyati = canli_borsa_verisi_al(hisse)
            fiyat, tavan_durumu, kar_durumu, yuzde_degisim, alarm = tavan_ve_kar_hesapla(hisse, api_fiyati)
            arz_fiyati = HALKA_ARZ_VERILERI[hisse]["arz_fiyati"]
            
            rapor_mesaji += (
                f"🔹 **{hisse}** (Arz: {arz_fiyati:.2f} TL)\n"
                f"  • Güncel Değer: {fiyat:.2f} TL ({yuzde_degisim})\n"
                f"  • Tavan Durumu: {tavan_durumu}\n"
                f"  • Toplam Kâr: {kar_durumu}\n"
                f"  • **Sinyal/Alarm: {alarm}**\n\n"
            )
            
        rapor_mesaji += "🔄 _Sistem 10 dakikalık periyotlarla otomatik çalışmaktadır._"
        
        # Beklemeden anında gönderiyoruz
        telegram_mesaj_gonder(rapor_mesaji)
        
        # Mesajı attıktan sonra 10 dakika uykuya geç
        time.sleep(600)

# ==========================================

@app.route('/')
def home():
    return "7/24 Otomatik Zaman Ayarlı Borsa Botu Aktif!"

# Arka plan döngüsünü Flask başlatılmadan hemen önce tetikliyoruz
otomatik_task = Thread(target=borsa_tavan_takip_sistemi)
otomatik_task.daemon = True
otomatik_task.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
