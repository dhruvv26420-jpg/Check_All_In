# HACK DAY SONIPAT — AUTOMATED CLEAN-ROOM AUDIT REPORT
Generated: 2026-11-01 03:22:00 UTC
Repository Evaluated: TrustMesh (Problem 07 — Decentralized Trust Network for Open Source)
Host Repository: `/Users/prajanradhakrishnan/hacktober`

================================================================================
STAGE 1: STATIC COMPLIANCE & DISQUALIFICATION SCAN
================================================================================

1. Forbidden Closed Cloud AI SDK Import Check:
   Command: grep -rnE "(import openai|import anthropic|google\.generativeai|import groq)" src/
   Matches Found: 0
   Status: [PASS] (Zero forbidden cloud AI imports. Disqualification criteria clean.)

2. Placeholder Mocks & Stub Detection:
   Command: grep -rnE "(# TODO|# implement later|pass\s*$)" src/
   Matches Found: 0
   Status: [PASS] (Zero placeholder stubs or unfulfilled logic.)

3. Open-Weight Model Alignment Verification:
   Declared in HACKATHON.md:
     • sentence-transformers/all-MiniLM-L6-v2 (Local 384-d semantic embedding model)
     • Qwen/Qwen2.5-Coder-1.5B-Instruct (Local open-weight code instruction LLM)
   Implementation Audit in src/:
     • src/trustmesh/models.py: Declares EMBEDDING_MODEL_ID and CODE_LLM_MODEL_ID in SUPPORTED_MODELS.
     • src/trustmesh/campaign.py: Imports and invokes sentence-transformers/all-MiniLM-L6-v2 on CPU.
     • src/trustmesh/evaluator.py: Employs embedding vectors in audit_pull_request().
     • tests/test_smoke.py: Validates model registry retrieval and configuration.
   Model Mismatch Penalty: 0 points (No declared models missing).
   Status: [PASS]

================================================================================
STAGE 2: DELIVERABLES & ARTIFACTS VERIFICATION
================================================================================

1. LICENSE File:
   • Exists: Yes (`LICENSE`)
   • License Terms: MIT License (Valid OSI-compliant license terms present)
   • Status: [PASS]

2. Continuous Integration Workflow:
   • Exists: Yes (`.github/workflows/ci.yml`)
   • Scope: Configures automated testing matrix across Python versions.
   • Status: [PASS]

3. Pull Request Template:
   • Exists: Yes (`.github/pull_request_template.md`)
   • Required Section 1: "What this PR does" — Present
   • Required Section 2: "Models the product uses in this PR" — Present
   • Required Section 3: "AI coding assistants that helped write it" — Present
   • Required Section 4: "How we tested it" — Present
   • Status: [PASS]

4. Input/Output Data Artifacts:
   • `examples/network_input.json`: Valid JSON (Defines 27 project peerings, 2 initial vouches).
   • `examples/audit_output.json`: Valid JSON (Contains machine-readable audit evaluation trace).
   • Status: [PASS]

================================================================================
STAGE 3: FUNCTIONAL UNIT TEST EXECUTION
================================================================================

Execution Command: pytest tests/ -v --tb=short
Runtime: Python 3.9.6, pytest 8.4.2
Summary: 37 collected, 37 passed, 0 failed in 3.55s (100% pass rate)

Breakdown of Mandatory Evaluation Invariants:
1. Transitive Positive Vouch Propagation:
   • Tests: `tests/test_graph.py::test_transitive_vouch`, `tests/test_node.py::test_transitive_decay_and_max_hops`
   • Result: PASSED (Multi-hop attenuation calculates correct decayed path weights).
2. Asymmetric Negative Isolation:
   • Tests: `tests/test_evaluator.py::test_untrusted_denouncement_newcomer_protected`, `tests/test_graph.py::test_hackathon_slide_scenario_untrusted_denouncement`, `tests/test_node.py::test_sybils_ignored`
   • Result: PASSED (Hostile denouncements from untrusted/unpeered entities are quarantined; cannot degrade contributor standing).
