from __future__ import annotations
import socket
import ssl
import time
import random
import threading
from typing import Optional
from collections import OrderedDict
from urllib.parse import urlparse
from datetime import datetime
import httpx

from nexura.models.schemas import PortInfo, ScanResult, Vulnerability


WELL_KNOWN_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 135: "RPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 9200: "Elasticsearch", 27017: "MongoDB",
}

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                 443, 445, 993, 995, 1433, 1521, 3306, 3389,
                 5432, 5900, 6379, 8080, 8443, 9200, 27017]


class NetworkScanner:
    def __init__(self):
        self._dns_cache = DNSCache()

    def quick_scan(self, host: str, ports: list[int] | None = None) -> ScanResult:
        target = self._normalize(host)
        start = datetime.now()
        result = ScanResult(tool="network", target=target, start_time=start, success=False)

        ip = self._resolve(target)
        if not ip:
            result.error = f"DNS resolve failed: {target}"
            result.end_time = datetime.now()
            return result

        ports = ports or DEFAULT_PORTS
        open_ports = []

        for port in ports:
            is_open, latency = self._tcp_connect(ip, port)
            if is_open:
                open_ports.append(PortInfo(
                    port=port,
                    state="open",
                    service=WELL_KNOWN_SERVICES.get(port, "unknown"),
                ))

        result.ports = open_ports
        result.summary = f"{len(open_ports)}/{len(ports)} ports open"
        result.success = True
        result.end_time = datetime.now()
        return result

    def full_health_check(self, target: str) -> dict:
        hostname = self._normalize(target)
        ip = self._resolve(hostname)
        if not ip:
            return {"target": target, "reachable": False, "error": "DNS resolve failed"}

        info = {"target": target, "ip": ip, "reachable": False, "ports": [], "ssl": {}, "waf": "UNKNOWN"}

        is_open, latency = self._tcp_connect(ip, 80)
        if not is_open:
            is_open, latency = self._tcp_connect(ip, 443)

        info["reachable"] = is_open
        info["latency_ms"] = latency

        if not is_open:
            info["error"] = "Not reachable on ports 80/443"
            return info

        for port in [21, 22, 80, 443, 8080, 8443, 3306, 5432]:
            o, _ = self._tcp_connect(ip, port)
            if o:
                info["ports"].append(port)

        if 443 in info["ports"] or 8443 in info["ports"]:
            info["ssl"] = self._check_ssl(hostname)

        url = f"https://{hostname}" if 443 in info["ports"] else f"http://{hostname}"
        info["waf"] = self._detect_waf(url)

        return info

    def _normalize(self, target: str) -> str:
        target = target.strip().lower()
        for prefix in ["https://", "http://", "ftp://"]:
            if target.startswith(prefix):
                return target[len(prefix):].split("/")[0]
        return target.split("/")[0]

    def _resolve(self, hostname: str) -> str | None:
        try:
            return self._dns_cache.resolve(hostname)
        except Exception:
            return None

    def _tcp_connect(self, ip: str, port: int, timeout: float = 2.0) -> tuple[bool, float]:
        start = time.time()
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True, round((time.time() - start) * 1000, 2)
        except Exception:
            return False, 0.0

    def _check_ssl(self, hostname: str, port: int = 443) -> dict:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    if not cert:
                        return {"valid": False, "error": "No certificate"}
                    expiry_str = cert.get("notAfter", "")
                    try:
                        expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
                        days = (expiry - datetime.utcnow()).days
                    except Exception:
                        days = -1
                    issuer = ""
                    for part in cert.get("issuer", ()):
                        for k, v in part:
                            if k == "organizationName":
                                issuer = v
                    return {
                        "valid": days > 0,
                        "issuer": issuer,
                        "days_left": days,
                        "protocol": ssock.version(),
                        "cipher": ssock.cipher()[0] if ssock.cipher() else "",
                    }
        except Exception as e:
            return {"valid": False, "error": str(e)[:100]}

    def _detect_waf(self, url: str) -> str:
        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
            server = resp.headers.get("server", "").lower()
            waf_map = {
                "cloudflare": "Cloudflare", "sucuri": "Sucuri",
                "incapsula": "Imperva", "akamai": "Akamai",
                "f5": "F5 BIG-IP", "barracuda": "Barracuda",
                "fortinet": "Fortinet", "aws": "AWS WAF",
                "modsecurity": "ModSecurity",
            }
            for sig, name in waf_map.items():
                if sig in server:
                    return name
            if "cf-ray" in resp.headers:
                return "Cloudflare"
            return "NONE"
        except Exception:
            return "UNKNOWN"


class DNSCache:
    def __init__(self, max_entries: int = 1000, ttl: int = 300):
        self.max = max_entries
        self.ttl = ttl
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._lock = threading.Lock()

    def resolve(self, hostname: str) -> str:
        with self._lock:
            now = time.time()
            if hostname in self._cache:
                ip, ts = self._cache[hostname]
                if now - ts < self.ttl:
                    return ip
                del self._cache[hostname]
        ip = socket.gethostbyname(hostname)
        with self._lock:
            if len(self._cache) >= self.max:
                self._cache.popitem(last=False)
            self._cache[hostname] = (ip, time.time())
        return ip


def parse_network(raw: str) -> dict:
    return {"summary": raw[:200]}
