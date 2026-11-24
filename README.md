# 🛡️ Local AI Threat Hunter & SOAR Agent (v1.0)

`Python 3.10+` • `Local LLM (Ollama)` • `VirusTotal API v3` • `Blue Team / SOAR` • `Status: Active`

**Veri gizliliğini (Data Privacy) koruyarak tamamen yerel (offline) çalışan, 7/24 sunucu loglarını izleyen ve gerçek zamanlı tehdit istihbaratı ile otonom müdahale kararları üreten yapay zekâ destekli Blue Team / SOAR ajanı.**

---

## 🎯 Neden Bu Projeyi Geliştirdim?
Kurumsal siber güvenlik operasyonlarında (SOC) gizli sunucu loglarını veya şüpheli dosyaları bulut tabanlı yapay zekâ API'lerine göndermek veri sızıntısı riski taşır. Bu proje, açık ağırlıklı (open-weight) yerel bir dil modelini (**Ollama + Qwen 3.5**) otonom araç çağırma (**Tool-Calling**) mimarisiyle birleştirerek dışarıya veri sızdırmadan tehdit avcılığı (Threat Hunting) yapılmasını sağlar.

## ⚙️ Mimari ve Yetenekler
* **🧠 Yerel LLM Beyni:** `Ollama` üzerinde çalışan açık ağırlıklı model ile sıfır veri sızıntısı.
* **👁️ 7/24 Canlı Log İzleme (Daemon Thread):** Sunucu loglarına düşen yeni satırları anlık yakalar (SQL Injection, Web Shell, Path Traversal vb.).
* **🔍 Canlı Tehdit İstihbaratı (VirusTotal API v3):** Tespit edilen şüpheli IP adreslerini 70+ güvenlik motorunda anlık sorgular.
* **🧬 Gizlilik Odaklı Dosya Hash Tarama:** Dosyaların kendisini yüklemeden yerel olarak **SHA256** parmak izini çıkarır ve VirusTotal veritabanında tarar.
* **🚨 Human-in-the-Loop (İnsan Onaylı Müdahale):** Kritik tehditlerde sesli alarm ve rapor üretir; yanlış pozitif (False Positive) riskine karşı engelleme işlemi için operatör onayı bekler.

## 🚀 Kurulum ve Çalıştırma

1. **Yerel modeli indirin:**
   ```bash
   ollama run huihui_ai/qwen3.5-abliterated:9b
   ```
2. **Gerekli Python kütüphanelerini kurun:**
   ```bash
   pip install ollama requests
   ```
3. **API Anahtarını Ekleyin ve Başlatın:**
   `pro_hunter_agent.py` içerisindeki `VT_API_KEY` alanına ücretsiz VirusTotal API anahtarınızı girin ve çalıştırın:
   ```bash
   python pro_hunter_agent.py
   ```

## 🗺️ Geliştirme Yol Haritası (Roadmap)
- [x] **v1.0:** Yerel LLM entegrasyonu, 7/24 log dinleme, VirusTotal IP & SHA256 Hash tarama, sesli alarm ve karantina listesi.
- [ ] **v1.1:** Dahili (Internal / Private) IP filtreleme (`192.168.x.x`, `10.x.x.x` yoksayma) ve geliştirilmiş raporlama.
- [ ] **v1.2:** Windows Güvenlik Olay Günlükleri (Event Logs) entegrasyonu (hatalı oturum açma / Brute-Force tespiti).
- [ ] **v1.3:** Telegram Bot entegrasyonu ile uzaktan canlı bildirim ve komut yönetimi.
- [ ] **v1.4:** MITRE ATT&CK teknik etiketleme ve gerçek Windows Güvenlik Duvarı (Firewall) kuralı ekleme.

