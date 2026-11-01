# TrustMesh Architecture & Design Specification

> **Hacktoberfest 2026 Hack Day — Problem 07**  
> *TrustMesh utilizes a hybrid architecture: a deterministic, cryptographic Web-of-Trust graph for peer consensus and Bayesian newcomer triage, augmented by a local, open-weight CPU embedding model (sentence-transformers/all-MiniLM-L6-v2) for spatiotemporal PR campaign clustering.*

---

## 1. Mathematical Foundations of Transitive Trust Propagation (A → B → C)

### 1.1 Direct Peer Declarations
In TrustMesh, trust is purely subjective and local. There is no global consensus, central ledger, or universal reputation score. Each project node $u$ defines its personal trust in peer projects $v \in \mathcal{P}$ by issuing signed `RecordKind.TRUST_PEER` records containing a declared weight $W(u \to v) \in [0.0, 1.0]$.

### 1.2 Path Trust and Hop Decay
When Project A evaluates Project C via an intermediary Project B:
1. **Edge Weight Product:** Trust along a path is multiplicative. If A trusts B with weight $W(A \to B) = 0.90$ and B trusts C with weight $W(B \to C) = 0.80$, the base product is $0.90 \times 0.80 = 0.72$.
2. **Hop Decay Factor ($0.70$):** Trust degrades as social distance increases. For every hop beyond the first direct link, an explicit attenuation factor of $\gamma = 0.70$ is applied. For path $A \to B \to C$ ($2$ hops):
   $$\text{Trust}(A \to C) = W_{\text{eff}}(A \to B) \times W_{\text{eff}}(B \to C) \times 0.70 = 0.90 \times 0.80 \times 0.70 = 0.5040$$
3. **Maximum Depth Bound (3 Hops):** Paths longer than 3 hops are discarded:
   $$\forall \text{path } P \text{ with } |P| > 3, \quad \text{Trust}(P) = 0.0$$
   This prevents distant, loose social networks from creating phantom trust across the ecosystem.
4. **Multiple Paths:** If multiple paths exist between $A$ and a target project $T$, $A$ selects the path that maximizes transitive trust:
   $$\text{Trust}(A \to T) = \max_{P \in \text{Paths}(A, T, \le 3)} \prod_{e=(u, v) \in P} W_{\text{eff}}(u \to v) \times \gamma^{\max(0, \text{len}(P) - 1)}$$

### 1.3 Fan-Out Dilution Conservation
A major vulnerability in naive transitive trust networks is "endorsement inflation": a node recklessly vouching for dozens of projects without due diligence. TrustMesh enforces **fan-out dilution**:
If a node $u$ declares trust in $K_u > 8$ peers, each outgoing edge is scaled by a conservation factor $\delta_u = \frac{8.0}{K_u}$:
$$W_{\text{eff}}(u \to v) = W(u \to v) \times \min\left(1.0, \frac{8.0}{K_u}\right)$$

For example, if Project B endorses 16 projects, its endorsement capacity per project is halved ($8/16 = 0.5$). If Project B endorses $\le 8$ projects, no dilution occurs ($\delta_u = 1.0$).

---

## 2. Preventing Malicious & Weaponized Denouncements

A decentralized reputation system must defend against griefing, false reports, competitor defamation, and rogue maintainers. TrustMesh implements four layers of protection:

### 2.1 Cryptographic Evidence Requirement
A denouncement record does not count on mere assertion. A `RecordKind.DENOUNCE` payload must include cited `pr_fingerprint` record IDs as immutable evidence.
Upon receipt, the evaluating node computes the **Evidence Factor** $E \in \{0.0, 1.0\}$:
* **Subject Match:** All cited fingerprints must belong to the subject accused.
* **Near-Duplicate Proof:** The receiver independently verifies that the cited PR fingerprints have a MinHash Jaccard similarity $\ge 0.65$ within a 48-hour window.
* **Local Verifiability:** If the cited PR fingerprints are missing from the receiver's local database or do not meet similarity thresholds, $E = 0.0$.

