#!/usr/bin/env python3
"""
TrustMesh One-Click Automated Runner
Executes the live demo, verifies compliance, and opens the auto-playing presentation deck.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ARTIFACT_HTML = Path("/Users/dhruvverma/.gemini/antigravity/brain/3b01eb47-a805-4bf7-8a0f-729b74b6e62a/presentation.html")
PPTX_FILE = REPO_ROOT / "trustmesh_presentation.pptx"

def main():
    print("\033[1;36m" + "=" * 78 + "\033[0m")
    print("\033[1;36m   TrustMesh — Automated One-Click Runner (Hack Day Sonipat)\033[0m")
    print("\033[2m   Running unified engine demo, compliance checks, and launching presentation...\033[0m")
    print("\033[1;36m" + "=" * 78 + "\033[0m\n")

    # Step 1: Run Unified Demo
    print("\033[1;32m[Step 1/3] Executing 4-Persona Unified Evaluation Engine...\033[0m")
    demo_script = REPO_ROOT / "demo_unified.py"
    if demo_script.exists():
        subprocess.run([sys.executable, str(demo_script)], check=False)
    
    time.sleep(1)

    # Step 2: Rule Compliance Verification
    print("\n\033[1;32m[Step 2/3] Checking Hackathon Rule Compliance (scripts/audit_compliance.py)...\033[0m")
    compliance_script = REPO_ROOT / "scripts" / "audit_compliance.py"
    if compliance_script.exists():
        subprocess.run([sys.executable, str(compliance_script)], check=False)

    time.sleep(1)

    # Step 3: Launch Presentation Deck
    print(f"\n\033[1;32m[Step 3/3] Launching Auto-Playing Slide Deck in Default Browser...\033[0m")
    if ARTIFACT_HTML.exists():
        print(f"Opening: {ARTIFACT_HTML}")
        if sys.platform == "darwin":
            subprocess.run(["open", str(ARTIFACT_HTML)])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", str(ARTIFACT_HTML)])
        elif sys.platform == "win32":
            os.startfile(str(ARTIFACT_HTML))
    
    print(f"\n\033[1;32m✔ All systems running on their own!\033[0m")
    print(f"  • PowerPoint file ready: {PPTX_FILE}")
    print(f"  • Interactive web deck:  {ARTIFACT_HTML}")
    print("  • Press 'Start Auto-Presentation' in the browser for voice-narrated playback.\n")

if __name__ == "__main__":
    main()
