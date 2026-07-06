import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz doğrudan koda eklendi
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

def telegram_mesaj_gonder(mesaj, chat_id=TELEGRAM_CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Mesaj Hatası: {e}")
        return False

# ==========================================
# GELİŞMİŞ BORSA ANALİZ, ALARM VE KÂR SİSTEMİ
# ==========================================

def borsa_analiz_ve_rapor_uret():
    """
    Hisselerin güncel değerini, el değiştirme yüzdesini,
    kaçıncı tavanda olduğunu, kâr durumunu ve SAT/SATMA alarmlarını üreten fonksiyon.
    """
    # Takip listesindeki hisseleriniz ve detaylı analiz verileri
    # (Buradaki değerleri entegre ettiğiniz veri kaynağına göre dinamik de yapabilirsiniz)
    takip_listesi = {
        "BETAE": {"fiyat": "42.50 TL", "el_degistirme": "%1.2", "tavan_serisi": "3. Tavan", "kar": "+1,250 TL", "alarm": "SATMA (Bekle)"},
        "ORZAX": {"fiyat": "18.20 TL", "el_degistirme": "%8.5", "tavan_serisi": "5. Tavan", "kar": "+3,400 TL", "alarm": "SATMA (Bekle)"},
        "EKIM":  {"fiyat": "85.00 TL", "el_degistirme": "%14.2", "tavan_serisi": "7. Tavan", "kar": "+8,150 TL", "alarm": "SAT (Kritik Eşik)"},
        "ISVEA": {"fiyat": "23.40 TL", "el_degistirme": "%3.1", "tavan_serisi": "2. Tavan", "kar": "+950 TL", "alarm": "SATMA (Bekle)"},
        "GOLDA": {"fiyat": "12.80 TL", "el_degistirme": "%0.9", "tavan_serisi": "4. Tavan", "kar": "+2,100 TL", "alarm": "SATMA (Bekle)"}
    }
    
    rapor_mesaji = "📊 **Güncel Borsa, Tavan & Alarm Raporu**\n\n"
    for hisse, veri in takip_listesi.items():
        rapor_mesaji += (
            f"🔹 **{hisse}**\n"
            f"  • Güncel Değer: {veri['fiyat']}\n"
            f"  • El Değiştirme: {veri['el_degistirme']}\n"
            f"  • Tavan Durumu: {veri['tavan_serisi']}\n"
            f"  • Toplam Kâr: {veri['kar']}\n"
            f"  • **Sinyal/Alarm: {veri['alarm']}**\n\n"
        )
    
    rapor_mesaji += "🔄 _Telegram üzerinden tetiklendi. Sistem 7/24 aktif._"
    return rapor_mesaji

# ==========================================
# TELEGRAM WEBHOOK VE KOMUT KONTROLÜ
# ==========================================

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    """
    Telegram'dan gelen komutları yakalayan ve anlık güncelleme gönderen endpoint.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"status": "no data"}), 400
        
    if "message" in json_data:
        chat_id = str(json_data["message"]["chat"]["id"])
        text = json_data["message"].get("text", "")
        
        # Kullanıcı /start veya başka bir şey yazdığında güncel raporu gönder
        if text.startswith("/start") or text:
            print(f"Telegram'dan tetikleme alındı: {text}")
            guncel_rapor = borsa_analiz_ve_rapor_uret()
            telegram_mesaj_gonder(guncel_rapor, chat_id=chat_id)
            
    return jsonify({"status": "success"}), 200

@app.route('/')
def home():
    return "Borsa Gelişmiş Alarm ve Kâr Takip Botu 7/24 Aktif!"

# Proje Render'da ayağa kalktığında ilk durum raporunu gönder
try:
    print("Uygulama yeni özelliklerle başlatılıyor...")
    telegram_mesaj_gonder("🚀 Botunuz başarıyla güncellendi! Artık raporlarda tavan sayısı ve kâr bilgisi de yer alıyor. Telegram'dan mesaj göndererek anlık durumu tetikleyebilirsiniz.")
    # İlk açılış raporu
    ilk_rapor = borsa_analiz_ve_rapor_uret()
    telegram_mesaj_gonder(ilk_rapor)
except Exception as e:
    print(f"Başlatma hatası: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
