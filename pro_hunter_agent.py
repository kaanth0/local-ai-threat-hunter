import time
import threading
import hashlib
import os
import winsound
import requests
import ollama

# --- BURAYA SADECE VIRUSTOTAL API KEY'İNİ YAPIŞTIR ---
VT_API_KEY = "BURAYA_VIRUSTOTAL_API_KEY_YAZIN"

MODEL_ADI = "huihui_ai/qwen3.5-abliterated:9b"
LOG_DOSYASI = "sample_access.log"

mesajlar = [
    {
        "role": "system",
        "content": (
            "Sen 7/24 nöbet tutan kıdemli bir Threat Hunter ve SOAR yapay zekâ ajanısın. "
            "Loglara yeni satır düştüğünde analiz et. Şüpheli bir IP görürsen mutlaka 'virustotal_ip_sorgula' aracını kullan. "
            "Kritik bir tehdit doğrulanırsa 'acil_alarm_ver' aracını kullanarak operatörü uyar ve raporu kaydet. "
            "Operatör sana komut verirse elindeki araçlarla uygula."
        )
    }
]
kilit = threading.Lock()

# --- ARAÇ 1: GERÇEK VIRUSTOTAL IP SORGUSU ---
def virustotal_ip_sorgula(ip_adresi: str) -> str:
    """Verilen IP adresini VirusTotal üzerinde 70'ten fazla güvenlik motorunda canlı tarar."""
    print(f"\n[ARAÇ - VT] -> '{ip_adresi}' VirusTotal veritabanında taranıyor...", flush=True)
    url = "https://virustotal.com" + "/api/v3/ip_addresses/" + ip_adresi
    headers = {"x-apikey": VT_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            veri = r.json()["data"]["attributes"]
            stats = veri["last_analysis_stats"]
            ulke = veri.get("country", "Bilinmiyor")
            sahip = veri.get("as_owner", "Bilinmiyor")
            return (
                f"VirusTotal Sonucu ({ip_adresi}): Ülke={ulke}, Sağlayıcı={sahip} | "
                f"Zararlı (Malicious) Motor Sayısı: {stats['malicious']}, "
                f"Şüpheli (Suspicious): {stats['suspicious']}, Temiz: {stats['harmless']}"
            )
        return f"VirusTotal sorgu hatası (Kod: {r.status_code})"
    except Exception as e:
        return f"Bağlantı hatası: {str(e)}"

# --- ARAÇ 2: DOSYA HASH ÇIKARMA VE VIRUSTOTAL'DE TARAMA ---
def dosya_hash_tara(dosya_yolu: str) -> str:
    """Bilgisayardaki şüpheli bir dosyanın SHA256 parmak izini çıkarır ve VirusTotal'de tarar."""
    print(f"\n[ARAÇ - HASH] -> '{dosya_yolu}' SHA256 hesaplanıyor ve VT'ye soruluyor...", flush=True)
    if not os.path.exists(dosya_yolu):
        return f"Hata: '{dosya_yolu}' dosyası bulunamadı."
    
    sha256 = hashlib.sha256()
    with open(dosya_yolu, "rb") as f:
        for parca in iter(lambda: f.read(4096), b""):
            sha256.update(parca)
    dosya_hash = sha256.hexdigest()
    url = "https://virustotal.com" + "/api/v3/files/" + dosya_hash
    headers = {"x-apikey": VT_API_KEY}
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        stats = r.json()["data"]["attributes"]["last_analysis_stats"]
        return f"Dosya SHA256: {dosya_hash} | Zararlı Tespit Eden Antivirüs: {stats['malicious']}"
    elif r.status_code == 404:
        return f"Dosya SHA256: {dosya_hash} | VirusTotal veritabanında daha önce görülmemiş (Yeni/Özel dosya)."
    return f"VT Dosya Sorgu Hatası: {r.status_code}"

# --- ARAÇ 3: SESLİ WINDOWS ALARMI VE RAPOR KAYDI ---
def acil_alarm_ver(rapor_metni: str) -> str:
    """Kritik tehdit tespit edildiğinde sesli alarm çalar ve raporu ALARM_RAPORU.txt dosyasına yazar."""
    print("\n[ARAÇ - ALARM] -> 🚨 SESLİ ALARM TETİKLENİYOR VE RAPOR KAYDEDİLİYOR!", flush=True)
    for _ in range(3):
        winsound.Beep(1000, 300)
    with open("ALARM_RAPORU.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- YENİ ALARM ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n{rapor_metni}\n")
    return "Sesli alarm çalındı ve rapor ALARM_RAPORU.txt dosyasına kaydedildi."

# --- ARAÇ 4: IP ENGELLEME ---
def ip_engelle(ip_adresi: str, sebep: str) -> str:
    """Zararlı IP adresini engellenenler listesine ekler."""
    print(f"\n[ARAÇ - FIREWALL] -> '{ip_adresi}' engelleniyor...", flush=True)
    with open("blocked_ips.txt", "a", encoding="utf-8") as f:
        f.write(f"{ip_adresi} | Sebep: {sebep}\n")
    return f"{ip_adresi} kara listeye eklendi."

araclar = {
    "virustotal_ip_sorgula": virustotal_ip_sorgula,
    "dosya_hash_tara": dosya_hash_tara,
    "acil_alarm_ver": acil_alarm_ver,
    "ip_engelle": ip_engelle
}

def beyne_gonder(yeni_mesaj: str, etiket: str = "AJAN"):
    with kilit:
        mesajlar.append({"role": "user", "content": yeni_mesaj})
        while True:
            cevap = ollama.chat(
                model=MODEL_ADI,
                messages=mesajlar,
                tools=[virustotal_ip_sorgula, dosya_hash_tara, acil_alarm_ver, ip_engelle],
                think=False
            )
            mesaj = cevap["message"]
            mesajlar.append(mesaj)

            if mesaj.get("tool_calls"):
                for tool in mesaj["tool_calls"]:
                    fonk_adi = tool["function"]["name"]
                    args = tool["function"]["arguments"]
                    sonuc = araclar[fonk_adi](**args)
                    mesajlar.append({"role": "tool", "content": str(sonuc)})
            else:
                print(f"\n[{etiket}]:\n{mesaj['content']}\n", flush=True)
                print("Sen > ", end="", flush=True)
                break

def nobetci_dongusu():
    with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
        son_satir = len(f.readlines())

    print(f"[NÖBETÇİ AKTİF] '{LOG_DOSYASI}' izleniyor... (VirusTotal Canlı Bağlı)", flush=True)

    while True:
        time.sleep(3)
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
            satirlar = f.readlines()

        if len(satirlar) > son_satir:
            yeni_loglar = "".join(satirlar[son_satir:])
            son_satir = len(satirlar)
            print("\n\n[!] YENİ LOG DÜŞTÜ! Otonom inceleme başlıyor...", flush=True)
            beyne_gonder(
                f"Log dosyasına şu yeni satırlar eklendi:\n{yeni_loglar}\n"
                "Tehdit varsa IP'yi VirusTotal'de tara ve kritikse 'acil_alarm_ver' aracını çalıştır!",
                etiket="🚨 CANLI ALARM"
            )

if __name__ == "__main__":
    t = threading.Thread(target=nobetci_dongusu, daemon=True)
    t.start()

    print("="*60)
    print("PRO THREAT HUNTER AJANI (VIRUSTOTAL CANLI ENTEGRE)")
    print("Örnek komut: 'sample_access.log dosyasının hash değerini tara'")
    print("="*60)

    while True:
        girdi = input("Sen > ")
        if girdi.strip().lower() == "cikis":
            break
        if girdi.strip():
            beyne_gonder(girdi, etiket="🤖 ASİSTAN")
