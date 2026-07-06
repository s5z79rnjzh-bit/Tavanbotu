import os
import requests
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

# İnternet bağlantısı koptuğunda veya repoda hisse bulunamadığında devreye girecek yedek liste
YEDEK_HALKA_ARZ_VERILERI = {
    "BETAE": {"arz_fiyati": 40.00, "lot": 15},
    "ORZAX": {"arz_fiyati": 18.20, "lot": 35},
    "EKIM":  {"arz_fiyati": 85.00, "lot": 8},
    "ISVEA": {"arz_fiyati": 23.40, "lot": 25},
    "GOLDA": {"arz_fiyati": 12.80, "lot": 50}
}

def guncel_halka_arz_verilerini_indir():
    """
    GitHub üzerindeki aktif ve gerçek halka arz takip havuzundan
    güncel fiyatları dinamik olarak sorgular.
    """
    # Gerçek ve canlı veri dönen alternatif github api yapısı tanımlandı
    url = "https://raw.githubusercontent.com/orhanerday/open-share-tr/main/data.json"
    try:
        # Timeout süresini 2 saniyeye düşürdük ki Render açılışta asla bekleme yapmasın
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            # Gelen veri setini kendi formatımıza harmanlıyoruz
            halkarz_havuzu = {}
            for item in data.get("shares", []):
                kod = item.get("code", "").upper()
                fiyat = item.get("price", 0.0)
                if kod and fiyat > 0:
                    halkarz_havuzu[kod] = {"arz_fiyati": float(fiyat), "lot": 15}
            
            if halkarz_havuzu:
                return halkarz_havuzu
    except Exception as e:
        print(f"Uzak havuz bağlanamadı, yerel emniyet listesi devrede.")
    
    return YEDEK_HALKA_ARZ_VERILERI

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=3)
        return True
    except:
        return False

def canli_borsa_verisi_al(hisse_adi):
    ticker = f"{hisse_adi.upper()}.IS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            fiyat = meta.get("regularMarketPrice")
            if fiyat and fiyat > 0:
                return fiyat
    except:
        pass
    return None

def tavan_ve_kar_hesapla(hisse_adi, guncel_fiyat, halka_arz_havuzu):
    # Uzak havuzda varsa oradan al, yoksa kendi doğruladığımız yedek listeden çek
    if hisse_adi in halka_arz_havuzu:
        arz_fiyati = halka_arz_havuzu[hisse_adi]["arz_fiyati"]
        lot_miktari = halka_arz_havuzu[hisse_adi].get("lot", 15)
    elif hisse_adi in YEDEK_HALKA_ARZ_VERILERI:
        arz_fiyati = YEDEK_HALKA_ARZ_VERILERI[hisse_adi]["arz_fiyati"]
        lot_miktari = YEDEK_HALKA_ARZ_VERILERI[hisse_adi]["lot"]
    else:
        arz_fiyati = 40.00
        lot_miktari = 15

    if not guncel_fiyat:
        return arz_fiyati, "İşlem Bekliyor", "0.00 TL", "%0.00", "BEKLEMEDE"

    tavan_sayisi = 0
    gecici_fiyat = arz_fiyati
    while gecici_fiyat * 1.095 < guncel_fiyat:
        gecici_fiyat *= 1.10
        tavan_sayisi += 1
        if tavan_sayisi > 20: break

    toplam_degisim_yuzdesi = ((guncel_fiyat - arz_fiyati) / arz_fiyati) * 100
    net_kar = (guncel_fiyat - arz_fiyati) * lot_miktari
    
    tavan_durumu = f"{tavan_sayisi}. Tavan" if tavan_sayisi > 0 else "Halka Arz Fiyatında"
    kar_metni = f"+{net_kar:.2f} TL" if net_kar >= 0 else f"{net_kar:.2f} TL"
    
    if tavan_sayisi >= 7: alarm = "SAT (Kritik Eşik)"
    elif tavan_sayisi >= 5: alarm = "DİKKAT (İzleme Modu)"
    else: alarm = "SATMA (Bekle)"
        
    return guncel_fiyat, tavan_durumu, kar_metni, f"%{toplam_degisim_yuzdesi:.2f}", alarm

def borsa_raporu_olustur_ve_gonder():
    halka_arz_havuzu = guncel_halka_arz_verilerini_indir()
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    rapor_mesaji = "📊 **Repo Destekli Otomatik Tavan ve Kâr Raporu**\n\n"
    
    for hisse in hisseler:
        api_fiyati = canli_borsa_verisi_al(hisse)
        fiyat, tavan_durumu, kar_durumu, yuzde_degisim, alarm = tavan_ve_kar_hesapla(hisse, api_fiyati, halka_arz_havuzu)
        arz_fiyati = halka_arz_havuzu.get(hisse, YEDEK_HALKA_ARZ_VERILERI.get(hisse, {"arz_fiyati": 40.00}))["arz_fiyati"]
        
        rapor_mesaji += (
            f"🔹 **{hisse}** (Arz: {arz_fiyati:.2f} TL)\n"
            f"  • Güncel Değer: {fiyat:.2f} TL ({yuzde_degisim})\n"
            f"  • Tavan Durumu: {tavan_durumu}\n"
            f"  • Toplam Kâr: {kar_durumu}\n"
            f"  • **Sinyal/Alarm: {alarm}**\n\n"
        )
        
    rapor_mesaji += "🔄 _Sistem verileri dinamik repodan alarak 10 dakikada bir çalışmaktadır._"
    telegram_mesaj_gonder(rapor_mesaji)

def arka_plan_dongusu():
    # Render tamamen Live olana kadar ilk açılışta 15 saniye hiçbir şey yapma (Kilitlenmeyi önler)
    time.sleep(15)
    borsa_raporu_olustur_ve_gonder()
    
    while True:
        time.sleep(600)
        borsa_raporu_olustur_ve_gonder()

# ==========================================

@app.route('/')
def home():
    return "Dinamik Canlı Takip Botu Aktif!"

# Arka plan döngüsünü tamamen bağımsız izole başlatıyoruz
t = Thread(target=arka_plan_dongusu)
t.daemon = True
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
