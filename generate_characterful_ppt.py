#!/usr/bin/env python3
"""
Generate a highly character-full, tactile paper-styled PowerPoint presentation (16:9)
that faithfully mirrors the TrustMesh website aesthetic, interactive engines,
mathematical proofs, storytelling personas, and hackathon presentation flair.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_characterful_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Character-Full Tactile Paper Palette
    BG_PAPER = RGBColor(251, 249, 244)       # #fbf9f4 Warm Cream Paper
    BG_PAPER_DARK = RGBColor(244, 239, 229)  # #f4efe5 Slightly darker paper
    CARD_WHITE = RGBColor(255, 255, 255)     # #ffffff Pure Paper White
    CARD_CREAM = RGBColor(248, 245, 238)     # #f8f5ee Warm Card
    SHADOW_COL = RGBColor(220, 213, 201)     # #dcd5c9 Tactile Paper Shadow
    BORDER_MAIN = RGBColor(226, 221, 211)    # #e2ddd3 Craft Paper Border
    BORDER_DARK = RGBColor(200, 193, 180)    # #c8c1b4 Deep Border

    # Typography Colors
    TEXT_CHARCOAL = RGBColor(27, 38, 59)     # #1b263b Deep Editorial Charcoal
    TEXT_MUTED = RGBColor(100, 116, 139)     # #64748b Slate Muted
    TEXT_DARK = RGBColor(15, 23, 42)         # #0f172a Near Black

    # Expressive Persona & Verdict Colors
    VERDICT_GREEN = RGBColor(22, 101, 52)    # #166534 Forest Green (ALLOW)
    VERDICT_GREEN_BG = RGBColor(236, 253, 245)# #ecfdf5 Light Green Card
    VERDICT_RED = RGBColor(185, 28, 28)      # #b91c1c Crimson Red (QUARANTINE)
    VERDICT_RED_BG = RGBColor(254, 242, 242)  # #fef2f2 Light Red Card
    VERDICT_AMBER = RGBColor(180, 83, 9)     # #b45309 Warm Amber (HONEST TRIAGE)
    VERDICT_AMBER_BG = RGBColor(255, 251, 235)# #fffbeb Light Amber Card
    VERDICT_INDIGO = RGBColor(67, 56, 202)   # #4338ca Royal Indigo (WoT/Ed25519)
    VERDICT_INDIGO_BG = RGBColor(238, 242, 255)# #eef2ff Light Indigo Card

    # Terminal Colors
    TERM_BG = RGBColor(13, 17, 23)           # #0d1117 GitHub Dark
    TERM_TEXT = RGBColor(240, 246, 252)      # #f0f6fc GitHub White
    DOT_RED = RGBColor(239, 68, 68)          # #ef4444
    DOT_YELLOW = RGBColor(245, 158, 11)      # #f59e0b
    DOT_GREEN = RGBColor(16, 185, 129)       # #10b981

    def add_paper_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_PAPER
        bg.line.fill.background()
        return bg

    def add_top_ribbon(slide, col=VERDICT_INDIGO):
        # Double layer top ribbon
        r1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.08))
        r1.fill.solid()
        r1.fill.fore_color.rgb = col
        r1.line.fill.background()

    def add_header(slide, title, category="HACK DAY SONIPAT — PROBLEM 07", subtitle=None, ribbon_col=VERDICT_INDIGO):
        add_top_ribbon(slide, ribbon_col)

        # Stamped Category Tag
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(3.4), Inches(0.32))
        tag.fill.solid()
        tag.fill.fore_color.rgb = CARD_CREAM
        tag.line.color.rgb = BORDER_MAIN
        tag.line.width = Pt(1)
        p_tag = tag.text_frame.paragraphs[0]
        p_tag.text = f"❖  {category.upper()}"
        p_tag.font.name = "Georgia"
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ribbon_col
        p_tag.alignment = PP_ALIGN.CENTER

        # Main Title (Serif Editorial)
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.65))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Georgia"
        p_title.font.size = Pt(25)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_CHARCOAL

        if subtitle:
            tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.7), Inches(0.4))
            p_sub = tb_sub.text_frame.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.name = "Calibri"
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_tactile_card(slide, left, top, width, height, bg_color=CARD_WHITE, border_color=BORDER_MAIN):
        # Layer 1: Drop Shadow for tactile paper depth
        shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.04), top + Inches(0.04), width, height)
        shadow.fill.solid()
        shadow.fill.fore_color.rgb = SHADOW_COL
        shadow.line.fill.background()

        # Layer 2: Main Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    def add_mac_window(slide, left, top, width, height, title="bash — 80x24", bg_col=TERM_BG):
        card = add_tactile_card(slide, left, top, width, height, bg_color=bg_col, border_color=CARD_WHITE)
        # Window Header
        hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.35))
        hdr.fill.solid()
        hdr.fill.fore_color.rgb = RGBColor(22, 27, 34)
        hdr.line.fill.background()

        # Traffic light dots
        dot_colors = [DOT_RED, DOT_YELLOW, DOT_GREEN]
        for idx, dc in enumerate(dot_colors):
            d = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.18 + idx * 0.22), top + Inches(0.11), Inches(0.12), Inches(0.12))
            d.fill.solid()
            d.fill.fore_color.rgb = dc
            d.line.fill.background()

        # Title
        tb = slide.shapes.add_textbox(left + Inches(0.9), top + Inches(0.05), width - Inches(1.8), Inches(0.28))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.name = "Courier New"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.alignment = PP_ALIGN.CENTER
        return card

    # =========================================================================
    # SLIDE 1: COVER / DOSSIER (Rich Tactile Personality)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s1)
    add_top_ribbon(s1, VERDICT_INDIGO)

    # Big Notebook / Dossier Card
    add_tactile_card(s1, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3), bg_color=CARD_WHITE)

    # Decorative Paper Header Ribbon inside card
    card_banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.15))
    card_banner.fill.solid()
    card_banner.fill.fore_color.rgb = VERDICT_INDIGO
    card_banner.line.fill.background()

    # Left Column: Story & Identity
    tb1_l = s1.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(7.4), Inches(5.6))
    tf1_l = tb1_l.text_frame
    tf1_l.word_wrap = True

    p = tf1_l.paragraphs[0]
    p.text = "❖  HACK DAY SONIPAT · PROBLEM 07 · TEAM CHECK_ALL_IN"
    p.font.name = "Georgia"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    p = tf1_l.add_paragraph()
    p.text = "TrustMesh: Decentralized Open-Source Trust Network"
    p.font.name = "Georgia"
    p.font.size = Pt(29)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.space_before = Pt(6)

    p = tf1_l.add_paragraph()
    p.text = "A Tactile Web Platform, 60fps HD Simulation Engine & Mathematical PR Audit Bench"
    p.font.name = "Georgia"
    p.font.size = Pt(14.5)
    p.font.color.rgb = VERDICT_AMBER
    p.space_before = Pt(4)

    p = tf1_l.add_paragraph()
    p.text = (
        "When AI-generated pull request spam floods open-source repositories during events like "
        "Hacktoberfest, maintainers face a brutal dilemma: drown in manual reviews or deploy naive "
        "reputation blocks that ban innocent newcomers. TrustMesh eliminates this dilemma with peer-to-peer "
        "cryptographic attestations, MinHash LSH campaign clustering, and Bayesian Laplace due process."
    )
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_CHARCOAL
    p.space_before = Pt(12)

    # Team Members Badges
    p = tf1_l.add_paragraph()
    p.text = "🛠️ Built by Team Check_All_In:"
    p.font.name = "Georgia"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.space_before = Pt(14)

    p = tf1_l.add_paragraph()
    p.text = "• Dhruv Verma   • Prajan Radhakrishnan   • Mukul   • Akshit Kumar"
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO
    p.space_before = Pt(4)

    p = tf1_l.add_paragraph()
    p.text = "🌐 Live Platform: https://dhruvv26420-jpg.github.io/Check_All_In/"
    p.font.name = "Courier New"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = VERDICT_GREEN
    p.space_before = Pt(8)

    # Right Column: Visual Stamp & Verified Seal
    seal_card = add_tactile_card(s1, Inches(9.0), Inches(1.1), Inches(3.2), Inches(5.4), bg_color=CARD_CREAM)
    tb1_r = s1.shapes.add_textbox(Inches(9.2), Inches(1.3), Inches(2.8), Inches(5.0))
    tf1_r = tb1_r.text_frame
    tf1_r.word_wrap = True

    p = tf1_r.paragraphs[0]
    p.text = "[ VERIFIED ATTESTATION ]"
    p.font.name = "Courier New"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO
    p.alignment = PP_ALIGN.CENTER

    p = tf1_r.add_paragraph()
    p.text = "INVARIANTS CERTIFIED"
    p.font.name = "Georgia"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(6)

    invariants = [
        ("⚖️ Due Process Prior", "Beta(1, 1) Laplace guarantee. Newcomers never auto-blocked."),
        ("🔒 Ed25519 Cryptography", "SHA-256 monotonic hash chains with key pinning."),
        ("🛡️ Negative Isolation", "Untrusted denouncements quarantined automatically."),
        ("⚡ MinHash 64-Perm", "O(1) candidate pairing detects multi-repo spam bursts."),
        ("🧠 100% Local AI", "all-MiniLM-L6-v2 on CPU. Zero cloud dependencies.")
    ]
    for h, b in invariants:
        p = tf1_r.add_paragraph()
        p.text = f"{h}: "
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: THE PROBLEM BATTLEFIELD (Storytelling Character)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s2)
    add_header(s2, "The Maintainer Battlefield: Chaos vs Due Process", "THE MOTIVATION",
               "Why naive reputation blocks break open source, and why decentralized trust is required.")

    # Left: The AI Spam Nightmare (Red Tinted Card)
    add_tactile_card(s2, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_color=VERDICT_RED_BG, border_color=VERDICT_RED)
    tb2_l = s2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.7))
    tf2_l = tb2_l.text_frame
    tf2_l.word_wrap = True

    p = tf2_l.paragraphs[0]
    p.text = "❌ The Status Quo Crisis:"
    p.font.name = "Georgia"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = VERDICT_RED

    bad_points = [
        ("Coordinated Bot Campaigns: ", "LLM-powered script kiddies generate hundreds of near-identical PRs across 50+ repositories in seconds."),
        ("Siloed Review Vulnerability: ", "Maintainer Alice rejects a spam PR in Repo A, but Maintainer Bob in Repo B has zero visibility and reviews it from scratch."),
        ("Innocent Newcomer Casualties: ", "Crude heuristics (e.g. 'block users with <5 commits') ban legitimate students and first-time contributors fixing typos."),
        ("Centralized Platform Silos: ", "Central reputation scores introduce single points of failure, censorship risks, and commercial vendor lock-in.")
    ]
    for head, body in bad_points:
        p = tf2_l.add_paragraph()
        p.text = f"• {head}"
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = VERDICT_RED
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # Right: The TrustMesh Solution (Green Tinted Card)
    add_tactile_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_color=VERDICT_GREEN_BG, border_color=VERDICT_GREEN)
    tb2_r = s2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.7))
    tf2_r = tb2_r.text_frame
    tf2_r.word_wrap = True

    p = tf2_r.paragraphs[0]
    p.text = "✔ The TrustMesh Paradigm:"
    p.font.name = "Georgia"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = VERDICT_GREEN

    good_points = [
        ("Peer-to-Peer Gossip Web: ", "Repositories exchange Ed25519-signed vouches directly. When one project detects a spam wave, all peers are immunized."),
        ("Bayesian Laplace Due Process: ", "Accounts with zero history start at E[T] = 0.50 with wide uncertainty—routing to human triage, NEVER auto-rejection."),
        ("MinHash LSH Campaign Detection: ", "Collapses synonym and paraphrased spam variants across repositories in real time without external cloud APIs."),
        ("Asymmetric Negative Isolation: ", "Rogue maintainers cannot smear honest contributors; hostile untrusted denouncements are quarantined harmlessly.")
    ]
    for head, body in good_points:
        p = tf2_r.add_paragraph()
        p.text = f"• {head}"
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = VERDICT_GREEN
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 3: THE LIVE WEBSITE OVERVIEW & EXPERIENCE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s3)
    add_header(s3, "Tactile Website Architecture & Live Demo", "WEB PLATFORM EXPERIENCE",
               "A handcrafted, responsive editorial interface designed for Hack Day Sonipat.")

    # 4 Cards mapping to the website zones
    zones = [
        ("01 · 60fps HD Canvas Animator",
         "1920×960 Interactive Visualizer",
         "Hardware-accelerated HTML5 canvas rendering 4 dynamic simulation modes: P2P WoT Gossip, MinHash Campaign Defense, Bayesian Cold-Start, and Cryptographic PR Reviews.",
         VERDICT_INDIGO, VERDICT_INDIGO_BG),
        ("02 · PR Audit Simulator Playground",
         "Live Contributor Testing Bench",
         "Simulates pull request evaluations across 4 distinct personas with instant cryptographic verdict badges: ALLOW_VOUCHED, QUARANTINE_DEN, QUARANTINE_CAM, and HONEST_TRIAGE.",
         VERDICT_GREEN, VERDICT_GREEN_BG),
        ("03 · Mathematical Proof Renderer",
         "KaTeX LaTeX Formulations",
         "Formal mathematical proofs rendered alongside every decision: Dijkstra path attenuation, Beta-Binomial conjugate distributions, and MinHash Jaccard collision formulas.",
         VERDICT_AMBER, VERDICT_AMBER_BG),
        ("04 · GitHub Open-Source Panel",
         "In-Browser Source Inspector",
         "Dark-mode GitHub-themed file explorer and syntax-highlighted code inspector covering all 10 core Python source files for judge and maintainer auditing.",
         TEXT_CHARCOAL, CARD_CREAM)
    ]

    for i, (title, subtitle, desc, col, bg_col) in enumerate(zones):
        zx = Inches(0.8 + (i % 2) * 5.95)
        zy = Inches(1.8 + (i // 2) * 2.65)
        add_tactile_card(s3, zx, zy, Inches(5.75), Inches(2.4), bg_color=bg_col, border_color=col)

        # Ribbon indicator
        rib = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, zx, zy, Inches(0.12), Inches(2.4))
        rib.fill.solid()
        rib.fill.fore_color.rgb = col
        rib.line.fill.background()

        tb = s3.shapes.add_textbox(zx + Inches(0.3), zy + Inches(0.15), Inches(5.25), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Georgia"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        p = tf.add_paragraph()
        p.text = subtitle
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED

        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 4: FEATURE 1 — 60FPS HD VIDEO ANIMATOR
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s4)
    add_header(s4, "Feature 1: Interactive 60fps HD Video Animator", "FEATURE 01: SIMULATION ENGINE",
               "Real-time visual telemetry illustrating cryptographic gossip, graph decay, and campaign clustering.")

    # Left: Explanation & Modes
    add_tactile_card(s4, Inches(0.8), Inches(1.8), Inches(5.3), Inches(5.1))
    tb4_l = s4.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.7), Inches(4.7))
    tf4 = tb4_l.text_frame
    tf4.word_wrap = True

    p = tf4.paragraphs[0]
    p.text = "4 Interactive Canvas Modes:"
    p.font.name = "Georgia"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    sim_modes = [
        ("Mode 1 · P2P WoT Attestation Gossip", "Ed25519-signed vouchers pulse across network hops. Transitive trust decays smoothly via Dijkstra negative-log weights."),
        ("Mode 2 · Coordinated Campaign Defense", "Spatiotemporal MinHash bursts illuminate in red. Cross-repo clustering quarantines the coordinated wave in under 1 second."),
        ("Mode 3 · Bayesian Cold-Start Triage", "First-time contributors enter with wide epistemic variance (Var=0.0833), routing safely to maintainer probation."),
        ("Mode 4 · Cryptographic Review & OpenVEX", "Verdicts are packaged into machine-readable signed OpenVEX attestation payloads for automated GitHub CI pipelines.")
    ]
    for sm_title, sm_desc in sim_modes:
        p = tf4.add_paragraph()
        p.text = f"▶ {sm_title}: "
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = sm_desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Photo Frame with Embedded Screenshot
    crop_video_path = Path("/tmp/crop_video_player.png")
    if crop_video_path.exists():
        add_tactile_card(s4, Inches(6.4), Inches(1.8), Inches(6.1), Inches(5.1), bg_color=CARD_CREAM)
        s4.shapes.add_picture(str(crop_video_path), Inches(6.55), Inches(2.1), width=Inches(5.8))
        tb_cap = s4.shapes.add_textbox(Inches(6.55), Inches(6.35), Inches(5.8), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live 1920×960 HD Video Animator embedded in the website with speed & mode controls"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10.5)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: FEATURE 2 — THE 4 STORYTELLING PERSONAS (Character-Full!)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s5)
    add_header(s5, "Feature 2: The 4 Contributor Personas & Audit Simulator", "FEATURE 02: PULL REQUEST AUDIT",
               "How TrustMesh evaluates incoming pull requests using real-world contributor personas.")

    # 4 Expressive Persona Cards
    personas = [
        ("👩‍💻 Alice: Trusted Contributor", "ALLOW_VOUCHED", VERDICT_GREEN, VERDICT_GREEN_BG,
         "PR #101: Fix memory leak in connection pool",
         "Web-of-Trust path: 2 hops (Weight 0.85). Vouched by Repo B and Repo C. Fast-tracked directly to maintainer review."),

        ("🦹 Dan: Malicious Actor", "QUARANTINE_DEN", VERDICT_RED, VERDICT_RED_BG,
         "PR #202: Add hidden telemetry logging",
         "Corroborated denouncements backed by concrete near-duplicate fingerprints. Negative isolation protects from retaliatory smears."),

        ("🤖 Sybil Botnet #14", "QUARANTINE_CAM", VERDICT_RED, VERDICT_RED_BG,
         "PR #303: Automated spam PR wave across 12 repos",
         "MinHash LSH hit: Jaccard similarity >= 0.85 within 600 seconds. Cross-repo campaign flag quarantines entire cluster instantly."),

        ("🌱 Charlie: Honest Newcomer", "HONEST_NEWCOMER_TRIAGE", VERDICT_AMBER, VERDICT_AMBER_BG,
         "PR #404: Fix typo in documentation README",
         "Bayesian Laplace prior E[T]=0.50, Variance=0.0833. First-time contributor is never auto-blocked; routed to gentle probation review.")
    ]

    for i, (p_name, badge, badge_col, bg_col, pr_title, desc) in enumerate(personas):
        px = Inches(0.8 + (i % 2) * 5.95)
        py = Inches(1.8 + (i // 2) * 2.65)
        add_tactile_card(s5, px, py, Inches(5.75), Inches(2.4), bg_color=bg_col, border_color=badge_col)

        tb = s5.shapes.add_textbox(px + Inches(0.3), py + Inches(0.15), Inches(5.15), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = p_name
        p.font.name = "Georgia"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL

        # Verdict badge callout
        p_badge = tf.add_paragraph()
        p_badge.text = f"VERDICT: [ {badge} ]"
        p_badge.font.name = "Courier New"
        p_badge.font.size = Pt(10.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = badge_col
        p_badge.space_before = Pt(3)

        p_pr = tf.add_paragraph()
        p_pr.text = f"Contribution: {pr_title}"
        p_pr.font.name = "Calibri"
        p_pr.font.size = Pt(10.5)
        p_pr.font.bold = True
        p_pr.font.color.rgb = TEXT_CHARCOAL
        p_pr.space_before = Pt(4)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = "Calibri"
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = TEXT_MUTED
        p_desc.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: FEATURE 3 — MATHEMATICAL RIGOR & LATEX PROOFS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s6)
    add_header(s6, "Feature 3: Mathematical Foundations & LaTeX Engine", "FEATURE 03: FORMAL PROOFS",
               "Every verdict is mathematically justified through probabilistic inference and graph theory.")

    # Left: The 4 mathematical pillars
    add_tactile_card(s6, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1))
    tb6_l = s6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.9), Inches(4.7))
    tf6_l = tb6_l.text_frame
    tf6_l.word_wrap = True

    p = tf6_l.paragraphs[0]
    p.text = "Formal Mathematical Formulations:"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    math_pillars = [
        ("1. Transitive Decay (Dijkstra)",
         "T_eff(u -> v) = exp( - sum e_i )",
         "Attenuates trust along multi-hop paths via negative log-probabilities. Eliminates trust loops and bounds sybil reach."),
        ("2. Laplace Cold-Start Prior",
         "E[T] = alpha / (alpha + beta) = 0.50,  Var = 0.0833",
         "Prior Beta(1, 1) guarantees new contributors are never blocked automatically. Epistemic variance forces honest probation."),
        ("3. MinHash LSH Campaign Detection",
         "P( h_i(A) = h_i(B) ) = J(A, B) >= 0.85",
         "64-permutation MinHash banded into b=16, r=4. Identifies near-duplicate PR spam bursts in O(1) time across repos."),
        ("4. Asymmetric Negative Isolation",
         "T_penalized = T * Beta(alpha_acc, beta_acc)",
         "Uncorroborated hostile accusations are quarantined into denouncements_ignored without poisoning contributor standing.")
    ]
    for m_title, m_form, m_desc in math_pillars:
        p = tf6_l.add_paragraph()
        p.text = f"{m_title}"
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(6)

        p_f = tf6_l.add_paragraph()
        p_f.text = f"   {m_form}"
        p_f.font.name = "Courier New"
        p_f.font.size = Pt(10)
        p_f.font.bold = True
        p_f.font.color.rgb = VERDICT_INDIGO

        p_d = tf6_l.add_paragraph()
        p_d.text = f"   {m_desc}"
        p_d.font.name = "Calibri"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Photo Frame with Cropped Verdict LaTeX Screenshot
    crop_verdict_path = Path("/tmp/crop_verdicts_detail.png")
    if crop_verdict_path.exists():
        add_tactile_card(s6, Inches(6.6), Inches(1.8), Inches(5.9), Inches(5.1), bg_color=CARD_CREAM)
        s6.shapes.add_picture(str(crop_verdict_path), Inches(6.75), Inches(2.2), width=Inches(5.6))
        tb_cap = s6.shapes.add_textbox(Inches(6.75), Inches(6.35), Inches(5.6), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live interactive PR Verdict simulator with collapsible KaTeX mathematical proofs"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: FEATURE 4 — GITHUB-THEMED CODE INSPECTOR
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s7)
    add_header(s7, "Feature 4: Embedded GitHub Code Inspector", "FEATURE 04: OPEN SOURCE TRANSPARENCY",
               "Judges can inspect all 10 core Python source files directly inside the website with syntax highlighting.")

    # Left: Explanation of modules
    add_tactile_card(s7, Inches(0.8), Inches(1.8), Inches(5.3), Inches(5.1))
    tb7_l = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.7), Inches(4.7))
    tf7_l = tb7_l.text_frame
    tf7_l.word_wrap = True

    p = tf7_l.paragraphs[0]
    p.text = "10 Core Source Modules:"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    files = [
        ("src/trustmesh/records.py", "Ed25519 signatures, content addressing, hash chains (verify_chain)"),
        ("src/trustmesh/node.py", "P2P Project Node, gossip protocol, evaluate() pipeline"),
        ("src/trustmesh/graph.py", "NetworkX Web-of-Trust graph engine & Dijkstra attenuation"),
        ("src/trustmesh/campaign.py", "Dual-Layer MinHash LSH + SentenceTransformers campaign detector"),
        ("src/trustmesh/evaluator.py", "Unified decision engine with Bayesian Laplace triage"),
        ("src/trustmesh/models.py", "Pydantic v2 schemas and OpenVEX attestation models"),
        ("demo_unified.py", "End-to-end multi-signal attack and defense demonstration")
    ]
    for fn, fd in files:
        p = tf7_l.add_paragraph()
        p.text = f"• {fn}"
        p.font.name = "Courier New"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(5)

        p2 = tf7_l.add_paragraph()
        p2.text = f"   {fd}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # Right: Photo Frame with Git Panel Screenshot
    crop_git_path = Path("/tmp/crop_git_panel.png")
    if crop_git_path.exists():
        add_tactile_card(s7, Inches(6.4), Inches(1.8), Inches(6.1), Inches(5.1), bg_color=CARD_CREAM)
        s7.shapes.add_picture(str(crop_git_path), Inches(6.55), Inches(2.1), width=Inches(5.8))
        tb_cap = s7.shapes.add_textbox(Inches(6.55), Inches(6.35), Inches(5.8), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live GitHub-themed code inspector with file tree, line numbers & dark syntax highlight"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: 100% LOCAL OPEN-WEIGHT AI ARCHITECTURE (Strict Compliance)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s8)
    add_header(s8, "100% Local Open-Weight AI Architecture", "AI IN PRODUCT COMPLIANCE",
               "Strict compliance with Hack Day Sonipat rules: zero cloud APIs, zero telemetry, 100% offline CPU inference.")

    # Model 1 Card
    add_tactile_card(s8, Inches(0.8), Inches(1.8), Inches(5.75), Inches(5.1), bg_color=VERDICT_INDIGO_BG, border_color=VERDICT_INDIGO)
    tb8_l = s8.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.15), Inches(4.7))
    tf8_l = tb8_l.text_frame
    tf8_l.word_wrap = True

    p = tf8_l.paragraphs[0]
    p.text = "Model 1: Sentence Transformers"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    p = tf8_l.add_paragraph()
    p.text = "sentence-transformers/all-MiniLM-L6-v2"
    p.font.name = "Courier New"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    m1_pts = [
        ("Dense Embeddings: ", "Generates 384-dimensional dense semantic vectors from PR descriptions and diff summaries."),
        ("Semantic Spam Distance: ", "Compares incoming PRs against known spam campaign clusters via cosine distance."),
        ("CPU Efficiency: ", "Compact ~80MB footprint running sub-50ms inference on standard CPUs."),
        ("Total Privacy: ", "Contributor code diffs and maintainer notes never leave the local node.")
    ]
    for h, b in m1_pts:
        p = tf8_l.add_paragraph()
        p.text = f"• {h}"
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = VERDICT_INDIGO
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # Model 2 Card
    add_tactile_card(s8, Inches(6.75), Inches(1.8), Inches(5.75), Inches(5.1), bg_color=VERDICT_GREEN_BG, border_color=VERDICT_GREEN)
    tb8_r = s8.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.15), Inches(4.7))
    tf8_r = tb8_r.text_frame
    tf8_r.word_wrap = True

    p = tf8_r.paragraphs[0]
    p.text = "Model 2: Local Code LLM"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_GREEN

    p = tf8_r.add_paragraph()
    p.text = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    p.font.name = "Courier New"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL

    m2_pts = [
        ("Local Code Reasoning: ", "Lightweight open-weight instruction model optimized for repository triage."),
        ("Verdict Synthesis: ", "Translates Ed25519 graph proofs into plain-English maintainer explanations."),
        ("Quantized Execution: ", "Runs locally via CPU/GGUF without active internet connectivity."),
        ("Hackathon Integrity: ", "100% compliant with zero external dependencies on OpenAI, Anthropic, or Gemini.")
    ]
    for h, b in m2_pts:
        p = tf8_r.add_paragraph()
        p.text = f"• {h}"
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = VERDICT_GREEN
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 9: PRODUCTION DEPLOYMENT & TESTING VERIFICATION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s9)
    add_header(s9, "Live Production Deployment & Verification", "ENGINEERING EXCELLENCE",
               "Fully deployed on GitHub Pages with 39 passing automated unit tests.")

    # Left: Deployment Specs
    add_tactile_card(s9, Inches(0.8), Inches(1.8), Inches(5.75), Inches(5.1))
    tb9_l = s9.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.15), Inches(4.7))
    tf9_l = tb9_l.text_frame
    tf9_l.word_wrap = True

    p = tf9_l.paragraphs[0]
    p.text = "Live Deployment Architecture:"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_INDIGO

    d_pts = [
        ("GitHub Repository", "github.com/dhruvv26420-jpg/Check_All_In"),
        ("Live Web Platform", "dhruvv26420-jpg.github.io/Check_All_In/"),
        ("Zero-Dependency Bundle", "Standalone index.html with embedded canvas engine, KaTeX, and simulation logic."),
        ("Clean Repository Layout", "Direct root structure with index.html, src/trustmesh/, docs/, and tests/."),
        ("Homepage Pinned Link", "Official repo sidebar links directly to the live deployed web application.")
    ]
    for lbl, val in d_pts:
        p = tf9_l.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = val
        run.font.name = "Courier New" if "github" in val else "Calibri"
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = VERDICT_INDIGO if "github" in val else TEXT_MUTED

    # Right: Test Suite Breakdown
    add_tactile_card(s9, Inches(6.75), Inches(1.8), Inches(5.75), Inches(5.1))
    tb9_r = s9.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.15), Inches(4.7))
    tf9_r = tb9_r.text_frame
    tf9_r.word_wrap = True

    p = tf9_r.paragraphs[0]
    p.text = "Comprehensive Test Suite (39 Passed):"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = VERDICT_GREEN

    tests = [
        ("✔ test_records.py (7 passed)", "Ed25519 signatures, tampering detection, key pinning, hash gaps."),
        ("✔ test_node.py (6 passed)", "Transitive decay, sybil dampening, retraction semantics, Beta prior."),
        ("✔ test_campaign.py (6 passed)", "MinHash 64-perm LSH candidate extraction, cosine similarity bursts."),
        ("✔ test_graph.py (5 passed)", "Directed peering, Dijkstra attenuation, negative isolation quarantine."),
        ("✔ test_evaluator.py (6 passed)", "Unified evaluation engine & Bayesian cold-start probation."),
        ("✔ test_simulation.py (5 passed)", "End-to-end multi-signal attack and defense simulation runs.")
    ]
    for t_head, t_body in tests:
        p = tf9_r.add_paragraph()
        p.text = t_head
        p.font.name = "Courier New"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = VERDICT_GREEN
        p.space_before = Pt(6)

        p2 = tf9_r.add_paragraph()
        p2.text = f"   {t_body}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 10: CONCLUSION & WINNING PROPOSITION (Team Check_All_In)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_paper_bg(s10)
    add_top_ribbon(s10, VERDICT_GREEN)

    # Large Final Card
    add_tactile_card(s10, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3), bg_color=CARD_WHITE)

    # Card Top Accent
    cb10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.15))
    cb10.fill.solid()
    cb10.fill.fore_color.rgb = VERDICT_GREEN
    cb10.line.fill.background()

    tb10 = s10.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(10.9), Inches(5.6))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p = tf10.paragraphs[0]
    p.text = "❖  HACK DAY SONIPAT · PROBLEM 07 VERDICT"
    p.font.name = "Georgia"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = VERDICT_GREEN

    p = tf10.add_paragraph()
    p.text = "Why Team Check_All_In Wins Problem 07"
    p.font.name = "Georgia"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_CHARCOAL
    p.space_before = Pt(6)

    reasons = [
        ("Decentralized by Design: ", "Operates peer-to-peer across GitHub, GitLab, and Radicle with zero central authorities or token speculation."),
        ("Mathematically Grounded: ", "Pairs Dijkstra negative-log shortest path decay with Beta-Binomial Bayesian conjugate inference and MinHash LSH."),
        ("Smear-Proof & Inclusive: ", "Asymmetric Negative Isolation neutralizes rogue maintainer attacks while Bayesian triage welcomes newcomers."),
        ("Interactive Web Experience: ", "Features 60fps HD animation engine, PR audit simulator, LaTeX proofs, and GitHub code viewer."),
        ("Live Production & Open Source: ", "100% deployed on GitHub Pages, full pytest validation, zero-cloud open-weight AI.")
    ]
    for r_head, r_body in reasons:
        p = tf10.add_paragraph()
        p.text = f"• {r_head}"
        p.font.name = "Georgia"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = r_body
        run.font.name = "Calibri"
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    p_final = tf10.add_paragraph()
    p_final.text = "Team Check_All_In: Dhruv Verma · Prajan Radhakrishnan · Mukul · Akshit Kumar"
    p_final.font.name = "Calibri"
    p_final.font.size = Pt(14)
    p_final.font.bold = True
    p_final.font.color.rgb = VERDICT_INDIGO
    p_final.space_before = Pt(16)

    p_url = tf10.add_paragraph()
    p_url.text = "🌐 Live Site: https://dhruvv26420-jpg.github.io/Check_All_In/  ·  GitHub: github.com/dhruvv26420-jpg/Check_All_In"
    p_url.font.name = "Courier New"
    p_url.font.size = Pt(12)
    p_url.font.bold = True
    p_url.font.color.rgb = VERDICT_GREEN
    p_url.space_before = Pt(4)

    # Save outputs
    out_path = Path("/Users/dhruvverma/.gemini/antigravity/scratch/trustmesh/Check_All_In.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    build_characterful_deck()
