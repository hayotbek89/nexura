from __future__ import annotations
import subprocess
import shutil
from datetime import datetime
from nexura.models.schemas import ToolCommand, ToolType, ScanResult


class ScanRunner:
    def run(self, command: ToolCommand, target: str) -> ScanResult:
        tool = command.tool
        start = datetime.now()
        result = ScanResult(tool=tool.value, target=target, start_time=start, success=False)

        binary = shutil.which(tool.value)
        if not binary:
            result.error = f"{tool.value} topilmadi. O'rnatish kerak."
            result.end_time = datetime.now()
            return result

        cmd = [binary] + command.args
        result.raw_output = self._execute(cmd)

        parsed = self._parse(tool, result.raw_output)
        result.ports = parsed.get("ports", [])
        result.vulnerabilities = parsed.get("vulnerabilities", [])
        result.summary = parsed.get("summary")
        result.success = True
        result.end_time = datetime.now()
        return result

    def _execute(self, cmd: list[str]) -> str:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return r.stdout or r.stderr
        except subprocess.TimeoutExpired:
            return "TIMEOUT: Skanerlash 300 soniyadan oshdi."
        except Exception as e:
            return f"ERROR: {e}"

    def _parse(self, tool: ToolType, output: str) -> dict:
        if tool == ToolType.NMAP:
            from nexura.parsers.nmap import parse_nmap
            return parse_nmap(output)
        elif tool == ToolType.NUCLEI:
            from nexura.parsers.nuclei import parse_nuclei
            return parse_nuclei(output)
        elif tool == ToolType.NIKTO:
            from nexura.parsers.nikto import parse_nikto
            return parse_nikto(output)
        elif tool == ToolType.SQLMAP:
            from nexura.parsers.sqlmap import parse_sqlmap
            return parse_sqlmap(output)
        elif tool == ToolType.GOBUSTER:
            from nexura.parsers.gobuster import parse_gobuster
            return parse_gobuster(output)
        elif tool == ToolType.NETWORK:
            from nexura.parsers.network import parse_network
            return parse_network(output)
        elif tool == ToolType.AMASS:
            from nexura.parsers.amass import parse_amass
            return parse_amass(output)
        return {"summary": output[:200]}
