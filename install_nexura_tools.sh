#!/bin/bash
# NEXURA Infinity Gauntlet - Barcha tool'larni o'rnatish skripti
# Ubuntu/Debian uchun

set -e

echo "=========================================="
echo " NEXURA Infinity Gauntlet Setup"
echo "=========================================="

# System update
echo "[1/12] Sistema yangilanmoqda..."
sudo apt update && sudo apt upgrade -y

# Python va pip
echo "[2/12] Python o'rnatilmoqda..."
sudo apt install -y python3 python3-pip python3-venv

# Git
echo "[3/12] Git o'rnatilmoqda..."
sudo apt install -y git curl wget

# OWASP ZAP
echo "[4/12] OWASP ZAP o'rnatilmoqda..."
sudo apt install -y zaproxy

# Nmap
echo "[5/12] Nmap o'rnatilmoqda..."
sudo apt install -y nmap

# Lynis
echo "[6/12] Lynis o'rnatilmoqda..."
sudo apt install -y lynis

# Trivy
echo "[7/12] Trivy o'rnatilmoqda..."
sudo apt install -y wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb stable main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install -y trivy

# Ansible
echo "[8/12] Ansible o'rnatilmoqda..."
sudo apt install -y ansible

# Docker (agar yo'q bo'lsa)
if ! command -v docker &> /dev/null; then
    echo "[9/12] Docker o'rnatilmoqda..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Docker Compose
echo "[10/12] Docker Compose o'rnatilmoqda..."
sudo apt install -y docker-compose

# OpenSCAP
echo "[11/12] OpenSCAP o'rnatilmoqda..."
sudo apt install -y libopenscap8 scap-workbench

# Additional tools
echo "[12/12] Qo'shimcha tools o'rnatilmoqda..."
sudo apt install -y net-tools tcpdump htop nethogs wireshark-common

echo "=========================================="
echo " O'rnatish tugadi!"
echo "=========================================="
echo ""
echo "Kerakli tool'lar:"
echo " - nmap:        $(which nmap || echo 'o'rnatilmagan')"
echo " - zaproxy:     $(which zaproxy || echo 'o'rnatilmagan')"
echo " - lynis:       $(which lynis || echo 'o'rnatilmagan')"
echo " - trivy:       $(which trivy || echo 'o'rnatilmagan')"
echo " - ansible:     $(which ansible || echo 'o'rnatilmagan')"
echo " - openscap:    $(which oscap || echo 'o'rnatilmagan')"
echo ""
echo "Docker Compose bilan qo'shimcha servislarni ishga tushirish uchun:"
echo "cd NEXURA && docker-compose up -d"
