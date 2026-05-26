import re
from nexura.models.schemas import PortInfo


def parse_nmap(raw: str) -> dict:
    ports = []
    in_port_section = False

    for line in raw.splitlines():
        if "PORT" in line and "STATE" in line and "SERVICE" in line:
            in_port_section = True
            continue
        if in_port_section:
            if not line.strip() or "TRACEROUTE" in line or "OS DETECTION" in line:
                in_port_section = False
                continue
            m = re.match(r"^(\d+)/(tcp|udp)\s+(\S+)\s+(\S+)?\s*(.*)?", line)
            if m:
                ports.append(PortInfo(
                    port=int(m.group(1)),
                    state=m.group(3),
                    service=m.group(4) or "unknown",
                    version=m.group(5) or None,
                ))

    vulns = []
    for line in raw.splitlines():
        if any(word in line.lower() for word in ["vuln", "cve-", "cve ", "vulnerability"]):
            vulns.append({"name": line.strip(), "severity": "unknown"})

    return {
        "ports": ports,
        "vulnerabilities": vulns,
        "summary": f"{len(ports)} port topildi, {len(vulns)} ta potentsial zaiflik",
    }
