# NEXURA Scanner v1.0

AI-powered vulnerability scanner. Natural language orqali buyruq bering, AI kerakli tool'ni tanlab skanerlasin.

## Quick Start

### Linux (tavsiya)

```bash
# 1. Avtomatik o'rnatish
chmod +x scripts/setup_linux.sh
sudo ./scripts/setup_linux.sh

# 2. Skanerlash
nexura scan "example.com ni zaifliklarga tekshir"
```

### Docker

```bash
# 1. Build
docker build -t nexura-scanner .

# 2. Skanerlash
docker run --rm -it nexura-scanner scan "example.com ni zaifliklarga tekshir"

# 3. Web UI
docker run --rm -p 8080:8080 nexura-scanner web
```

### Windows (WSL)

1. WSL'da Linux setup skriptini ishga tushiring
2. Yoki Docker Desktop orqali

## Model yuklab olish

AI modeli kerak (4.7 GB). Ikki usul:

```bash
# Usul 1: Skript orqali
pip install huggingface-hub
python scripts/download_model.py

# Usul 2: To'g'ridan-to'g'ri
# https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf
# Faylni gguf_models/ papkasiga joylashtiring
```

AIsiz ishlatish: `nexura quick example.com` port skanerlash AIsiz ishlaydi.

## Buyruqlar

| Buyruq | Izoh |
|--------|------|
| `nexura scan "..."` | AI orqali skanerlash |
| `nexura quick example.com` | Tezkor port skanerlash (AIsiz) |
| `nexura web` | Web UI (http://localhost:8080) |
| `nexura list-models` | GGUF modellar ro'yxati |

## Tool'lar

Dastur ishlashi uchun quyidagi tool'lar kerak:
- **nmap** — port skanerlash
- **nuclei** — zaiflik skanerlash
- **nikto** — web server skanerlash
- **sqlmap** — SQL injection test
- **gobuster** — directory brute-force

`scripts/setup_linux.sh` ularni avtomatik o'rnatadi.
