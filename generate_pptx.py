import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_DARK = RGBColor(15, 23, 42)        # Slate 900
    CARD_DARK = RGBColor(30, 41, 59)      # Slate 800
    BORDER_DARK = RGBColor(51, 65, 85)    # Slate 700
    TEXT_WHITE = RGBColor(248, 250, 252)  # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
    ACCENT_BLUE = RGBColor(59, 130, 246)  # Blue 500
    ACCENT_CYAN = RGBColor(6, 182, 212)   # Cyan 500
    ACCENT_GREEN = RGBColor(16, 185, 129) # Emerald 500
    ACCENT_RED = RGBColor(239, 68, 68)    # Red 500
    ACCENT_AMBER = RGBColor(245, 158, 11) # Amber 500
    ACCENT_PURPLE = RGBColor(139, 92, 246)# Violet 500
    TERM_DARK = RGBColor(13, 17, 23)      # Terminal Black

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.color.rgb = BG_DARK
        return bg

    def add_header(slide, title, category="HACK DAY SONIPAT — PROBLEM 07"):
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.75))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(25)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_window(slide, left, top, width, height, title=None, border_color=BORDER_DARK, bg_color=CARD_DARK):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        # macOS traffic lights
        dot_r = Inches(0.12)
        dot_y = top + Inches(0.14)
        c_red = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.2), dot_y, dot_r, dot_r)
        c_red.fill.solid(); c_red.fill.fore_color.rgb = ACCENT_RED; c_red.line.color.rgb = ACCENT_RED
        c_yellow = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.38), dot_y, dot_r, dot_r)
        c_yellow.fill.solid(); c_yellow.fill.fore_color.rgb = ACCENT_AMBER; c_yellow.line.color.rgb = ACCENT_AMBER
        c_green = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.56), dot_y, dot_r, dot_r)
        c_green.fill.solid(); c_green.fill.fore_color.rgb = ACCENT_GREEN; c_green.line.color.rgb = ACCENT_GREEN

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.8), top + Inches(0.08), width - Inches(1.0), Inches(0.38))
            p = tb.text_frame.paragraphs[0]
            p.text = title
            p.font.name = "Arial"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_MUTED

        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE (TEAM CHECK_ALL_IN PRESENTS)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)

    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_CYAN
    bar.line.color.rgb = ACCENT_CYAN

    add_window(s1, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.6), title="Check_All_In — Terminal Launch Window", bg_color=CARD_DARK, border_color=BORDER_DARK)

    # Team Name Badge
    tb_badge = s1.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10), Inches(0.4))
    p = tb_badge.text_frame.paragraphs[0]
    p.text = "HACK DAY SONIPAT  •  PROBLEM STATEMENT 07  •  MLH"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # Team Check_All_In Presents
    tb_team_pres = s1.shapes.add_textbox(Inches(1.5), Inches(1.85), Inches(10), Inches(0.5))
    p = tb_team_pres.text_frame.paragraphs[0]
    p.text = "TEAM CHECK_ALL_IN  PRESENTS"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    # Title
    tb_main = s1.shapes.add_textbox(Inches(1.5), Inches(2.25), Inches(10), Inches(1.2))
    p = tb_main.text_frame.paragraphs[0]
    p.text = "TrustMesh"
    p.font.name = "Arial"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # Subtitle
    tb_tag = s1.shapes.add_textbox(Inches(1.5), Inches(3.4), Inches(10.2), Inches(0.8))
    tf = tb_tag.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Decentralized Trust & Reputation Network for Open Source Contributions"
    p.font.name = "Arial"
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p2 = tf.add_paragraph()
    p2.text = "Multi-Hop Web-of-Trust  •  Asymmetric Smear Isolation  •  Local Open-Weight AI Triage  •  Production CLI Tool"
    p2.font.name = "Arial"
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED

    # Team Members Box
    add_window(s1, Inches(1.5), Inches(4.5), Inches(10.3), Inches(1.8), title="Check_All_In Members & Repositories", bg_color=TERM_DARK, border_color=BORDER_DARK)
    tb_gh = s1.shapes.add_textbox(Inches(1.7), Inches(4.8), Inches(9.9), Inches(1.4))
    tf_gh = tb_gh.text_frame
    tf_gh.word_wrap = True
    p = tf_gh.paragraphs[0]
    p.text = "TEAM CHECK_ALL_IN MEMBERS:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p_dev1 = tf_gh.add_paragraph()
    p_dev1.text = "• Dhruv Verma   • Prajan   • Mukul   • Akshit"
    p_dev1.font.name = "Arial"
    p_dev1.font.size = Pt(13)
    p_dev1.font.bold = True
    p_dev1.font.color.rgb = TEXT_WHITE

    p_repo = tf_gh.add_paragraph()
    p_repo.text = "• GitHub: github.com/dhruvv26420-jpg/TrustMesh (Problem 07 Submission)"
    p_repo.font.name = "Arial"
    p_repo.font.size = Pt(12)
    p_repo.font.color.rgb = ACCENT_GREEN

    # ==========================================
    # SLIDE 2: THE PROBLEM (WINDOWS / PANELS)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "The Open Source Trust Dilemma", "THE PROBLEM")

    cards_data_s2 = [
        ("1. Coordinated Sybil Spams", ACCENT_RED, [
            "Botnets & token farmers flood 30+ repositories with trivial typo pull requests.",
            "Consumes maintainer bandwidth with endless notification fatigue.",
            "Traditional single-repo spam filters cannot detect cross-repository bot bursts."
        ]),
        ("2. Malicious Smear Campaigns", ACCENT_AMBER, [
            "Adversarial or competitor nodes publish false denouncements and blacklists.",
            "Honest contributors risk being unfairly blocked across git ecosystems.",
            "Zero cryptographic defense against coordinated smear attacks in decentralized git."
        ]),
        ("3. The Newcomer Cold-Start Trap", ACCENT_PURPLE, [
            "Naive zero-trust algorithms treat zero past history as zero trust (0.0).",
            "Genuine first-time developers get auto-quarantined or gated behind friction.",
            "Lacks a formal way to separate epistemic uncertainty from confirmed malice."
        ])
    ]

    col_w = Inches(3.68)
    gap = Inches(0.33)
    start_x = Inches(0.8)

    for i, (title, color, bullets) in enumerate(cards_data_s2):
        x = start_x + i * (col_w + gap)
        add_window(s2, x, Inches(1.6), col_w, Inches(5.3), title=title, border_color=color)
        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(2.2), col_w - Inches(0.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        for b_idx, b in enumerate(bullets):
            p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
            p.text = f"•  {b}"
            p.font.name = "Arial"
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_WHITE
            p.space_after = Pt(16)

    # ==========================================
    # SLIDE 3: ARCHITECTURE & GITHUB CI/CD
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "TrustMesh Architecture & GitHub CI/CD Pipeline", "SYSTEM ARCHITECTURE")

    add_window(s3, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.3), title="4-Pillar Multi-Signal Defense Window", border_color=ACCENT_BLUE)
    tb_arch = s3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.6), Inches(4.5))
    tf = tb_arch.text_frame
    tf.word_wrap = True

    pils = [
        ("P1. Multi-Hop Web-of-Trust: ", "Transitive peering graph attenuation using Dijkstra negative-log transforms. Continuous product of trust edges: T = prod(w)."),
        ("P2. Asymmetric Smear Isolation: ", "Validates denouncer reputation. Untrusted negative claims are isolated into ignored lists and cannot degrade contributor reputation."),
        ("P3. Spatiotemporal PR Clustering: ", "2-hour sliding window embedding clustering using local all-MiniLM-L6-v2 on CPU. Quarantines multi-repo Sybil bursts."),
        ("P4. Bayesian Newcomer Triage: ", "Beta-Binomial conjugate update. Distinguishes epistemic variance from malice, routing cold-start developers to human review.")
    ]
    for i, (head, desc) in enumerate(pils):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{head}{desc}"
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)

    add_window(s3, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.3), title=".github/workflows/trustmesh.yml (Action Window)", border_color=ACCENT_GREEN, bg_color=TERM_DARK)
    tb_gh_wf = s3.shapes.add_textbox(Inches(7.3), Inches(2.2), Inches(5.0), Inches(4.5))
    tf_gw = tb_gh_wf.text_frame
    tf_gw.word_wrap = True

    p = tf_gw.paragraphs[0]
    p.text = "Drop-in GitHub Action (.github/workflows/trustmesh.yml):"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)

    gh_code = [
        "name: TrustMesh PR Evaluation",
        "on: [pull_request_target]",
        "jobs:",
        "  audit:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - name: Evaluate Contributor Trust",
        "        run: |",
        "          trustmesh audit \\",
        "            --network .trustmesh/network.json \\",
        "            --events ${{ github.event_path }} \\",
        "            --inspecting-repo ${{ github.repository }}",
        "      - name: Post OpenVEX Attestation",
        "        uses: trustmesh/comment-action@v1"
    ]
    for line in gh_code:
        p_c = tf_gw.add_paragraph()
        p_c.text = line
        p_c.font.name = "Courier New"
        p_c.font.size = Pt(10)
        p_c.font.color.rgb = RGBColor(187, 247, 208) if "trustmesh" in line else TEXT_WHITE

    # ==========================================
    # SLIDE 4: PILLAR 1 - WEB OF TRUST GRAPH
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "Pillar 1: Multi-Hop Peering & Attenuation Graph", "GRAPH THEORY")

    add_window(s4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), title="Mathematical Formulation Window", border_color=ACCENT_BLUE)
    tb_left = s4.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb_left.text_frame
    tf.word_wrap = True

    pts_s4 = [
        ("Directed Graph Peering: ", "Repositories register bilateral trust edges with weights w in [0.0, 1.0]."),
        ("Negative Log Transformation: ", "To calculate lowest-attenuation paths, weights are mapped via d(u, v) = -ln(w)."),
        ("Optimal Path Multiplication: ", "Dijkstra shortest path on d(u, v) minimizes sum(-ln w), maximizing product of weights:"),
        ("T(A, B) = prod(w_uv): ", "Preserves continuous multiplicative attenuation across arbitrary hops."),
        ("Vouch Propagation: ", "Effective contributor trust is: effective_trust = max(T(Inspecting, P) * confidence).")
    ]
    for i, (head, body) in enumerate(pts_s4):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {head}{body}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)

    add_window(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), title="Interactive Peering Topology Window", border_color=ACCENT_CYAN)
    tb_topo = s4.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf_top = tb_topo.text_frame
    tf_top.word_wrap = True

    net_nodes = [
        ("Inspecting Node: ", "Your-Project (The evaluating repository)"),
        ("Peered Upstream (0.95): ", "Project-B  ──>  Vouches for @alice_vouched (0.90)"),
        ("Security Partner (0.90): ", "Project-C  ──>  Denounces @dan_denounced (0.92)"),
        ("Untrusted Node (0.00): ", "Project-X  ──>  Denounces @charlie_newbie (ISOLATED)"),
        ("Effective Vouch Result: ", "T(Your-Project, @alice) = 0.95 * 0.90 = 0.855 -> ALLOW"),
        ("Zero Central Coordinator: ", "Calculated entirely locally via Dijkstra shortest-path decay.")
    ]
    for i, (h, b) in enumerate(net_nodes):
        p = tf_top.paragraphs[0] if i == 0 else tf_top.add_paragraph()
        p.text = f"✔ {h}{b}"
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

    # ==========================================
    # SLIDE 5: PILLAR 2 - ASYMMETRIC NEGATIVE ISOLATION
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "Pillar 2: Asymmetric Negative Isolation (Smear Defense)", "ADVERSARIAL RESILIENCE")

    add_window(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), title="The Sybil Smear Vulnerability Window", border_color=ACCENT_RED)
    tb_l5 = s5.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb_l5.text_frame
    tf.word_wrap = True
    l5_text = [
        "In naive reputation systems, a single negative claim or blacklist entry can destroy a developer's standing.",
        "Attack Vector: Malicious rogue project (Project-X) spins up and issues false denouncements (severity: 1.0) against honest developers.",
        "Without isolation, malicious entities weaponize reputation systems to censor competitors or extort contributors.",
        "Traditional solutions require centralized KYC or dispute councils — defeating decentralization."
    ]
    for i, t in enumerate(l5_text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"✗  {t}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(14)

    add_window(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), title="TrustMesh Asymmetric Defense Window", border_color=ACCENT_GREEN)
    tb_r5 = s5.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf_r5 = tb_r5.text_frame
    tf_r5.word_wrap = True
    r5_text = [
        "Subjective Validation: When evaluating Contributor C, Project A first checks its own trust in the denouncing project X: T(A, X).",
        "Threshold Check: If T(A, X) < 0.50, denouncement is isolated into 'denouncements_ignored'.",
        "Neutralization: Untrusted claims CANNOT unilaterally degrade a contributor's reputation or block PRs.",
        "Verified Accountability: If a trusted peer (T(A, C) >= 0.50) denounces with evidence, it is applied into 'denouncements_applied' -> QUARANTINE."
    ]
    for i, t in enumerate(r5_text):
        p = tf_r5.paragraphs[0] if i == 0 else tf_r5.add_paragraph()
        p.text = f"✔  {t}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(14)

    # ==========================================
    # SLIDE 6: PILLAR 3 - SPAM SCATTER PLOT
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "Pillar 3: Spatiotemporal Spam Campaign Detector", "LOCAL OPEN-WEIGHT AI")

    cards_s6 = [
        ("Spatiotemporal Sliding Window", ACCENT_CYAN, [
            "Partitions PR streams into 2-hour sliding windows (Δt <= 7200s).",
            "Builds temporal-semantic graph connecting submissions with high similarity and low time delta.",
            "Eliminates false alarms on spread-out recurring maintenance commits."
        ]),
        ("Local 384D Vector Embeddings", ACCENT_BLUE, [
            "sentence-transformers/all-MiniLM-L6-v2 running 100% locally on CPU.",
            "Sub-50ms latency, zero cloud API calls, zero credential risk.",
            "Deterministic TF-IDF n-gram fallback guarantees 100% offline availability."
        ]),
        ("Multi-Repo Dispersion Heuristic", ACCENT_PURPLE, [
            "Requires cluster size >= 4, repository dispersion >= 3 distinct targets.",
            "Checks newcomer account age (<= 7 days).",
            "Synthesizes deterministic campaign signature (e.g., camp_3b8f102) to quarantine entire bot fleets."
        ])
    ]

    for i, (title, color, bullets) in enumerate(cards_s6):
        x = start_x + i * (col_w + gap)
        add_window(s6, x, Inches(1.6), col_w, Inches(5.3), title=title, border_color=color)
        tb = s6.shapes.add_textbox(x + Inches(0.2), Inches(2.2), col_w - Inches(0.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        for b_idx, b in enumerate(bullets):
            p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
            p.text = f"•  {b}"
            p.font.name = "Arial"
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_WHITE
            p.space_after = Pt(16)

    # ==========================================
    # SLIDE 7: PILLAR 4 - BAYESIAN DENSITY CURVES
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "Pillar 4: Bayesian Cold-Start Triage & Beta Density Curves", "PROBABILISTIC INFERENCE")

    add_window(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), title="Beta-Binomial Conjugate Model Window", border_color=ACCENT_PURPLE)
    tb_l7 = s7.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb_l7.text_frame
    tf.word_wrap = True
    l7_pts = [
        ("Conjugate Update: ", "alpha = alpha_0 + w_vouch,  beta = beta_0 + w_denounce."),
        ("Prior State: ", "Uninformative Laplace prior Beta(1.0, 1.0) represents complete prior neutrality."),
        ("Expected Trust: ", "E[T] = alpha / (alpha + beta). With 0 history, E[T] = 0.50."),
        ("Epistemic Uncertainty: ", "Var(T) = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))."),
        ("Cold-Start Variance: ", "With zero history, Var(T) = 1/12 = 0.0833 (Maximum entropy).")
    ]
    for i, (head, body) in enumerate(l7_pts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {head}{body}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(14)

    add_window(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), title="Probability Density Distribution Shifts Window", border_color=ACCENT_AMBER)
    tb_r7 = s7.shapes.add_textbox(Inches(7.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf_r7 = tb_r7.text_frame
    tf_r7.word_wrap = True
    r7_pts = [
        ("Cold-Start Newcomer [Beta(1, 1)]: ", "Flat probability density across [0, 1]. High variance (0.0833). Signals UNCERTAINTY, NOT malice. Routed to maintainer review."),
        ("Verified Vouched Contributor [Beta(9, 1)]: ", "Sharp, right-skewed peak centered around 0.90. Low variance. Fast-tracked for automated merge."),
        ("Coordinated Sybil Bot [Beta(1, 13)]: ", "Severe left-skewed density collapsed against 0.0. Instant quarantine."),
        ("OpenVEX Attestation: ", "Generates machine-readable justification explaining the non-exclusionary classification.")
    ]
    for i, (head, body) in enumerate(r7_pts):
        p = tf_r7.paragraphs[0] if i == 0 else tf_r7.add_paragraph()
        p.text = f"✔ {head}{body}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(14)

    # ==========================================
    # SLIDE 8: GITHUB PR REVIEW BOT SIMULATION
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "Simulated GitHub Pull Request Review UI", "GITHUB INTEGRATION")

    add_window(s8, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.3), title="GitHub Pull Request #104 Window (decentralized-mesh/core)", bg_color=TERM_DARK, border_color=BORDER_DARK)

    gh_cases = [
        ("@alice_vouched", "ALLOW_VOUCHED", ACCENT_GREEN, "✔ Fast-Track Merge Approved", [
            "WoT Status: VERIFIED (0.855)",
            "Vouch: Project-B -> @alice",
            "Spam Scan: CLEAN (0 clusters)",
            "GitHub Action: PASS (Check 104)"
        ]),
        ("@dan_denounced", "QUARANTINE_DENOUNCED", ACCENT_RED, "✖ Blocked: Malicious Peer Denouncement", [
            "WoT Status: DENOUNCED",
            "Peer: Project-C confirmed attack",
            "Payload: Supply-chain curl pipe",
            "GitHub Action: FAIL (Check 105)"
        ]),
        ("@sybil_bot_014", "QUARANTINE_CAMPAIGN", ACCENT_PURPLE, "✖ Quarantined: Coordinated Bot Burst", [
            "Cluster: camp_3b8f102",
            "Dispersion: 38 distinct repos",
            "Diff: 99.2% typo overlap",
            "GitHub Action: AUTO-DISMISS"
        ]),
        ("@charlie_newbie", "HONEST_NEWCOMER_TRIAGE", ACCENT_AMBER, "⚠ Routed to Human Review Queue", [
            "Cold-Start: Zero prior vouches",
            "Smear: Project-X denouncement ISOLATED",
            "Fairness: Epistemic Var 0.0833",
            "GitHub Action: TRIAGE REQUIRED"
        ])
    ]

    pr_col_w = Inches(2.7)
    pr_gap = Inches(0.18)
    pr_start_x = Inches(1.1)

    for i, (author, verdict, color, action_head, details) in enumerate(gh_cases):
        x = pr_start_x + i * (pr_col_w + pr_gap)
        add_window(s8, x, Inches(2.4), pr_col_w, Inches(4.2), title=author, border_color=color, bg_color=CARD_DARK)

        tb_box = s8.shapes.add_textbox(x + Inches(0.15), Inches(2.9), pr_col_w - Inches(0.3), Inches(3.5))
        tf_b = tb_box.text_frame
        tf_b.word_wrap = True

        p_v = tf_b.paragraphs[0]
        p_v.text = verdict
        p_v.font.name = "Arial"
        p_v.font.size = Pt(11)
        p_v.font.bold = True
        p_v.font.color.rgb = color
        p_v.space_after = Pt(4)

        p_a = tf_b.add_paragraph()
        p_a.text = action_head
        p_a.font.name = "Arial"
        p_a.font.size = Pt(10)
        p_a.font.bold = True
        p_a.font.color.rgb = TEXT_WHITE
        p_a.space_after = Pt(8)

        for d in details:
            p_d = tf_b.add_paragraph()
            p_d.text = f"• {d}"
            p_d.font.name = "Courier New"
            p_d.font.size = Pt(9)
            p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: WHAT IT DOES IN THE END - THE TOOL PART!
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "What It Does: The TrustMesh Interactive CLI Tool", "THE TOOL IN PRACTICE")

    # Left: What It Does in 3 Steps
    add_window(s9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3), title="Production Workflow: Ingestion to Merge", border_color=ACCENT_CYAN)
    tb_tool_desc = s9.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.1), Inches(4.5))
    tf_td = tb_tool_desc.text_frame
    tf_td.word_wrap = True

    tool_steps = [
        ("1. PR Ingestion: ", "CLI ingests pull request events directly from GitHub Webhooks or local JSON streams with diff contents and metadata."),
        ("2. Sub-250ms Multi-Signal Audit: ", "Executes WoT graph traversal + CPU vector clustering (all-MiniLM-L6-v2) + Bayesian conjugate update completely locally."),
        ("3. Deterministic Verdicts: ", "Emits ALLOW_VOUCHED, QUARANTINE_DENOUNCED, QUARANTINE_CAMPAIGN, or HONEST_NEWCOMER_TRIAGE."),
        ("4. Automated GitHub Enforcement: ", "Sets commit status checks, posts OpenVEX-compliant attestations, and auto-dismisses coordinated Sybil spam bursts."),
        ("5. Zero Maintenance Overhead: ", "Maintainers regain 80%+ of time lost to typo spam without risking exclusion of honest new contributors.")
    ]
    for i, (h, b) in enumerate(tool_steps):
        p = tf_td.paragraphs[0] if i == 0 else tf_td.add_paragraph()
        p.text = f"{h}{b}"
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)

    # Right: Live Terminal Window
    add_window(s9, Inches(6.7), Inches(1.6), Inches(5.8), Inches(5.3), title="Terminal — trustmesh audit (CLI Session)", border_color=ACCENT_GREEN, bg_color=TERM_DARK)
    tb_term = s9.shapes.add_textbox(Inches(6.9), Inches(2.1), Inches(5.4), Inches(4.6))
    tf_t = tb_term.text_frame
    tf_t.word_wrap = True

    term_lines = [
        "$ trustmesh audit --network net.json --events prs.json",
        "============================================================",
        "  TrustMesh Audit Report — Evaluating for: Your-Project",
        "  Scanned: 120 total events | Auditing: 4 target submissions",
        "============================================================",
        "PR ID         │ Contributor     │ WoT │ Spam │ Verdict",
        "──────────────┼─────────────────┼─────┼──────┼──────────────",
        "pr_alice_001  │ alice_vouched   │ YES │ CLR  │ ALLOW_VOUCHED",
        "pr_dan_002    │ dan_denounced   │ NO  │ CLR  │ QUARANTINE_DEN",
        "pr_spam_014   │ sybil_bot_014   │ NO  │ HIT  │ QUARANTINE_CAM",
        "pr_charlie_004│ charlie_newbie  │ NO  │ CLR  │ HONEST_TRIAGE",
        "────────────────────────────────────────────────────────────",
        "✔ Summary: 1 Fast-Track | 1 Triage | 2 Quarantines",
        "✔ Exported OpenVEX Attestation -> audit_output.json"
    ]
    for line in term_lines:
        p = tf_t.add_paragraph()
        p.text = line
        p.font.name = "Courier New"
        p.font.size = Pt(9.5)
        if "ALLOW" in line or line.startswith("$"):
            p.font.color.rgb = ACCENT_GREEN
        elif "QUARANTINE" in line:
            p.font.color.rgb = ACCENT_RED
        elif "HONEST" in line:
            p.font.color.rgb = ACCENT_AMBER
        elif line.startswith("="):
            p.font.color.rgb = ACCENT_CYAN
        else:
            p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 10: CONCLUSION & SUMMARY
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)

    bar10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar10.fill.solid()
    bar10.fill.fore_color.rgb = ACCENT_GREEN
    bar10.line.color.rgb = ACCENT_GREEN

    add_window(s10, Inches(1.0), Inches(1.1), Inches(11.333), Inches(5.3), title="Check_All_In — Closing Remarks & Impact Window", bg_color=CARD_DARK, border_color=ACCENT_BLUE)

    tb_end = s10.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.333), Inches(4.6))
    tf = tb_end.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Why Check_All_In & TrustMesh Win Problem 07"
    p.font.name = "Arial"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    concl_points = [
        ("Decentralized by Design: ", "Operates across GitHub, GitLab, and Radicle without global consensus bottlenecks or token speculation."),
        ("Mathematically Grounded: ", "Pairs Dijkstra negative-log shortest path decay with Beta-Binomial Bayesian conjugate inference."),
        ("Smear-Proof & Inclusive: ", "Asymmetric Negative Isolation neutralizes rogue attacks while Bayesian triage welcomes newcomers."),
        ("Native GitHub CI/CD Action: ", "Maintainers add 1 workflow file (.github/workflows/trustmesh.yml) to guard their repositories in seconds."),
        ("Production CLI & Engine: ", "Zero-cloud local AI models, comprehensive pytest suite, CLI tool, and OpenVEX machine-readable output.")
    ]
    for i, (head, body) in enumerate(concl_points):
        p = tf.add_paragraph()
        p.text = f"•  {head}{body}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(8)

    p_final = tf.add_paragraph()
    p_final.text = "Team Check_All_In: Dhruv Verma, Prajan, Mukul, Akshit  •  GitHub: github.com/dhruvv26420-jpg/TrustMesh"
    p_final.font.name = "Arial"
    p_final.font.size = Pt(15)
    p_final.font.bold = True
    p_final.font.color.rgb = ACCENT_CYAN
    p_final.space_before = Pt(16)

    out_path = Path("/Users/dhruvverma/.gemini/antigravity/scratch/trustmesh/trustmesh_presentation.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_deck()
