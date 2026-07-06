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
# GÜNCEL KESİN MYNET VERİ KAZIMA ALGORİTMASI
# ==========================================

def canli_borsa_verisi_al(hisse_adi):
    """
    Mynet Finans üzerindeki doğru HTML etiketlerini tarayarak
    hisselerin gerçek fiyat ve yüzde değişimini çeker.
    """
    # Link düzeltildi: finans.mynet.com
    url = f"https://finans.mynet.com/borsa/hisseler/{hisse_adi.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            html = response.text
            
            fiyat = "Bulunamadı"
            degisim = "%0.0"
            
            # Mynet'in güncel fiyatı barındırdığı sınıfları tarıyoruz
            if 'class="fn-fiyat' in html:
                parca_fiyat = html.split('class="fn-fiyat')
                if len(parca_fiyat) > 1:
                    # Etiketin içindeki saf rakamı temizle
                    fiyat = parca_fiyat[1].split('>')[1].split('<')[0].strip()
            elif 'id="seans_fiyat"' in html:
                parca_fiyat = html.split('id="seans_fiyat">')
                if len(parca_fiyat) > 1:
                    fiyat = parca_fiyat[1].split('<')[0].strip()
                    
            # Yüzde değişimi yakalıyoruz
            if 'class="fn-oran' in html:
                parca_degisim = html.split('class="fn-oran')
                if len(parca_degisim) > 1:
                    degisim = parca_degisim[1].split('>')[1].split('<')[0].strip()
            elif 'id="seans_degisim"' in html:
                parca_degisim = html.split('id="seans_degisim">')
                if len(parca_degisim) > 1:
                    degisim = parca_degisim[1].split('<')[0].strip()
            
            if fiyat != "Bulunamadı" and fiyat != "" and fiyat != "0" and fiyat != "0,00":
                return f"{fiyat} TL", degisim
                
    except Exception as e:
        print(f"{hisse_adi} Güncel Mynet hatası: {e}")
        
    return "İşlem Görmüyor (0.00 TL)", "%0.0"

# ==========================================
# HARMANLANMIŞ CANLI VERİLİ BORSA TAKİBİ
# ==========================================

def borsa_tavan_takip_sistemi():
    print("Mynet kesin veri sistemi tetiklendi...")
    
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    rapor_mesaji = "📊 **Canlı Harmanlanmış Borsa Raporu (Mynet Güncel)**\n\n"
    
    for hisse in hisseler:
        guncel_fiyat, degisim = canli_borsa_verisi_al(hisse)
        
        if "İşlem Görmüyor" in guncel_fiyat:
            tavan_durumu = "Henüz Başlamadı"
            kar_durumu = "0 TL"
            alarm = "BEKLEMEDE (Halka Arz)"
        else:
            tavan_durumu = "Canlı Takipte (Tavan Serisi)"
            # İleride buraya tam elinizdeki lot sayısı/maliyet girilince kârı otomatik basacak
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
    
    rapor_mesaji += "🔄 _Sistem güncellenmiş Mynet hatları üzerinden tetiklendi._"
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Mynet Güncel Borsa Botu Aktif!"

try:
    print("Uygulama düzeltilmiş linklerle başlatılıyor...")
    telegram_mesaj_gonder("🚀 Bot linkleri ve tarama etiketleri güncellendi!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
