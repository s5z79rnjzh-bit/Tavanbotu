import time
import requests
from threading import Thread
from flask import Flask

# --- BULUT SİSTEMLERİ İÇİN WEB SUNUCU AYARI ---
app = Flask('')

@app.route('/')
def home():
    return "Bot internette 7/24 aktif olarak çalışıyor!"

def run_web_server():
    # Render veya Koyeb'in botu açık tutması için bir web portu açıyoruz
    app.run(host='0.0.0.0', port=8080)

# ==================== SİZİN AYARLARINIZ ====================
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

IZLENECEK_HISSELER = {
    "BETAE": {"esik_lot": 250000, "aktif": True},
    "ORZAX": {"esik_lot": 150000, "aktif": True},
    "EKIM":  {"esik_lot": 100000, "aktif": True},
    "ISVEA": {"esik_lot": 80000,  "aktif": True},
    "GOLDA": {"esik_lot": 80000,  "aktif": True}
}
KONTROL_PERIYODU = 5 
# ===========================================================

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except:
        return False

def canli_derinlik_verisi_al(hisse_kodu):
    import random
    return random.randint(70000, 400000) # Test Simülasyonu

def bot_ana_dongu():
    print("📈 Tavan takip döngüsü başlatıldı...")
    telegram_mesaj_gonder("🚀 *Tavan Takip Botu Online Sistemde Aktif!*")
    
    while True:
        hisse_kalan_aktif = False
        for hisse, ayar in IZLENECEK_HISSELER.items():
            if not ayar["aktif"]:
                continue
                
            hisse_kalan_aktif = True
            tavan_lot = canli_derinlik_verisi_al(hisse)
            
            if tavan_lot < ayar["esik_lot"]:
                uyari_mesaji = (
                    f"⚠️ *TAVAN BOZMA TEHLİKESİ!*\n\n"
                    f"*Hisse:* #{hisse}\n"
                    f"*Lot:* {tavan_lot:,}\n"
                    f"ℹ️ Tavandaki alıcı eriyor!"
                )
                if telegram_mesaj_gonder(uyari_mesaji):
                    ayar["aktif"] = False
        
        if not hisse_kalan_aktif:
            telegram_mesaj_gonder("🛑 Tüm hisselerin takibi bitti.")
            break
            
        time.sleep(KONTROL_PERIYODU)

# --- BOTU VE WEB SUNUCUSUNU AYNI ANDA ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Web sunucusunu arka planda başlat
    server_thread = Thread(target=run_web_server)
    server_thread.start()
    
    # Ana borsa takip döngüsünü başlat
    bot_ana_dongu()

