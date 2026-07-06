import os
import requests
from flask import Flask

app = Flask(__name__)

# Çevre değişkenlerinden bilgileri alıyoruz
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Hata: Token veya Chat ID bulunamadı!")
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
# ASIL BORSA VE PORTFÖY ANALİZİ FONKSİYONLARINIZ
# ==========================================

def borsa_verilerini_isle():
    """
    Hisse senedi verilerini çeken, halka arzları takip eden 
    ve portföy analizini yapan asıl fonksiyonunuz.
    """
    print("Borsa verileri ve portföy analizi tetiklendi...")
    
    # Buraya asıl borsa analiz mantığınız, taramalarınız ve 
    # Telegram'a göndermek istediğiniz bildirim içerikleri gelecek.
    
    analiz_sonucu = "📊 **Hisse Senedi & Portföy Analizi Raporu**\n\nSisteminiz aktif, veriler güncel!"
    telegram_mesaj_gonder(analiz_sonucu)

# ==========================================

@app.route('/')
def home():
    return "Borsa Portföy Takip Botu 7/24 Aktif!"

# Render/Gunicorn projeyi ayağa kaldırdığında analiz fonksiyonunu tetikliyoruz
try:
    print("Uygulama başlatılıyor...")
    telegram_mesaj_gonder("🚀 Borsa Takip Botunuz Render üzerinde başarıyla başlatıldı!")
    borsa_verilerini_isle()  # Asıl işi yapan borsa kodunuz burada çalışıyor
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


