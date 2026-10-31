# Hack Day Sonipat — Project Overview

## Team Details
- **Team Name**: Check_All_In
- **Team Members**:
  - Dhruv Verma
  - Prajan Radhakrishnan 
  - Mukul
  - Akshit Kumar

## Selected Problem Statement
**Problem 07 — Decentralized Trust Network for Open Source Contributions**

### Summary of Problem & Solution

#### The Challenge
The advent of AI-assisted development tools has drastically lowered the barrier to generating code, pull requests, and issue reports. Consequently, open-source maintainers face high volumes of coordinated low-quality submissions and automated spam campaigns spanning hundreds of repositories simultaneously. Because individual project maintainers review incoming PRs in silos, cross-repository attack patterns remain invisible to them. At the same time, relying on a centralized reputation authority introduces single points of failure, censorship risks, and vendor lock-in, while naive reputation scoring risks unfairly excluding legitimate newcomers who lack prior track records.

#### Our Solution: TrustMesh
Built by **Team Check_All_In**, **TrustMesh** is a fully decentralized, peer-to-peer trust scoring and reputation network designed specifically for open-source ecosystems:
- **Decentralized Web-of-Trust (WoT):** Projects maintain public, cryptographically signed (Ed25519) vouch and denouncement attestations, exchanging trust signals directly via peer-to-peer gossip without any central authority.
- **Fair Newcomer Triage (Bayesian Due Process):** Implements a Beta prior ($E[T] = 0.50$, variance $0.0833$) ensuring first-time contributors receive probation and human review rather than automated blocks or rejections.
- **Coordinated Campaign Detection:** Combines MinHash LSH fuzzy fingerprinting with local semantic embeddings to detect multi-project PR bursts and flag coordinated spam waves in real time.
- **Protection Against Malicious Denouncements:** Features transitive trust decay, fan-out dilution, and Bayesian serial-smearer penalties so uncorroborated or retaliatory accusations cannot damage legitimate contributors.

## AI Models & Technical Justification

In strict compliance with Hack Day Sonipat rules, all models are 100% open-source / open-weight and run locally without requiring closed cloud APIs or internet connectivity:

1. **`sentence-transformers/all-MiniLM-L6-v2`**
   - **Type**: Local Semantic Embedding Model (Sentence Transformers)
   - **Technical Justification**: Generates 384-dimensional dense semantic embeddings from commit messages, pull request descriptions, and code reviews. Enables semantic clustering of contribution topics, contributor domain specialization scoring, and semantic similarity comparison between past trusted contributions and incoming PRs. Operates locally on CPU with minimal memory footprint (~80MB) and sub-50ms inference latency.

2. **`Qwen/Qwen2.5-Coder-1.5B-Instruct`**
   - **Type**: Local Open-Weight Code Instruction LLM
   - **Technical Justification**: Lightweight open-weight language model optimized for code understanding and repository analysis. Runs locally via CPU/quantized runtime to evaluate PR risk factors, extract semantic metadata from code diffs, synthesize code review trust annotations, and detect adversarial or spam pull requests within the decentralized trust network without leaking proprietary or sensitive developer code to third-party cloud services.
