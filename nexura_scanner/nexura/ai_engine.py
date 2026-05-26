from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional
from nexura import config


class AIEngine:
    def __init__(self):
        self._llm = None
        self._ready = False
        self._load_model()

    def _load_model(self):
        model_path = Path(config.LLAMA_MODEL_PATH)
        if not model_path.exists():
            return

        try:
            from llama_cpp import Llama

            self._llm = Llama(
                model_path=str(model_path),
                n_ctx=config.LLAMA_N_CTX,
                n_threads=config.LLAMA_N_THREADS,
                n_gpu_layers=config.LLAMA_N_GPU_LAYERS,
                verbose=False,
            )
            self._ready = True
        except Exception as e:
            import sys
            print(f"[NEXURA] AI Engine load error: {e}", file=sys.stderr)
            self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    def ask(self, system: str, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        if not self._ready:
            msg = "AI Engine yoqilmagan. GGUF model faylini gguf_models/ papkasiga joylashtiring."
            raise RuntimeError(msg)

        resp = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature or config.LLAMA_TEMP,
            max_tokens=max_tokens or config.LLAMA_MAX_TOKENS,
        )
        return resp["choices"][0]["message"]["content"].strip()

    def ask_structured(self, system: str, prompt: str) -> dict:
        raw = self.ask(system, prompt)
        return self._extract_json(raw)

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            text = match.group(1)

        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) > 2:
                text = "\n".join(lines[1:-1])

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Model JSON qaytarmadi:\n{text[:500]}")


SYSTEM_PROMPT = """You are NEXURA, an AI-powered vulnerability scanner orchestrator. Your only job is to analyze the user's request and determine which security scanning tool(s) to use.

AVAILABLE TOOLS:
1. **nmap** — Network mapping, port scanning, service/OS detection, NSE vulnerability scripts
   - Use for: port scanning, service discovery, OS detection, general network recon
   - Common args: -sV (version), -sC (default scripts), -A (aggressive), --script vuln (vuln scripts)
   - Example: targeting a web server → ["-sV", "-sC", "-p", "22,80,443,8080", "<target>"]

2. **nuclei** — Template-based vulnerability scanner (YAML templates)
   - Use for: web vulnerability detection, CVE checking, misconfiguration scanning
   - Common args: -severity critical,high,medium, -t (template path)
   - Example: web vulnerability scan → ["-severity", "critical,high,medium", "<target>"]

3. **nikto** — Web server scanner (finds outdated software, misconfigurations)
   - Use for: web server vulnerability assessment, CGI checks, outdated software
   - Common args: -h (host), -ssl (force SSL), -port (specific port)
   - Example: full web scan → ["-h", "<target>"]

4. **sqlmap** — SQL injection detection and exploitation
   - Use for: SQL injection testing on web parameters
   - Common args: --batch, --random-agent, --level, --risk
   - Example: test a URL → ["--batch", "--random-agent", "-u", "<target>"]

5. **gobuster** — Directory/file brute-forcing
   - Use for: discovering hidden directories, files, subdomains
   - Common args: dir (directory mode), -u (url), -w (wordlist)
   - Example: directory brute-force → ["dir", "-u", "<target>", "-w", "/usr/share/wordlists/dirb/common.txt"]

6. **amass** — Subdomain enumeration and attack surface mapping
   - Use for: discovering subdomains, DNS enumeration, attack surface discovery
   - Common args: enum (enumeration mode), -d (domain), -passive (passive mode)
   - Example: subdomain discovery → ["enum", "-d", "<target>"]
   - Example: passive subdomain discovery → ["enum", "-passive", "-d", "<target>"]

RULES:
- Always choose the MOST APPROPRIATE tool(s) for the user's intent
- For a general vulnerability assessment on a web target: use nmap + nuclei + nikto + amass
- For a specific SQL injection test: use sqlmap (and optionally nikto)
- For port scanning only: use nmap (lightweight)
- For directory discovery: use gobuster
- For subdomain discovery: use amass
- NEVER run aggressive/exploitative scans without user's explicit request
- ALWAYS output in the exact JSON format shown below
- <target> should be replaced with the actual target value
- If user doesn't specify a target, set "error" field

Output ONLY valid JSON in this exact format:
```json
{
  "target": "example.com or IP",
  "intent": "brief description of what user wants",
  "tools": [
    {
      "tool": "nmap",
      "args": ["-sV", "-sC", "-p", "22,80,443", "<target>"],
      "description": "Port va service skanerlash"
    }
  ],
  "reasoning": "Why these tools were chosen"
}
```
"""
