import re
from nexura.models.schemas import Vulnerability


def parse_gobuster(raw: str) -> dict:
    urls = []

    for line in raw.splitlines():
        m = re.match(r"^/(\S+)\s+\(Status:\s*(\d+)\)", line)
        if not m:
            m = re.match(r"^/(\S+)\s+\((\d+)\)", line)
        if m:
            urls.append({"path": f"/{m.group(1)}", "status": m.group(2)})

    vulns = []
    for u in urls:
        status = u["status"]
        if status.startswith("20") or status.startswith("30"):
            sev = "info" if status.startswith("30") else "low"
            vulns.append(Vulnerability(
                name=f"Discovered: {u['path']} ({status})",
                severity=sev,
            ))

    return {
        "vulnerabilities": vulns,
        "summary": f"{len(urls)} ta yo'l topildi",
    }
