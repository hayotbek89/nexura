from nexura.parsers.nmap import parse_nmap
from nexura.parsers.nuclei import parse_nuclei
from nexura.parsers.nikto import parse_nikto
from nexura.parsers.gobuster import parse_gobuster
from nexura.models.schemas import PortInfo, Vulnerability


NMAP_OUTPUT = """
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for example.com (93.184.216.34)
PORT    STATE    SERVICE
22/tcp  open     SSH
80/tcp  open     HTTP
443/tcp open     HTTPS
8080/tcp closed  HTTP-Alt

Nmap done: 1 IP address scanned
"""

NUCLEI_OUTPUT = """
[critical] test-sqli-1 [http://example.com]
[high] test-xss-2 [http://example.com]
[medium] test-config [http://example.com]
[low] test-info [http://example.com]
"""

NIKTO_OUTPUT = """
- Nikto v2.5.0
+ Server: nginx
+ /: Retrieved x-powered-by header: PHP/7.4.
+ /admin/: Admin login page found.
"""

GOBUSTER_OUTPUT = """
/admin (Status: 200)
/login (Status: 200)
/backup (Status: 403)
/robots.txt (Status: 200)
/admin/login.php (Status: 301)
"""


def test_parse_nmap():
    result = parse_nmap(NMAP_OUTPUT)
    open_ports = [p for p in result["ports"] if p.state == "open"]
    assert len(open_ports) == 3
    assert open_ports[0].port == 22
    assert open_ports[0].service == "SSH"
    assert open_ports[2].port == 443


def test_parse_nuclei():
    result = parse_nuclei(NUCLEI_OUTPUT)
    assert len(result["vulnerabilities"]) == 4
    assert result["vulnerabilities"][0].severity == "CRITICAL"
    assert result["vulnerabilities"][1].severity == "HIGH"
    assert "test-sqli" in result["vulnerabilities"][0].name


def test_parse_nikto():
    result = parse_nikto(NIKTO_OUTPUT)
    assert len(result["vulnerabilities"]) > 0


def test_parse_gobuster():
    result = parse_gobuster(GOBUSTER_OUTPUT)
    assert len(result["vulnerabilities"]) >= 3
