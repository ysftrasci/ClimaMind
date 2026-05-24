# ClimaMind

Python ve Tkinter ile yazılmış masaüstü hava durumu uygulaması. Şehir bazlı anlık hava verisi, e-posta hatırlatıcıları, Joyuci sohbet asistanı ve doğa sesleri tek pencerede toplanıyor. Klasik bir hava durumu uygulamasından ziyade kullanım süresini arttırmak için ekstra özellikler içerir. İlk geniş kapsamlı proje denemem.

## Ne yapar?

- **Search Weather** — OpenWeatherMap üzerinden şehir arama ve hava durumu sonuç ekranı
- **Joyuci** — Haftalık tahmin, tehlikeli koşullar ve aktivite önerileri için sohbet arayüzü. Bahsettiğiniz konumdaki hava durumuna göre sizlere yardımcı olur.
- **Reminders** — Belirlediğin saatte ve şehirde otomatik hava durumu e-postası gönderir. 
- **Relaxing Music** — Kullanıcıyı uygulamada tutma amaçlı kullanıcı günlük işleriyle ilgilenirken dinlenilebilecek odak arttıran sesler. Hava durumu uygulaması olduğu için çoğunlukla doğa sesleri içerir.
- **Hesap** — Kayıt, giriş, favori şehirler, profil, şifre sıfırlama gibi temel özellikler.

Kullanıcı verileri yerel `users.json` dosyasında tutulur. API ve mail ayarları `.env` dosyasından okunur.

## Gereksinimler

- Python 3.10 veya üzeri
- [OpenWeatherMap](https://openweathermap.org/api) API anahtarı
- SMTP bilgileri

## Kurulum

Depoyu klonla ve proje köküne gir:

```bash
git clone https://github.com/ysftrasci/ClimaMind.git
cd UmbrellaReminder
```

Sanal ortam (önerilir):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
```

Bağımlılıklar:

```bash
pip install -r requirements.txt #Gerekli malzemeleri otomatik projeye dahil eder.
```

Ortam değişkenleri:

```bash
copy .env.example .env
```

`.env` içine en az şunları yaz:


| Değişken               | Açıklama                     |
| ---------------------- | ---------------------------- |
| `OPENWEATHER_API_KEY`  | OpenWeather API key          |
| `SMTP_SENDER_EMAIL`    | Gönderen e-posta adresi      |
| `SMTP_SENDER_PASSWORD` | Gmail için App Password.     |
| `SMTP_HOST`            | Varsayılan: `smtp.gmail.com` |
| `SMTP_PORT`            | Varsayılan: `587`            |


## Çalıştırma

Proje kökünden:

```bash
python run.py
```

## Proje yapısı

```
UmbrellaReminder/
├── run.py
├── requirements.txt
├── .env.example
├── users.example.json
├── src/climamind/
│   ├── app.py              # Başlangıç ve servis bağlantıları
│   ├── config/
│   ├── domain/
│   ├── infrastructure/   # API, SMTP, users.json, ses
│   ├── services/
│   └── ui/views/           # Ekranlar
├── Resimler/               # Arayüz görselleri
├── sounds/                 # Tıklama vb. efektler
└── Müzikler/               # Müzik MP3’leri 
```

