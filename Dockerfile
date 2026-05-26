FROM python:3.11-slim

RUN apt-get update -qq && apt-get install -y -qq \
    nmap nikto sqlmap gobuster wget unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip \
    && unzip -q nuclei_linux_amd64.zip -d /tmp/nuclei \
    && mv /tmp/nuclei/nuclei /usr/local/bin/nuclei \
    && rm -rf nuclei_linux_amd64.zip /tmp/nuclei

WORKDIR /app
COPY nexura_scanner/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY nexura_scanner/ .
RUN mkdir -p /app/gguf_models

ENV NEXURA_MODEL=/app/gguf_models/qwen2.5-7b-instruct-q4_k_m.gguf
EXPOSE 8080
CMD ["python", "-m", "nexura", "web"]
