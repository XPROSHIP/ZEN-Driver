# 🚀 ZEN Driver — Cloud Transfer Engine

ZEN Driver, tek kullanımlık/geçici indirme bağlantılarını (Google User Content, CDN token URL'leri vb.) doğrudan **Google Drive** hesabınıza yüksek hızda aktaran hafif ve modern bir bulut transfer uygulamasıdır.

## 🛠️ Teknolojiler
- **Backend:** FastAPI (Python 3.10+), Requests, Uvicorn
- **Frontend:** HTML5, TailwindCSS, JavaScript (Fetch API)
- **Deployment:** Render.com (Backend API) & GitHub Pages (Frontend)

## 📁 Proje Yapısı
```
ZEN-Driver/
├── main.py             # FastAPI backend (Stream upload & status tracking)
├── requirements.txt    # Python bağımlılıkları
├── index.html          # Frontend web arayüzü
└── README.md           # Dokümantasyon
```

## ⚙️ Yerel Geliştirme (Local Setup)

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/KULLANICI_ADI/ZEN-Driver.git
   cd ZEN-Driver
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. Sunucuyu başlatın:
   ```bash
   uvicorn main:app --reload
   ```

4. `index.html` dosyasını tarayıcınızda açarak kullanmaya başlayın.
