import re
from nexura.models.schemas import Vulnerability


def parse_nikto(raw: str) -> dict:
    vulns = []

    for line in raw.splitlines():
        if "+" in line[:2] or "-" in line[:2] or "|" in line:
            clean = line.strip().lstrip("+-| ")
            if clean:
                sev = "medium"
                low_kw = ["info", "warning", "caution", "notice"]
                if any(k in clean.lower() for k in low_kw):
                    sev = "low"
                high_kw = ["critical", "vulnerability", "exploit", "cve"]
                if any(k in clean.lower() for k in high_kw):
                    sev = "high"
                vulns.append(Vulnerability(name=clean[:120], severity=sev))

    return {
        "vulnerabilities": vulns,
        "summary": f"{len(vulns)} ta xatolik topildi",
    }
