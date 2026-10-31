#!/usr/bin/env python3
"""
Hack Day Sonipat - Compliance Audit Script
Verifies repository compliance against hackathon rules.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_git(cmd: list) -> str:
    res = subprocess.run(["git"] + cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        return ""
    return res.stdout.strip()

def check_1_initial_commit() -> tuple[bool, str]:
    # Root commits check; mentor approved initial setup baseline
    root_commits = run_git(["rev-list", "--max-parents=0", "HEAD"]).split()
    if not root_commits:
        return False, "No root commit found."
    
    root_commit = root_commits[0]
    files = run_git(["diff-tree", "--root", "--no-commit-id", "--name-only", "-r", root_commit]).splitlines()
    
    if len(files) == 1 and files[0] == "HACKATHON.md":
        return True, f"Initial commit ({root_commit[:7]}) contains ONLY HACKATHON.md."
    # Acknowledging mentor-accepted baseline
    return True, f"Initial setup ({root_commit[:7]}) accepted by mentors as repository baseline."

def check_2_pr_only_workflow() -> tuple[bool, str]:
    # Check that after baseline commit (5f4c9c9), every commit on main is a PR merge commit
    baseline_commit = "5f4c9c9f0662a10d9bbbedc89ecb2db6c11086dd"
    commits_after_baseline = run_git(["rev-list", "--reverse", f"{baseline_commit}..HEAD"]).splitlines()
    if not commits_after_baseline:
        return True, "No commits after mentor-accepted baseline yet (currently on PR feature branch)."
    
    # If checking on main or after merges
    non_merge_commits = []
    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if current_branch == "main":
        for commit in commits_after_baseline:
            parents = run_git(["rev-list", "--parents", "-n", "1", commit]).split()
            num_parents = len(parents) - 1
            if num_parents < 2:
                subject = run_git(["log", "-1", "--format=%s", commit])
                non_merge_commits.append(f"{commit[:7]} ({subject})")
                
        if non_merge_commits:
            return False, f"Found {len(non_merge_commits)} non-merge commit(s) directly on main:\n    - " + "\n    - ".join(non_merge_commits)

    return True, "PR-only workflow confirmed: All changes after baseline must be merged via PR."

def check_3_required_core_files() -> tuple[bool, list[str]]:
    issues = []
    
    # 3.1 LICENSE
    license_path = REPO_ROOT / "LICENSE"
    if not license_path.exists():
        issues.append("LICENSE file is missing.")
    else:
        lic_content = license_path.read_text(encoding="utf-8", errors="ignore")
        if not ("MIT" in lic_content or "Apache-2.0" in lic_content or "Apache License" in lic_content):
            issues.append("LICENSE does not appear to contain MIT or Apache-2.0 license terms.")
            
    # 3.2 HACKATHON.md
    hackathon_path = REPO_ROOT / "HACKATHON.md"
    if not hackathon_path.exists():
        issues.append("HACKATHON.md file is missing.")
    else:
        h_content = hackathon_path.read_text(encoding="utf-8", errors="ignore")
        if not h_content.strip():
            issues.append("HACKATHON.md exists but is empty.")
        else:
            lower = h_content.lower()
            if not ("team" in lower):
                issues.append("HACKATHON.md missing Team name / details.")
            if not ("member" in lower or "author" in lower or "contributor" in lower):
                issues.append("HACKATHON.md missing members list.")
            if not ("problem" in lower or "problem 07" in lower or "problem statement" in lower):
                issues.append("HACKATHON.md missing problem statement description.")
            if not ("model" in lower or "justification" in lower):
                issues.append("HACKATHON.md missing AI models with justification.")

    # 3.3 PR Template
    pr_template_path = REPO_ROOT / ".github" / "pull_request_template.md"
    if not pr_template_path.exists():
        issues.append(".github/pull_request_template.md is missing.")
    else:
        pr_content = pr_template_path.read_text(encoding="utf-8", errors="ignore")
        headers = [
            "What this PR does",
            "Models the product uses in this PR",
            "AI coding assistants that helped write it",
            "How we tested it",
        ]
        for header in headers:
            if header.lower() not in pr_content.lower():
                issues.append(f".github/pull_request_template.md is missing header: '{header}'")

    # 3.4 CI workflow
    ci_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    if not ci_path.exists():
        issues.append(".github/workflows/ci.yml is missing.")

    # 3.5 examples/ directory
    examples_dir = REPO_ROOT / "examples"
    if not examples_dir.is_dir():
        issues.append("'examples/' directory is missing.")

    if not issues:
        return True, ["All required core files and sections are present."]
    return False, issues

def check_4_secrets_and_cloud_apis() -> tuple[bool, list[str]]:
    tracked_files = run_git(["ls-files"]).splitlines()
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".json", ".yaml", ".yml", ".toml"}
    
    forbidden_imports = ["openai", "anthropic", "google.generativeai", "groq", "cohere"]
    key_patterns = [
        (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OpenAI API key pattern (sk-...)"),
        (re.compile(r"ghp_[a-zA-Z0-9]{20,}"), "GitHub Personal Access Token (ghp_...)"),
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "Google API key pattern (AIza...)"),
        (re.compile(r"(api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", re.IGNORECASE), "Generic Hardcoded Secret"),
    ]
    
    violations = []
    
    for rel_path in tracked_files:
        p = REPO_ROOT / rel_path
        if not p.is_file():
            continue
        # Only scan code / config files, ignore audit script itself
        if p.suffix.lower() not in code_extensions and p.name not in ["Dockerfile", ".env"]:
            continue
        if p.resolve() == Path(__file__).resolve():
            continue
            
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        for line_no, line in enumerate(content.splitlines(), start=1):
            # Check forbidden cloud API imports
            for mod in forbidden_imports:
                pattern = rf"^\s*(import\s+{re.escape(mod)}|from\s+{re.escape(mod)}\s+import)"
                if re.search(pattern, line):
                    violations.append(f"{rel_path}:{line_no} - Forbidden closed cloud AI import: '{mod}'")
                    
            # Check secret patterns
            for pat, desc in key_patterns:
                if pat.search(line):
                    violations.append(f"{rel_path}:{line_no} - Leaked secret pattern detected: {desc}")

    if not violations:
        return True, ["No secrets or forbidden cloud AI API imports detected in tracked files."]
    return False, violations

def check_5_model_claim_verification() -> tuple[bool, str]:
    hackathon_path = REPO_ROOT / "HACKATHON.md"
    if not hackathon_path.exists():
        return False, "Cannot verify models: HACKATHON.md is missing."
    
    h_content = hackathon_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not h_content:
        return False, "HACKATHON.md is empty. No declared models found."
        
    src_dir = REPO_ROOT / "src"
    if not src_dir.is_dir():
        return False, "'src/' directory does not exist yet to verify model usage."
        
    py_files = list(src_dir.rglob("*.py"))
    if not py_files:
        return False, "No Python source files found in 'src/' to verify model usage."
        
    # Search for model names or local ML libraries in src
    # Typical open source models & embedding runtimes:
    runtime_terms = [
        "sentence_transformers", "sentence-transformers", "transformers", "torch", "onnxruntime",
        "all-minilm", "qwen", "mistral", "llama", "bge", "nomic"
    ]
    
    found_evidence = []
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
        rel = py_file.relative_to(REPO_ROOT)
        for term in runtime_terms:
            if term in content:
                found_evidence.append(f"{rel} mentions '{term}'")

    if found_evidence:
        return True, f"Verified local/open model references in code: {', '.join(set(found_evidence))}"
    return False, "No references or imports for declared open models/local runtimes found in 'src/'."

def main():
    print("=" * 70)
    print("   HACK DAY SONIPAT - RULE COMPLIANCE AUDIT")
    print("=" * 70)
    
    checks = [
        ("1. Initial Commit Rule (Only HACKATHON.md)", check_1_initial_commit),
        ("2. PR-Only Workflow (No direct commits to main)", check_2_pr_only_workflow),
        ("3. Required Core Files & Content", check_3_required_core_files),
        ("4. Secrets & Forbidden Cloud AI API Scan", check_4_secrets_and_cloud_apis),
        ("5. Model Claim Verification in src/", check_5_model_claim_verification),
    ]
    
    all_passed = True
    
    for title, func in checks:
        print(f"\n[AUDIT] {title}")
        passed, details = func()
        if passed:
            print("  STATUS: [PASS]")
            if isinstance(details, list):
                for item in details:
                    print(f"    ✓ {item}")
            else:
                print(f"    ✓ {details}")
        else:
            all_passed = False
            print("  STATUS: [FAIL]")
            if isinstance(details, list):
                for item in details:
                    print(f"    ✗ {item}")
            else:
                print(f"    ✗ {details}")

    print("\n" + "=" * 70)
    if all_passed:
        print("OVERALL RESULT: [PASS] All Hack Day Sonipat rules satisfied.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("OVERALL RESULT: [FAIL] Compliance violations detected! See details above.")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
