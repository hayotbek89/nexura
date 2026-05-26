#!/bin/bash
# Docker container ichida ishga tushirish
set -e

docker build -t nexura-scanner .

echo "✅ Docker image yaratildi: nexura-scanner"
echo ""
echo "Ishga tushirish:"
echo "  docker run --rm -it nexura-scanner scan 'example.com ni zaifliklarga tekshir'"
echo "  docker run --rm -p 8080:8080 nexura-scanner web"
