from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ToolType(str, Enum):
    NMAP = "nmap"
    NUCLEI = "nuclei"
    NIKTO = "nikto"
    SQLMAP = "sqlmap"
    GOBUSTER = "gobuster"
    AMASS = "amass"
    NETWORK = "network"


class ScanTarget(BaseModel):
    target: str
    description: Optional[str] = None


class ToolCommand(BaseModel):
    tool: ToolType
    args: list[str]
    description: str


class ScanPlan(BaseModel):
    target: str
    intent: str
    tools: list[ToolCommand]
    reasoning: str


class PortInfo(BaseModel):
    port: int
    state: str
    service: Optional[str] = None
    version: Optional[str] = None


class Vulnerability(BaseModel):
    name: str
    severity: str
    description: Optional[str] = None
    url: Optional[str] = None
    cve: Optional[str] = None
    cvss: Optional[float] = None
    solution: Optional[str] = None


class ScanResult(BaseModel):
    tool: str
    target: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool
    raw_output: Optional[str] = None
    error: Optional[str] = None
    ports: list[PortInfo] = []
    vulnerabilities: list[Vulnerability] = []
    summary: Optional[str] = None


class ScanReport(BaseModel):
    id: str
    target: str
    intent: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    results: list[ScanResult] = []
    html_path: Optional[str] = None
