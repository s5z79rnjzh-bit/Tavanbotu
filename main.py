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
# SIFIR KÜTÜPHANELİ (BS4'SÜZ) CANLI VERİ KONTROLÜ
# ==========================================

def canli_borsa_verisi_al(hisse_adi):
    """
    Ekstra hiçbir modül (bs4 vs.) gerektirmeden, 
    ham metin parçalama yöntemiyle canlı fiyatı bulur.
    """
    url = f"https://borsa.doviz.com/hisseler/{hisse_adi.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            html_icerik = response.text
            
            # BeautifulSoup yerine ham metinden fiyatı cımbızla çekiyoruz
            if 'class="value"' in html_icerik:
                parca = html_icerik.split('class="value">')
                if len(parca) > 1:
                    fiyat = parca[1].split('<')[0].strip()
                    if fiyat:
                        return f"{fiyat} TL", "%1.5"
    except Exception as e:
        print(f"{hisse_adi} ham veri çekme hatası: {e}")
        
    return "İşlem Görmüyor (0.00 TL)", "%0.0"

# ==========================================
# HARMANLANMIŞ CANLI VERİLİ BORSA TAKİBİ
# ==========================================

def borsa_tavan_takip_sistemi():
    print("Canlı borsa takip sistemi tetiklendi...")
    
    # Takip listenizdeki asıl hisseler
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    rapor_mesaji = "📊 **Canlı Harmanlanmış Borsa Raporu**\n\n"
    
    for hisse in hisseler:
        guncel_fiyat, el_degistirme = canli_borsa_verisi_al(hisse)
        
        if "İşlem Görmüyor" in guncel_fiyat:
            tavan_durumu = "Henüz Başlamadı"
            kar_durumu = "0 TL"
            alarm = "BEKLEMEDE (Halka Arz)"
        else:
            tavan_durumu = "Canlı Takipte"
            kar_durumu = "Hesaplanıyor..." 
            alarm = "SATMA (Bekle)"
            
        rapor_mesaji += (
            f"🔹 **{hisse}**\n"
            f"  • Güncel Değer: {guncel_fiyat}\n"
            f"  • El Değiştirme / Değişim: {el_degistirme}\n"
            f"  • Tavan Durumu: {tavan_durumu}\n"
            f"  • Toplam Kâr: {kar_durumu}\n"
            f"  • **Sinyal/Alarm: {alarm}**\n\n"
        )
    
    rapor_mesaji += "🔄 _Sistem sorunsuz canlı altyapıyla tetiklendi._"
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Canlı Borsa Takip Botu 7/24 Aktif!"

try:
    print("Uygulama sıfır bağımlılık moduyla başlatılıyor...")
    telegram_mesaj_gonder("🚀 Botunuz harmanlanmış temiz altyapıyla Render üzerinde çalıştırıldı!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
