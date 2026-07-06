import os
import requests
from bs4 import BeautifulSoup
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
# CANLI TÜRK BORSASI VERİ ÇEKME FONKSİYONU
# ==========================================

def canli_borsa_verisi_al(hisse_adi):
    """
    Açık kaynak yöntemlerle (Web Kazıma) Türk borsasından 
    hissenin gerçek anlık verilerini çekmeye çalışır.
    """
    # Örnek olarak döviz.com veya bigpara tarzı açık kaynak sitelerden kazıma simülasyonu/altyapısı
    url = f"https://borsa.doviz.com/hisseler/{hisse_adi.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sitedeki fiyat ve değişim alanlarını buluyoruz (Site yapısına göre parse edilir)
            # Eğer hisse henüz işleme başlamadıysa buralar boş dönecektir
            fiyat_element = soup.find("div", {"class": "value"})
            degisim_element = soup.find("div", {"class": "change"})
            
            fiyat = fiyat_element.text.strip() + " TL" if fiyat_element else "İşlem Görmüyor (0.00 TL)"
            degisim = degisim_element.text.strip() if degisim_element else "%0.0"
            
            return fiyat, degisim
    except Exception as e:
        print(f"{hisse_adi} verisi çekilirken hata oluştu: {e}")
        
    return "İşlem Görmüyor (0.00 TL)", "%0.0"

# ==========================================
# HARMANLANMIŞ CANLI VERİLİ BORSA TAKİBİ
# ==========================================

def borsa_tavan_takip_sistemi():
    print("Canlı borsa ve tavan takip sistemi tetiklendi...")
    
    # Takip listenizdeki asıl hisseler
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    
    rapor_mesaji = "📊 **Canlı Harmanlanmış Borsa Raporu**\n\n"
    
    for hisse in hisserler:
        # İnternetten açık kaynak yöntemle canlı veriyi sorguluyoruz
        guncel_fiyat, el_degistirme = canli_borsa_verisi_al(hisse)
        
        # Eğer fiyat sıfır veya işlem görmüyor gelirse henüz işleme başlamamıştır
        if "İşlem Görmüyor" in guncel_fiyat:
            tavan_durumu = "Henüz Başlamadı"
            kar_durumu = "0 TL"
            alarm = "BEKLEMEDE (Halka Arz)"
        else:
            # İşlem görüyorsa gerçek duruma göre hesaplama (Burayı portföyünüze göre özelleştirebiliriz)
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
    
    rapor_mesaji += "🔄 _Sistem canlı veri hatlarını kullanarak tetiklendi._"
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Canlı Borsa Takip Botu 7/24 Aktif!"

try:
    print("Uygulama canlı veri entegrasyonuyla başlatılıyor...")
    telegram_mesaj_gonder("🚀 Botunuz canlı borsa altyapısıyla Render üzerinde çalıştırıldı!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
