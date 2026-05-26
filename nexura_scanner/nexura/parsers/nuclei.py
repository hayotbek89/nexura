import re
from nexura.models.schemas import Vulnerability


def parse_nuclei(raw: str) -> dict:
    vulns = []
    seen = set()

    for line in raw.splitlines():
        if "[critical]" in line.lower() or "[high]" in line.lower() or "[medium]" in line.lower() or "[low]" in line.lower():
            parts = line.split()
            sev = "unknown"
            for s in ["critical", "high", "medium", "low", "info"]:
                if f"[{s}]" in line.lower():
                    sev = s
                    break
            name = line.strip()[:120]
            key = f"{sev}:{name}"
            if key not in seen:
                seen.add(key)
                vulns.append(Vulnerability(name=name, severity=sev.upper()))

    return {
        "vulnerabilities": vulns,
        "summary": f"{len(vulns)} ta zaiflik topildi",
    }
