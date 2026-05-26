import re
from nexura.models.schemas import Vulnerability


def parse_sqlmap(raw: str) -> dict:
    vulns = []

    for line in raw.splitlines():
        if "Parameter:" in line or "Type:" in line or "Title:" in line:
            vulns.append(Vulnerability(
                name=line.strip()[:120],
                severity="CRITICAL",
            ))
        if "is vulnerable" in line.lower():
            vulns.append(Vulnerability(
                name="SQL Injection",
                severity="CRITICAL",
            ))
        if "not injectable" in line.lower():
            return {
                "vulnerabilities": [],
                "summary": "SQL injection topilmadi",
            }

    if vulns:
        return {
            "vulnerabilities": vulns,
            "summary": f"{len(vulns)} ta potentsial SQL injection topildi",
        }
    return {
        "vulnerabilities": [],
        "summary": "SQL injection aniqlanmadi yoki skaner ishlamadi",
    }
