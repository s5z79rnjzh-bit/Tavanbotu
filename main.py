import os
import requests
from flask import Flask

app = Flask(__name__)

# Telegram Bot ve Chat ID bilgileriniz
TELEGRAM_TOKEN = "8607261709:AAFVLk2WjZibbGUBqq3B_JjVjZkB5SrkdKI"
TELEGRAM_CHAT_ID = "1336984102"

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Hatası: {e}")
        return False

# ==========================================
# HALKA ARZ VERİLERİ VE HESAPLAMA MOTORU
# ==========================================

# Hisselerin resmi halka arz fiyatları ve hesaba düşen tahmini lot miktarları
HALKA_ARZ_VERILERI = {
    "BETAE": {"arz_fiyati": 42.50, "lot": 15},  # Örnek: 42.50 TL'den arz oldu, 15 lot verdi
    "ORZAX": {"arz_fiyati": 18.20, "lot": 35},
    "EKIM":  {"arz_fiyati": 85.00, "lot": 8},
    "ISVEA": {"arz_fiyati": 23.40, "lot": 25},
    "GOLDA": {"arz_fiyati": 12.80, "lot": 50}
}

def canli_borsa_verisi_al(hisse_adi):
    """Yahoo Finance üzerinden anlık fiyatı çeker."""
    ticker = f"{hisse_adi.upper()}.IS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            fiyat = meta.get("regularMarketPrice")
            if fiyat:
                return fiyat
    except Exception as e:
        print(f"{hisse_adi} fiyat çekme hatası: {e}")
    return None

def tavan_ve_kar_hesapla(hisse_adi, guncel_fiyat):
    """Halka arz fiyatına göre kaçıncı tavanda olduğunu ve kârı hesaplar."""
    if hisse_adi not in HALKA_ARZ_VERILERI or not guncel_fiyat:
        return "Hesaplanamadı", "0.00 TL", "%0.0", "BEKLEMEDE"
    
    arz_fiyati = HALKA_ARZ_VERILERI[hisse_adi]["arz_fiyati"]
    lot_miktari = HALKA_ARZ_VERILERI[hisse_adi]["lot"]
    
    # Halka arz fiyatından bugüne toplam yüzde yükseliş
    toplam_degisim_yuzdesi = ((guncel_fiyat - arz_fiyati) / arz_fiyati) * 100
    
    # Borsada tavan serisi yaklaşık %10 (her gün katlanarak) gittiği için tavan sayısı bulma:
    # Formül: arz_fiyati * (1.10 ^ tavan_sayisi) = guncel_fiyat
    tavan_sayisi = 0
    gecici_fiyat = arz_fiyati
    while gecici_fiyat * 1.095 < guncel_fiyat:  # %9.5 ve üzeri marjları tavan kabul etmesi için emniyet payı
        gecici_fiyat *= 1.10
        tavan_sayisi += 1
        if tavan_sayisi > 20:  # Sonsuz döngü koruması
            break
            
    # Net Kâr Hesaplama: (Güncel Fiyat - Arz Fiyatı) * Lot Sayısı
    toplam_maliyet = arz_fiyati * lot_miktari
    guncel_deger = guncel_fiyat * lot_miktari
    net_kar = guncel_deger - toplam_maliyet
    
    tavan_durumu = f"{tavan_sayisi}. Tavan" if tavan_sayisi > 0 else "Halka Arz Fiyatında"
    kar_metni = f"+{net_kar:.2f} TL" if net_kar >= 0 else f"{net_kar:.2f} TL"
    yuzde_metni = f"%{toplam_degisim_yuzdesi:.2f}"
    
    # El değiştirme oranları simülasyonu ve Alarm üretimi
    if tavan_sayisi >= 7:
        alarm = "SAT (Kritik Eşik)"
    elif tavan_sayisi >= 5:
        alarm = "DİKKAT (Yakından İzle)"
    else:
        alarm = "SATMA (Bekle)"
        
    return tavan_durumu, kar_metni, yuzde_metni, alarm

# ==========================================
# HARMANLANMIŞ OTOMATİK HESAPLAMALI RAPOR
# ==========================================

def borsa_tavan_takip_sistemi():
    print("Zeki borsa hesaplama motoru tetiklendi...")
    
    hisseler = ["BETAE", "ORZAX", "EKIM", "ISVEA", "GOLDA"]
    rapor_mesaji = "📊 **Canlı Tavan ve Kâr Hesaplama Raporu**\n\n"
    
    for hisse in hisseler:
        guncel_fiyat = canli_borsa_verisi_al(hisse)
        
        if not guncel_fiyat or guncel_fiyat <= 0:
            rapor_mesaji += (
                f"🔹 **{hisse}**\n"
                f"  • Güncel Değer: İşlem Görmüyor\n"
                f"  • Tavan Durumu: Henüz Başlamadı\n"
                f"  • Toplam Kâr: 0.00 TL\n"
                f"  • **Sinyal/Alarm: BEKLEMEDE (Halka Arz)**\n\n"
            )
        else:
            tavan_durumu, kar_durumu, yuzde_degisim, alarm = tavan_ve_kar_hesapla(hisse, guncel_fiyat)
            arz_fiyati = HALKA_ARZ_VERILERI[hisse]["arz_fiyati"]
            
            rapor_mesaji += (
                f"🔹 **{hisse}** (Halka Arz: {arz_fiyati:.2f} TL)\n"
                f"  • Güncel Değer: {guncel_fiyat:.2f} TL ({yuzde_degisim})\n"
                f"  • Tavan Durumu: {tavan_durumu}\n"
                f"  • Toplam Kâr: {kar_durumu}\n"
                f"  • **Sinyal/Alarm: {alarm}**\n\n"
            )
            
    rapor_mesaji += "🔄 _Sistem halka arz fiyatı bazlı matematik motoruyla çalıştı._"
    telegram_mesaj_gonder(rapor_mesaji)

# ==========================================

@app.route('/')
def home():
    return "Halka Arz Hesaplama Botu Aktif!"

try:
    print("Uygulama otomatik hesaplama moduyla başlatılıyor...")
    telegram_mesaj_gonder("🚀 Botunuza halka arz fiyatı bazlı tavan/kâr hesaplama motoru eklendi!")
    borsa_tavan_takip_sistemi()
except Exception as e:
    print(f"Başlatma esnasında hata: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

