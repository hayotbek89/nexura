from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nexura.models.schemas import ScanReport
from nexura.ai_engine import AIEngine
from nexura.tool_selector import ToolSelector
from nexura.runner import ScanRunner
from nexura.report.generator import ReportGenerator
from nexura.parsers.network import NetworkScanner
from nexura import config

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
REPORTS_DIR = config.REPORTS_DIR

app = FastAPI(title="Nexura Scanner", version="1.0.0")

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

_engine = None
_selector = None
runner = ScanRunner()
reporter = ReportGenerator()
scanner = NetworkScanner()


def get_engine():
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine


def get_selector():
    global _selector
    engine = get_engine()
    if _selector is None and engine.is_ready:
        _selector = ToolSelector(engine)
    return _selector


class ScanRequest(BaseModel):
    prompt: str
    target: str | None = None


class QuickScanRequest(BaseModel):
    target: str


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = FRONTEND_DIST / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Nexura Scanner</h1><p>Frontend not built. Run: cd frontend && npm run build</p>")


@app.post("/api/scan")
async def start_scan(req: ScanRequest):
    selector = get_selector()
    if not selector:
        engine = get_engine()
        if not engine.is_ready:
            return JSONResponse(
                status_code=503,
                content={"error": "AI Engine yoqilmagan. GGUF model faylini joylashtiring."},
            )
        selector = ToolSelector(engine)
        global _selector
        _selector = selector

    plan = selector.create_plan(req.prompt, req.target)
    report = reporter.create_report(plan.target, plan.intent)

    for tc in plan.tools:
        result = runner.run(tc, plan.target)
        report.results.append(result)

    report.end_time = datetime.now()
    report.status = "completed"

    html_path = reporter.save(report, fmt="both")
    return {
        "id": report.id,
        "target": report.target,
        "intent": plan.intent,
        "tools": [t.tool for t in plan.tools],
        "results": [r.model_dump(mode="json", exclude_none=True) for r in report.results],
        "report_html": html_path,
    }


@app.post("/api/quick-scan")
async def quick_scan(req: QuickScanRequest):
    result = scanner.quick_scan(req.target)
    return result.model_dump(mode="json", exclude_none=True)


@app.get("/api/status")
async def status():
    engine = get_engine()
    return {
        "name": "Nexura Scanner",
        "version": "1.0.0",
        "ai_ready": engine.is_ready,
        "tools": _check_tools(),
    }


@app.get("/api/history")
async def get_history():
    if not REPORTS_DIR.exists():
        return {"reports": []}
    reports = []
    for f in sorted(REPORTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            total_vulns = sum(len(r.get("vulnerabilities", [])) for r in data.get("results", []))
            severities = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for r in data.get("results", []):
                for v in r.get("vulnerabilities", []):
                    sev = v.get("severity", "").upper()
                    if sev in severities:
                        severities[sev] += 1
            reports.append({
                "id": data.get("id", ""),
                "target": data.get("target", ""),
                "intent": data.get("intent", ""),
                "date": data.get("start_time", ""),
                "status": data.get("status", ""),
                "total_vulns": total_vulns,
                "severities": severities,
                "tools": list(set(r.get("tool", "") for r in data.get("results", []))),
                "filename": f.stem,
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return {"reports": reports}


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    for f in REPORTS_DIR.glob(f"{report_id}.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        return data
    for f in REPORTS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("id") == report_id:
                return data
        except json.JSONDecodeError:
            continue
    return JSONResponse(status_code=404, content={"error": "Hisobot topilmadi"})


def _check_tools() -> dict:
    import shutil, os
    tools = ["nmap", "nuclei", "nikto", "sqlmap", "gobuster", "amass"]
    result = {}
    for t in tools:
        path = shutil.which(t)
        if not path:
            extra = {
                "nmap": r"C:\Program Files\nmap\nmap.exe",
                "nuclei": os.path.expanduser(r"~\nuclei\nuclei.exe"),
            }
            if t in extra and os.path.exists(extra[t]):
                path = extra[t]
        result[t] = path is not None
    return result
