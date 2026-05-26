import re
from nexura.models.schemas import Vulnerability


def parse_amass(raw: str) -> dict:
    vulns = []
    seen = set()

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "OWASP Amass" in line:
            continue
        if "Subdomain Name" in line and "Source" in line:
            continue
        if "requests completed" in line.lower():
            continue
        if "/" in line and "requests" in line.lower():
            continue

        m = re.match(r"^([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})\s+", line)
        if m:
            subdomain = m.group(1).lower()
            if subdomain not in seen:
                seen.add(subdomain)
                vulns.append(Vulnerability(
                    name=f"Subdomain: {subdomain}",
                    severity="INFO",
                    description=f"Discovered subdomain: {subdomain}",
                    url=f"https://{subdomain}" if not subdomain.startswith("http") else subdomain,
                ))

    if not vulns:
        domain_pattern = re.compile(r"([a-zA-Z0-9][a-zA-Z0-9._-]+\.[a-zA-Z]{2,})")
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            m = domain_pattern.match(line)
            if m:
                subdomain = m.group(1).lower()
                if subdomain not in seen:
                    seen.add(subdomain)
                    vulns.append(Vulnerability(
                        name=f"Subdomain: {subdomain}",
                        severity="INFO",
                        description=f"Discovered subdomain: {subdomain}",
                        url=f"https://{subdomain}",
                    ))

    return {
        "vulnerabilities": vulns,
        "summary": f"{len(vulns)} ta subdomain topildi",
    }
