import os
import requests
from flask import Flask

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Hatası: {e}")
        return False

# ==========================================
# RESMİ YAHOO FINANCE API VERİ BAĞLANTISI
# ==========================================

def canli_borsa_verisi_al(hisse_adi):
    """
    Kütüphanesiz, doğrudan Yahoo Finance API üzerinden 
    BIST hisselerinin anlık fiyatını ve değişimini çeker.
    """
    # Borsa İstanbul için hisse sonuna .IS ekliyoruz
    ticker = f"{hisse_adi.upper()}.IS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    # Engellenmemek için standart tarayıcı başlığı (Header) ekliyoruz
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # API'den gelen verinin içindeki fiyatı ve dünkü kapanışı ayıklıyoruz
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            fiyat = meta.get("regularMarketPrice")
            onceki_kapanis = meta.get("previousClose")
            
            if fiyat and onceki_kapanis:
                # Günlük yüzde değişimi hesapla
                yuzde_degisim = ((fiyat - onceki_kapanis) / onceki_kapanis) * 100
                return f"{fiyat:.2f} TL", f"%{yuzde_degisim:.2f}"
                
    except Exception as e:
        print(f"{hisse_adi} Yahoo API hatası: {e}")
        
    return "İşlem Görmüyor (0.00 TL)", "%0.0"

# ==========================================
# HARMANLANMIŞ GERÇEK VERİLİ BORSA TAKİBİ
# ==========================================

def borsa_tavan_takip_sistemi():
    print("Yahoo API canlı borsa takip sistemi tetiklendi...")
    
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    rapor_mesaji = "📊 **Canlı Harmanlanmış Resmi Borsa Raporu**\n\n"
    
    for hisse in hisseler:
        guncel_fiyat, degisim = canli_borsa_verisi_al(hisse)
        
        if "İşlem Görmüyor" in guncel_fiyat:
            tavan_durumu = "Henüz Başlamadı"
            kar_durumu = "0 TL"
            alarm = "BEKLEMEDE (Halka Arz)"
        else:
            tavan_durumu = "Canlı Takipte (Tahta Açık)"
            kar_durumu = "Hesaplanıyor..." 
            alarm = "SATMA (Bekle)"
            
        rapor_mesaji += (
            f"🔹 **{hisse}**\n"
            f"  • Güncel Değer: {guncel_fiyat}\n"
            f"  • Günlük Değişim: {degisim}\n"
            f"  • Tavan Durumu: {tavan_durumu}\n"
            f"  • Toplam Kâr: {kar_durumu}\n"
            f"  • **Sinyal/Alarm: {alarm}**\n\n"
        )
    
    rapor_mesaji += "🔄 _Sistem resmi Yahoo Finance API hatları üzerinden tetiklendi._"
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Yahoo API Canlı Borsa Botu Aktif!"

try:
    print("Uygulama Yahoo API moduyla başlatılıyor...")
    telegram_mesaj_gonder("🚀 Bot altyapısı resmi Yahoo Finance API sistemine bağlandı!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