When $E = 0.0$, the effective negative weight of that denouncement collapses to zero:
$$w_{\text{neg}} = T_{\text{issuer}} \times D(t) \times R_{\text{issuer}} \times E = 0.0$$

### 2.2 Corroboration Requirement for BLOCK
A single project—no matter how highly trusted—can **never** unilaterally block a contributor across the network. A verdict of `BLOCK` is strictly restricted to two conditions:
1. **Own Project Direct Policy:** The evaluating maintainer's own node directly denounced the contributor.
2. **Corroborated Network Threshold:** At least **two independent trusted issuers** ($T \ge 0.50$) have active denouncements with verified evidence, their combined Noisy-OR negative weight meets $\text{neg} \ge 0.70$, and $\text{neg} > \text{pos}$.

If an uncorroborated claim is made by a trusted peer, the verdict is at most `FLAG` or `PROBATION`, preserving the contributor's ability to participate elsewhere.

### 2.3 Bayesian Reliability Penalty ($\text{Beta}(2, 1)$)
TrustMesh models each issuer's reporting credibility using a Bayesian $\text{Beta}(\alpha, \beta)$ prior:
* Prior: $\alpha_0 = 2.0, \beta_0 = 1.0 \implies E[\theta] = \frac{2}{3}$.
* For each denouncement issued:
  * If corroborated by other trusted peers or backed by verified duplicate evidence: $\alpha \leftarrow \alpha + 1.0$.
  * If uncorroborated and lacking verifiable evidence: $\beta \leftarrow \beta + 1.0$.
* Normalized reliability:
  $$R(\text{issuer}) = \min\left(1.0, \frac{\alpha}{\alpha + \beta} \times \frac{3}{2}\right)$$

A rogue maintainer issuing 5 uncorroborated accusations sees their reliability drop to:
$$R = \frac{2}{2 + 6} \times 1.5 = 0.375$$
Serial smearers rapidly neutralize their own voting power across the entire network.

### 2.4 Cryptographic Retraction
If a maintainer mistakenly denounces an innocent contributor, they can issue a `RecordKind.RETRACT` referencing the target record ID. When gossiped, all nodes instantly nullify the retracted record from Noisy-OR aggregation, immediately restoring the contributor's standing.

---

## 3. The Newcomer Path: Safety Without Rejection

Open source depends on welcoming first-time contributors. A common failure mode of trust systems is treating unknown accounts as guilty until proven innocent.

### 3.1 Guaranteed PROBATION Policy
When a contributor with no prior history in the network submits a PR, the evaluator's rule is absolute:
$$\text{No network records} \implies \text{Verdict} = \mathbf{PROBATION}$$
The contributor is **never rejected, blocked, or held**. Maintainers review their PR using standard code review without prejudice.

### 3.2 Distinguishing Typo Fixes from Coordinated Spreading
During Hacktoberfest, many newcomers begin by fixing a typo in documentation. Malicious botnets also fix typos in documentation. TrustMesh differentiates them using **network breadth and volume**:
* **Campaign Member Definition:** An account is classified as a campaign member **only if** it submits $\ge 3$ near-duplicate PRs across $\ge 3$ distinct projects within 48 hours.
* **Single-Project Exemption:** An honest newcomer submitting a typo fix to 1 or 2 repositories has $N_{\text{projects}} < 3$. They cannot be classified as a campaign member.
* **Substantive Code Exemption:** Any PR with $\ge 5$ additions or genuine feature code has `is_low_value = False`. Clusters without a low-value signal cannot be classified as spam campaigns.

### 3.3 The Organic Trust Accumulation Ladder
1. **First Contribution:** Newcomer arrives $\to$ `PROBATION`.
2. **First Merge:** Maintainer merges PR and optionally issues a `RecordKind.VOUCH` $\to$ `ALLOW`.
3. **Repeated Quality Contributions:** Multiple maintainers vouch $\to$ $\text{pos} \ge 0.60 \to$ `TRUST`.
4. **Exemption Guarantee:** Contributors with $\text{pos} \ge 0.60$ are permanently exempt from automated campaign `HOLD` actions.

