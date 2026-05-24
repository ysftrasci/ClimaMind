# Clima Mind (Umbrella Reminder)

A desktop weather and lifestyle app built with **Python** and **Tkinter**. Search weather, chat with **Joyuci**, set email reminders, relax with nature sounds, and manage your account — all in one place.

## Features

- **Search Weather** — current conditions for any city (OpenWeatherMap)
- **Joyuci** — AI-style weather assistant (forecasts, safety tips, activity ideas)
- **Reminders** — scheduled weather emails
- **Relaxing Music** — nature ambience player
- **Account** — registration, favorites, profile, password reset

## Requirements

- **Python 3.10+** (Tkinter included with most Python installs on Windows)
- OpenWeatherMap API key
- SMTP credentials (optional, for registration / reminders / password reset)

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/UmbrellaReminder.git
cd UmbrellaReminder
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

```bash
copy .env.example .env
```

Edit `.env` and set:

| Variable | Description |
|----------|-------------|
| `OPENWEATHER_API_KEY` | From [OpenWeatherMap](https://openweathermap.org/api) |
| `SMTP_SENDER_EMAIL` | Sender email address |
| `SMTP_SENDER_PASSWORD` | App password (e.g. Gmail App Password) |
| `SMTP_HOST` / `SMTP_PORT` | Usually `smtp.gmail.com` / `587` |

### 5. Local user data (first run)

`users.json` is **not** in Git (it contains passwords). For a fresh setup:

```bash
copy users.example.json users.json
```

Or start the app and **Sign Up** to create your first account.

### 6. Run the app

```bash
python run.py
```

No `PYTHONPATH` setup is required — `run.py` adds `src/` automatically.

## Project layout

```
UmbrellaReminder/
├── run.py              # Entry point
├── requirements.txt
├── .env.example        # Template for secrets (copy to .env)
├── users.example.json  # Template for local user DB
├── src/climamind/      # Application code
│   ├── app.py          # Bootstrap & DI
│   ├── config/         # Settings & paths
│   ├── domain/         # Models
│   ├── infrastructure/ # API, email, persistence, audio
│   ├── services/       # Business logic
│   └── ui/             # Views & widgets
├── Resimler/           # UI images
├── sounds/             # UI sound effects
└── Müzikler/           # Nature sound MP3s (add your own tracks)
```

## Security notes

- **Never commit** `.env` or `users.json`.
- If API keys or passwords were ever committed to Git, **rotate them** in the provider dashboards and treat the old values as compromised.
- Use Gmail **App Passwords** (not your main account password) for SMTP.

## License

Add your license here (e.g. MIT) if you publish the repository.

## Contributing

1. Fork the repo  
2. Create a feature branch  
3. Open a pull request  

---

**Clima Mind** — stay dry, stay informed.
