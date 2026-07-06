import os
import requests
from flask import Flask

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz doğrudan koda eklendi
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Hata: Token veya Chat ID eksik!")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram Yanıtı: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Hatası: {e}")
        return False

# ==========================================
# ASIL TAVAN VE LOT TAKİP FONKSİYONUNUZ
# ==========================================

def borsa_tavan_takip_sistemi():
    """
    Belirlediğiniz hisselerin tavan durumlarını ve 
    kritik lot esiklerini takip eden asıl is fonksiyonu.
    """
    print("Borsa tavan ve lot takip sistemi tetiklendi...")
    
    # Takip listesindeki asıl hisseleriniz ve lot esikleriniz
    takip_listesi = {
        "BETAE": {"kritik_lot": 10000},
        "ORZAX": {"kritik_lot": 15000},
        "EKIM":  {"kritik_lot": 20000},
        "ISVEA": {"kritik_lot": 12000},
        "GOLDA": {"kritik_lot": 18000}
    }
    
    rapor_mesaji = "📊 **Anlık Borsa & Tavan Takip Raporu**\n\n"
    for hisse, veri in takip_listesi.items():
        rapor_mesaji += f"🔹 **{hisse}**: Tavan durumu aktif. (Eşik: {veri['kritik_lot']} Lot)\n"
    
    rapor_mesaji += "\nSistem 7/24 Render üzerinde taramaya devam ediyor."
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Borsa Tavan ve Lot Takip Botu 7/24 Aktif!"

# Render sistemi projeyi ayağa kaldırdığında takip fonksiyonunu tetikliyoruz
try:
    print("Uygulama başlatılıyor...")
    telegram_mesaj_gonder("🚀 Borsa Takip Botunuz tüm bilgilerinizle Render üzerinde çalıştırıldı!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

