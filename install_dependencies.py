#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEXURA Dependency Installation & Security Audit Script
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Command ishga tushirish va error handling"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ {description} muvaffaqiyatsiz!")
        return False
    print(f"✅ {description} muvaffaqiyatsiz!")
    return True

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         NEXURA Dependency Installation Script              ║
    ║              Installation & Security Audit                ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # 1. Upgrade pip
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "pip yangilash"
    ):
        return False

    # 2. Install production dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Production dependencies o'rnatish"
    ):
        return False

    # 3. Install development dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements-dev.txt",
        "Development dependencies o'rnatish"
    ):
        return False

    # 4. Run pip-audit for CVEs
    print("\n" + "="*60)
    print("▶ CVE va vulnerability scanning (pip-audit)")
    print("="*60)
    result = subprocess.run(f"{sys.executable} -m pip install pip-audit", shell=True)
    result = subprocess.run(f"{sys.executable} -m pip_audit", shell=True)

    if result.returncode == 0:
        print("✅ Barcha dependencies xavfsiz!")
    else:
        print("⚠️  Vulnerabilities topildi - pip-audit output ko'ring")

    # 5. Verify imports
    print("\n" + "="*60)
    print("▶ Critical modules import check")
    print("="*60)

    critical_modules = [
        'fastapi',
        'sqlalchemy',
        'pydantic',
        'cryptography',
        'pytest',
        'pandas',
        'numpy'
    ]

    for module in critical_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - INSTALL MUVAFFAQIYATSIZ")
            return False

    # 6. Summary
    print("\n" + "="*60)
    print("📊 Installation Summary")
    print("="*60)
    print("""
    ✅ pip upgraded
    ✅ Production dependencies installed
    ✅ Development dependencies installed
    ✅ Critical modules verified

    🎯 NEXT STEPS:
    1. Copy .env.example to .env:
       cp .env.example .env

    2. Update .env with real values:
       NEXURA_AUTH_TOKEN=<generate with secrets>
       NEXURA_MASTER_KEY=<generate with secrets>
       API keys = <get from services>

    3. Initialize database:
       alembic init migrations
       alembic upgrade head

    4. Run tests:
       pytest tests/ -v

    5. Start development server:
       python backend/main.py
    """)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