---

## 4. Decentralization: No Central Authority, No Cloud

### 4.1 Set-Difference Gossip Protocol
TrustMesh runs entirely peer-to-peer. Nodes synchronize by exchanging record IDs:
1. Node A requests known record hashes from declared peers and random nodes: $\mathcal{H}_B$.
2. Node A computes the set difference: $\Delta = \mathcal{H}_B \setminus \mathcal{H}_A$.
3. Node A pulls only missing records $\Delta$ and ingests them in per-issuer chain order.
4. Information propagates through the network in $O(\log N)$ gossip rounds without any master coordinator, consensus beacon, or central database.

### 4.2 Content Addressing & Ed25519 Hash Chains
Every record is content-addressed via SHA-256:
$$\text{record\_id} = \text{SHA-256}(\text{canonical\_json}(\text{issuer}, \text{issuer\_key}, \text{kind}, \text{subject}, \text{ts}, \text{payload}, \text{prev}))$$
* **Immutability:** Signatures are computed with Ed25519 over deterministic canonical JSON. Any modification in payload or timestamp breaks the signature.
* **Anti-Forking:** Each issuer maintains a strict monotonic hash chain where $\text{rec}_i.\text{prev} = \text{rec}_{i-1}.\text{record\_id}$. Backdating or deleting past records is cryptographically impossible.
* **Key Pinning on First Sight (TOFU):** When an issuer name is first observed, its public key is pinned. Any subsequent record claiming the same name with a different key is rejected immediately as key impersonation.

---

## 5. Why AI-Text Detection Alone is Fundamentally Insufficient

A common proposal for Hacktoberfest spam is using Large Language Models (LLMs) or neural text classifiers to detect "AI-generated" or "low-quality" PR text. TrustMesh utilizes a hybrid architecture: a deterministic, cryptographic Web-of-Trust graph for peer consensus and Bayesian newcomer triage, augmented by a local, open-weight CPU embedding model (sentence-transformers/all-MiniLM-L6-v2) for spatiotemporal PR campaign clustering. Here is why closed AI-text detectors are avoided:

### 5.1 Fragility in the Adversarial LLM Arms Race
Probabilistic classifiers (like Perplexity or RoBERTa detectors) look for statistical regularity in text. Spammers trivially bypass them by:
* Adding slight typographical errors.
* Paraphrasing templates via few-shot prompting.
* Mixing human snippets with bot templates.
A system reliant on AI detection forces maintainers into an expensive, never-ending adversarial arms race.

### 5.2 Discrimination Against Non-Native English Speakers
Empirical studies consistently show that AI-text detectors exhibit severe bias against non-native English speakers. Standardized grammatical phrasing, simpler vocabulary, and formulaic PR descriptions are disproportionately misclassified as "machine-generated." Open source must remain globally accessible; banning contributors based on linguistic style is unacceptable.

### 5.3 Lack of Cryptographic Accountability & Auditability
In a decentralized trust network, verdicts must be verifiable by independent third parties:
* If Project A tells Project B that an account is blocked, B must be able to verify the cryptographic signatures and deterministic math.
* An AI model's output cannot be verified: weights change across versions, model inference is non-deterministic or closed-source, and a neural probability score ($0.87$) provides no verifiable evidence of wrongdoing.

### 5.4 The TrustMesh Alternative: Structural & Temporal Fingerprinting
Instead of guessing whether text is "AI-generated," TrustMesh analyzes **deterministic structural invariants**:
1. **MinHash + LSH (64 Permutations):** Collapses synonym variations deterministically.
2. **Multi-Repo Burst Detection:** Spammers must spread widely ($\ge 3$ projects in 48h) to achieve scale.
3. **Behavioral Diff Metrics:** Evaluates low-value diff ratios and account age.
4. **Decentralized Corroboration:** Requires multiple independent maintainers to verify duplicate artifacts.

This approach is 100% deterministic, transparent, explainable in open court or open-source governance, and runs in milliseconds without GPU hardware or external API calls.

