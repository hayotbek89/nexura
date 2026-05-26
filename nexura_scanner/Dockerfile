FROM python:3.11-slim

RUN apt-get update -qq && apt-get install -y -qq \
    nmap nikto sqlmap gobuster wget unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip \
    && unzip -q nuclei_linux_amd64.zip -d /tmp/nuclei \
    && mv /tmp/nuclei/nuclei /usr/local/bin/nuclei \
    && rm -rf nuclei_linux_amd64.zip /tmp/nuclei

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY nexura/ nexura/
COPY gguf_models/ gguf_models/
COPY scripts/ scripts/

ENV NEXURA_MODEL=/app/gguf_models/qwen2.5-7b-instruct-q4_k_m.gguf
ENTRYPOINT ["python", "-m", "nexura"]
CMD ["--help"]