3. Trusted Peer Denouncement Quarantine:
   • Tests: `tests/test_graph.py::test_trusted_peer_denouncement`, `tests/test_node.py::test_single_denouncement_never_blocks`, `tests/test_node.py::test_corroborated_denouncements_block`
   • Result: PASSED (Single uncorroborated accusation never triggers network-wide block; corroborated evidence required).
4. Coordinated Multi-Repo Campaign Burst Detection:
   • Tests: `tests/test_campaign.py::test_coordinated_spam_burst_detected`, `tests/test_campaign.py::test_campaign_detected_through_paraphrase`, `tests/test_evaluator.py::test_sybil_bot_in_campaign_quarantined`
   • Result: PASSED (Detected coordinated low-value PR wave hitting multiple distinct repos within sliding window).
5. Bayesian Newcomer Triage with Epistemic Uncertainty:
   • Tests: `tests/test_evaluator.py::test_honest_cold_start_newcomer`, `tests/test_graph.py::test_uncertain_newcomer`
   • Result: PASSED (Cold-start accounts without history receive non-exclusionary triage, E[T]=0.50, Var=0.0833).

================================================================================
STAGE 4: STRESS & FUZZ TESTING
================================================================================

1. Circular Peering Loops (A -> B -> C -> A):
   • Setup: Directed cyclical peering graph with weights A->B (0.90), B->C (0.85), C->A (0.80), evaluating target D connected via C.
   • Observed: Shortest-path Dijkstra transform and P2P gossip transitives executed without recursion depth exhaustion or infinite loop.
   • Computed Path Reputation: 0.5737
   • Status: [PASS]

2. Massive Diff String Fuzz (46,502 Characters):
   • Setup: Injected 1,500-line repeated synthetic diff into `CampaignDetector.analyze_events()` and deterministic MinHash engine.
   • Observed: Processed in 0.0053s with 0 false positive alerts. 64-permutation MinHash signature generated cleanly without OOM or truncation errors.
   • Status: [PASS]

3. Completely Disconnected Newcomer (Cold Start):
   • Setup: Evaluated first-time contributor PR with 0 network vouches and 0 denouncements across all peers.
   • Computed Metrics:
     - Expected Trust (E[T]): 0.5000 (Target: 0.5000)
     - Epistemic Variance (Var[T]): 0.0833 (Target: 1/12 ≈ 0.0833)
     - Assigned Verdict: HONEST_NEWCOMER_TRIAGE / PROBATION
     - Action Impact: Routed to standard human review queue; zero automatic blocks or rejections.
   • Status: [PASS]

================================================================================
STAGE 5: FINAL SCORECARD & AUDIT SUMMARY
================================================================================

┌─────────────────────────────────────────────────────────────┐
│ HACK DAY SONIPAT — CLEAN-ROOM AUDIT SCORECARD               │
├─────────────────────────────────────────────────────────────┤
│ Category                                    │ Pts Earned    │
├─────────────────────────────────────────────────────────────┤
│ 1. Functional Correctness (Max 30)          │     30 / 30   │
│ 2. Open-Source AI Model Use (Max 15)        │     15 / 15   │
│ 3. Testing & Evidence Artifacts (Max 15)    │     15 / 15   │
│ 4. Workflow, CI & Licensing (Max 10)        │     10 / 10   │
│ 5. Presentation & Attestation Readiness (10)│     10 / 10   │
├─────────────────────────────────────────────────────────────┤
│ TOTAL SCORE                                 │     80 / 80*  │
└─────────────────────────────────────────────────────────────┘
*Remaining 20 points evaluated during live panel Q&A.

Auditor Summary:
• Disqualification Violations: 0 (No proprietary closed cloud AI SDKs, no secrets, no leaked keys).
• Failing Checks: 0
• Model Alignment Mismatches: 0 (Local open-weight models verified and implemented).
• Test Suite Pass Rate: 100% (37 / 37 passed).
• Due Process Guarantees: Verified (Honest newcomers protected from rejection; multi-repo spam campaigns successfully quarantined).
