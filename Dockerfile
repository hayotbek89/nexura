FROM python:3.11-slim

RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    nmap wget unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/sullo/nikto/archive/refs/heads/master.zip -O /tmp/nikto.zip \
    && unzip -q /tmp/nikto.zip -d /tmp/ \
    && mv /tmp/nikto-master/program /opt/nikto \
    && ln -s /opt/nikto/nikto.pl /usr/local/bin/nikto \
    && rm -rf /tmp/nikto.zip /tmp/nikto-master

RUN wget -q https://github.com/sqlmapproject/sqlmap/archive/refs/heads/master.zip -O /tmp/sqlmap.zip \
    && unzip -q /tmp/sqlmap.zip -d /opt/ \
    && ln -s /opt/sqlmap-master/sqlmap.py /usr/local/bin/sqlmap \
    && rm -rf /tmp/sqlmap.zip

RUN wget -q https://github.com/OJ/gobuster/releases/latest/download/gobuster_Linux_x86_64.tar.gz -O /tmp/gobuster.tar.gz \
    && tar -xzf /tmp/gobuster.tar.gz -C /usr/local/bin/ \
    && rm -rf /tmp/gobuster.tar.gz

RUN wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip -O /tmp/nuclei.zip \
    && unzip -q /tmp/nuclei.zip -d /tmp/nuclei \
    && mv /tmp/nuclei/nuclei /usr/local/bin/nuclei \
    && rm -rf /tmp/nuclei.zip /tmp/nuclei

WORKDIR /app
COPY nexura_scanner/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY nexura_scanner/ .
RUN mkdir -p /app/gguf_models

ENV NEXURA_MODEL=/app/gguf_models/qwen2.5-7b-instruct-q4_k_m.gguf
EXPOSE 8080
CMD ["python", "-m", "nexura", "web"]
