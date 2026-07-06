import os
import requests
import time
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

# image_3.png görselindeki birebir lot adetleriniz ve halka arz fiyatları
PORTFOY_VERILERI = {
    "EKIM":  {"arz_fiyati": 30.26, "lot": 200, "toplam_lot_sayisi": 50000000},  # Örnek şirket toplam lotu (El değiştirme için)
    "ORZAX": {"arz_fiyati": 69.00, "lot": 30,  "toplam_lot_sayisi": 25000000},
    "BETAE": {"arz_fiyati": 40.00, "lot": 28,  "toplam_lot_sayisi": 30000000},
    "ISVEA": {"arz_fiyati": 20.90, "lot": 40,  "toplam_lot_sayisi": 18000000},
    "GOLDA": {"arz_fiyati": 9.20,  "lot": 88,  "toplam_lot_sayisi": 40000000}
}

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=3)
        return True
    except:
        return False

def canli_borsa_detayli_veri_al(hisse_adi):
    """Yahoo Finance üzerinden anlık fiyat ve günlük işlem hacmini çeker."""
    ticker = f"{hisse_adi.upper()}.IS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            fiyat = meta.get("regularMarketPrice")
            
            # Günlük işlem gören lot hacmini çekiyoruz (El değiştirme hesabı için)
            indicators = data.get("chart", {}).get("result", [{}])[0].get("indicators", {})
            quote = indicators.get("quote", [{}])[0]
            hacim_listesi = quote.get("volume", [])
            # En son geçerli hacim verisini ayıkla
            gunluk_hacim = next((v for v in reversed(hacim_listesi) if v is not None), 0)
            
            if fiyat and fiyat > 0:
                return fiyat, gunluk_hacim
    except:
        pass
    return None, 0

def borsa_raporu_olustur_ve_gonder():
    print("Detaylı portföy raporu tetiklendi...")
    hisseler = ["EKIM", "ORZAX", "BETAE", "ISVEA", "GOLDA"]
    
    rapor_mesaji = "📊 **Canlı Detaylı Portföy ve Tavan Raporu**\n\n"
    
    toplam_maliyet_genel = 0.0
    toplam_deger_genel = 0.0
    toplam_kar_genel = 0.0
    
    for hisse in hisseler:
        arz_fiyati = PORTFOY_VERILERI[hisse]["arz_fiyati"]
        benim_lotum = PORTFOY_VERILERI[hisse]["lot"]
        toplam_sirket_lotu = PORTFOY_VERILERI[hisse]["toplam_lot_sayisi"]
        
        api_fiyati, gunluk_hacim = canli_borsa_detayli_veri_al(hisse)
        
        # Eğer API'den anlık fiyat dönmezse portföy görselindeki son fiyata sadık kal
        guncel_fiyat = api_fiyati if api_fiyati else arz_fiyati
        
        # Hisse bazlı kâr ve değer hesaplamaları
        hisse_maliyet = arz_fiyati * benim_lotum
        hisse_guncel_deger = guncel_fiyat * benim_lotum
        hisse_net_kar = hisse_guncel_deger - hisse_maliyet
        hisse_degisim_yuzdesi = ((guncel_fiyat - arz_fiyati) / arz_fiyati) * 100
        
        # Genel toplamlar için biriktir
        toplam_maliyet_genel += hisse_maliyet
        toplam_deger_genel += hisse_guncel_deger
        toplam_kar_genel += hisse_net_kar
        
        # Tavan Sayısı Bulma
        tavan_sayisi = 0
        gecici_fiyat = arz_fiyati
        while gecici_fiyat * 1.095 < guncel_fiyat:
            gecici_fiyat *= 1.10
            tavan_sayisi += 1
            if tavan_sayisi > 20: break
            
        tavan_durumu = f"{tavan_sayisi}. Tavan" if tavan_sayisi > 0 else "İşlem Bekliyor / Arz Fiyatında"
        if not api_fiyati: tavan_durumu += " (Kapanış)"
        
        # El Değiştirme Oranı Hesaplama: (Günlük İşlem Hacmi / Toplam Halka Arz Lot Sayısı) * 100
        if gunluk_hacim > 0 and toplam_sirket_lotu > 0:
            el_degistirme_orani = (gunluk_hacim / toplam_sirket_lotu) * 100
            el_degistirme_metni = f"%{el_degistirme_orani:.2f}"
        else:
            el_degistirme_metni = "%0.00"
            
        kar_isareti = "+" if hisse_net_kar >= 0 else ""
        
        if tavan_sayisi >= 7 or (gunluk_hacim > 0 and el_degistirme_orani > 10): 
            alarm = "SAT (Kritik Marj)"
        elif tavan_sayisi >= 5 or (gunluk_hacim > 0 and el_degistirme_orani > 5): 
            alarm = "DİKKAT (İzleme Modu)"
        else: 
            alarm = "SATMA (Bekle)"
            
        rapor_mesaji += (
            f"🔹 **{hisse}**\n"
            f"  • Benim Lotum: {benim_lotum} Adet (Arz: {arz_fiyati:.2f} TL)\n"
            f"  • Güncel Lot Değeri: {guncel_fiyat:.2f} TL ({kar_isareti}%{hisse_degisim_yuzdesi:.2f})\n"
            f"  • Hissedeki Toplam Param: {hisse_guncel_deger:.2f} TL\n"
            f"  • Hissedeki Net Kârım: {kar_isareti}{hisse_net_kar:.2f} TL\n"
            f"  • Tavan Durumu: {tavan_durumu}\n"
            f"  • El Değiştirme Oranı: {el_degistirme_metni}\n"
            f"  • **Sinyal/Alarm: {alarm}**\n\n"
        )
        
    # EN ALT GENEL PORTFÖY ÖZET TABLOSU
    kar_isareti_genel = "+" if toplam_kar_genel >= 0 else ""
    toplam_büyüme_yuzdesi = (toplam_kar_genel / toplam_maliyet_genel) * 100 if toplam_maliyet_genel > 0 else 0.0
    
    rapor_mesaji += (
        f"🏁 —————— **PORTFÖY ÖZETİ** ——————\n"
        f"💰 **Toplam Yatırılan Ana Para:** {toplam_maliyet_genel:.2f} TL\n"
        f"📈 **Portföyün Güncel Toplam Değeri:** {toplam_deger_genel:.2f} TL\n"
        f"💵 **Net Toplam Kâr Durumu:** {kar_isareti_genel}{toplam_kar_genel:.2f} TL ({kar_isareti_genel}%{toplam_büyüme_yuzdesi:.2f})\n"
        f"—————————————————————\n"
        f"🔄 _Veriler 10 dakikalık periyotlarla güncellenmektedir._"
    )
    
    telegram_mesaj_gonder(rapor_mesaji)

def arka_plan_dongusu():
    # Render'ın projeyi Live moduna güvenle geçirmesi için 15 saniye duraksama
    time.sleep(15)
    borsa_raporu_olustur_ve_gonder()
    
    while True:
        time.sleep(600)
        borsa_raporu_olustur_ve_gonder()

# ==========================================

@app.route('/')
def home():
    return "Gelişmiş Canlı Portföy Takip Sistemi Aktif!"

t = Thread(target=arka_plan_dongusu)
t.daemon = True
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

