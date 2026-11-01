#!/usr/bin/env python3
"""
Generate an exceptional, high-production, character-full PowerPoint pitch deck (16:9 widescreen)
for Team Check_All_In (Hack Day Sonipat, Problem 07).

Features:
- Slide 1: Showstopper Front Page / Hero Dossier Poster
- Slide 2: Numbered System Index / Presentation Roadmap (Table of Contents)
- Slide 3: Act I — The Crisis: Maintainer Burnout vs Coordinated AI Spam
- Slide 4: Act II — The Live Web Platform Experience & Tactile War Room
- Slide 5: Act II — The 60fps HD Canvas Simulation Engine & Live Telemetry
- Slide 6: Act III — The 4 Storytelling Personas (Alice, Dan, Sybil, Charlie)
- Slide 7: Act IV — Mathematical Rigor & KaTeX Formal Proofs
- Slide 8: Act V — 100% Local Open-Weight AI Architecture (Strict Compliance)
- Slide 9: Act VI — Embedded GitHub Code Explorer & 39/39 Automated Test Matrix
- Slide 10: Grand Finale — Why Team Check_All_In Wins Problem 07
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_ultimate_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Premium Color Palette
    DARK_NAVY = RGBColor(10, 15, 29)         # #0a0f1d Deep Midnight Navy
    DARK_CARD = RGBColor(18, 25, 44)         # #12192c Dark Card
    DARK_CARD_ALT = RGBColor(24, 34, 58)     # #18223a Lighter Navy Card
    DARK_BORDER = RGBColor(39, 52, 85)       # #273455 Dark Border

    BG_PAPER = RGBColor(251, 249, 244)       # #fbf9f4 Warm Paper White
    CARD_WHITE = RGBColor(255, 255, 255)     # #ffffff
    CARD_CREAM = RGBColor(246, 242, 233)     # #f6f2e9
    SHADOW_PAPER = RGBColor(223, 216, 204)   # #dfd8cc Paper Drop Shadow
    BORDER_PAPER = RGBColor(226, 221, 211)   # #e2ddd3 Craft Paper Border

    TEXT_WHITE = RGBColor(248, 250, 252)     # #f8fafc Pure White
    TEXT_SLATE = RGBColor(148, 163, 184)     # #94a3b8 Muted Slate
    TEXT_CHARCOAL = RGBColor(27, 38, 59)     # #1b263b Deep Editorial
    TEXT_MUTED = RGBColor(100, 116, 139)     # #64748b Paper Muted

    # High-Vibrancy Accent Colors
    ACCENT_EMERALD = RGBColor(16, 185, 129)  # #10b981 Vibrant Green
    ACCENT_FOREST = RGBColor(22, 101, 52)    # #166534 Editorial Green
    ACCENT_CRIMSON = RGBColor(239, 68, 68)   # #ef4444 Vibrant Red
    ACCENT_RED = RGBColor(185, 28, 28)       # #b91c1c Deep Red
    ACCENT_AMBER = RGBColor(245, 158, 11)    # #f59e0b Vibrant Amber
    ACCENT_GOLD = RGBColor(180, 83, 9)       # #b45309 Deep Ochre
    ACCENT_INDIGO = RGBColor(99, 102, 241)   # #6366f1 Vibrant Indigo
    ACCENT_CYAN = RGBColor(6, 182, 212)      # #06b6d4 Electric Cyan

    def fill_bg(slide, col=BG_PAPER):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = col
        bg.line.fill.background()
        return bg

    def add_top_ribbon(slide, col=ACCENT_INDIGO):
        r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.08))
        r.fill.solid()
        r.fill.fore_color.rgb = col
        r.line.fill.background()

    def add_tactile_card(slide, left, top, width, height, bg_col=CARD_WHITE, border_col=BORDER_PAPER, shadow_col=SHADOW_PAPER):
        # 3D Paper shadow
        sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.04), top + Inches(0.04), width, height)
        sh.fill.solid()
        sh.fill.fore_color.rgb = shadow_col
        sh.line.fill.background()

        # Foreground card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_col
        card.line.color.rgb = border_col
        card.line.width = Pt(1.2)
        return card

    def add_header(slide, title, category="HACK DAY SONIPAT · PROBLEM 07", subtitle=None, ribbon_col=ACCENT_INDIGO):
        add_top_ribbon(slide, ribbon_col)

        # Stamped Category Tag
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(3.6), Inches(0.32))
        tag.fill.solid()
        tag.fill.fore_color.rgb = CARD_CREAM
        tag.line.color.rgb = BORDER_PAPER
        tag.line.width = Pt(1)
        p_tag = tag.text_frame.paragraphs[0]
        p_tag.text = f"❖  {category.upper()}"
        p_tag.font.name = "Georgia"
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ribbon_col
        p_tag.alignment = PP_ALIGN.CENTER

        # Title
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

    # =========================================================================
    # SLIDE 1: FRONT PAGE (High-Impact Hero Poster)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    fill_bg(s1, DARK_NAVY)

    # Top Glowing Accent Bar
    bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = ACCENT_CYAN
    bar1.line.fill.background()

    # Giant Hero Card (Dark Glass / Terminal Aesthetic)
    hero_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3))
    hero_card.fill.solid()
    hero_card.fill.fore_color.rgb = DARK_CARD
    hero_card.line.color.rgb = DARK_BORDER
    hero_card.line.width = Pt(1.5)

    # Top Stamped Pill Badge
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.95), Inches(4.8), Inches(0.38))
    pill.fill.solid()
    pill.fill.fore_color.rgb = DARK_CARD_ALT
    pill.line.color.rgb = ACCENT_CYAN
    pill.line.width = Pt(1)
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "⚡ HACK DAY SONIPAT — PROBLEM 07 · TEAM CHECK_ALL_IN"
    p_pill.font.name = "Courier New"
    p_pill.font.size = Pt(10.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = ACCENT_CYAN
    p_pill.alignment = PP_ALIGN.CENTER

    # Title & Subtitle inside Hero Card
    tb_hero = s1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(10.9), Inches(2.2))
    tf_h = tb_hero.text_frame
    tf_h.word_wrap = True

    p = tf_h.paragraphs[0]
    p.text = "TrustMesh: Decentralized Open-Source Trust Network"
    p.font.name = "Georgia"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p = tf_h.add_paragraph()
    p.text = "A Tactile Web Platform, 60fps HD Simulation Engine & Mathematical PR Audit Bench"
    p.font.name = "Georgia"
    p.font.size = Pt(16)
    p.font.color.rgb = ACCENT_AMBER
    p.space_before = Pt(6)

    p = tf_h.add_paragraph()
    p.text = (
        "Protecting open-source maintainers from coordinated AI PR spam campaigns with "
        "Bayesian Laplace newcomer due process, zero cloud dependencies, and 100% local open-weight AI."
    )
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_SLATE
    p.space_before = Pt(8)

    # 4 Team Members Badges
    team_members = [
        ("Dhruv Verma", "@dhruvv26420-jpg"),
        ("Prajan Radhakrishnan", "@prajanradhakrishnan"),
        ("Mukul", "Contributor"),
        ("Akshit Kumar", "Contributor")
    ]
    for i, (name, role) in enumerate(team_members):
        tx = Inches(1.2 + i * 2.7)
        ty = Inches(3.8)
        mb = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx, ty, Inches(2.55), Inches(0.9))
        mb.fill.solid()
        mb.fill.fore_color.rgb = DARK_CARD_ALT
        mb.line.color.rgb = DARK_BORDER
        mb.line.width = Pt(1)

        tb_m = s1.shapes.add_textbox(tx + Inches(0.15), ty + Inches(0.1), Inches(2.25), Inches(0.7))
        tf_m = tb_m.text_frame
        p_n = tf_m.paragraphs[0]
        p_n.text = f"👤 {name}"
        p_n.font.name = "Georgia"
        p_n.font.size = Pt(11)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_WHITE

        p_r = tf_m.add_paragraph()
        p_r.text = role
        p_r.font.name = "Courier New"
        p_r.font.size = Pt(9.5)
        p_r.font.color.rgb = ACCENT_CYAN

    # 4 Key Stats / Metric Badges Bar
    metrics = [
        ("60 FPS", "Canvas Simulation"),
        ("E[T]=0.50", "Laplace Prior"),
        ("O(1) LSH", "MinHash Clustering"),
        ("100% Local", "Open-Weight AI")
    ]
    for i, (m_val, m_lbl) in enumerate(metrics):
        mx = Inches(1.2 + i * 2.7)
        my = Inches(4.9)
        mb = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, mx, my, Inches(2.55), Inches(0.85))
        mb.fill.solid()
        mb.fill.fore_color.rgb = DARK_NAVY
        mb.line.color.rgb = ACCENT_EMERALD
        mb.line.width = Pt(1)

        tb_met = s1.shapes.add_textbox(mx + Inches(0.15), my + Inches(0.08), Inches(2.25), Inches(0.7))
        tf_met = tb_met.text_frame
        p_v = tf_met.paragraphs[0]
        p_v.text = m_val
        p_v.font.name = "Georgia"
        p_v.font.size = Pt(13)
        p_v.font.bold = True
        p_v.font.color.rgb = ACCENT_EMERALD

        p_l = tf_met.add_paragraph()
        p_l.text = m_lbl
        p_l.font.name = "Calibri"
        p_l.font.size = Pt(10)
        p_l.font.color.rgb = TEXT_SLATE

    # Bottom Live URL Badge
    url_bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.95), Inches(10.9), Inches(0.6))
    url_bar.fill.solid()
    url_bar.fill.fore_color.rgb = DARK_CARD_ALT
    url_bar.line.color.rgb = ACCENT_EMERALD
    url_bar.line.width = Pt(1.5)

    tb_u = s1.shapes.add_textbox(Inches(1.4), Inches(6.02), Inches(10.5), Inches(0.45))
    p_u = tb_u.text_frame.paragraphs[0]
    p_u.text = "🌐 LIVE PLATFORM: https://dhruvv26420-jpg.github.io/Check_All_In/  ·  GITHUB: dhruvv26420-jpg/Check_All_In"
    p_u.font.name = "Courier New"
    p_u.font.size = Pt(11)
    p_u.font.bold = True
    p_u.font.color.rgb = TEXT_WHITE
    p_u.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: INDEX / ROADMAP (Table of Contents)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    fill_bg(s2)
    add_header(s2, "System Architecture & Presentation Roadmap", "AGENDA & TABLE OF CONTENTS",
               "An end-to-end traversal of the problem, the live web experience, and the underlying mathematical engine.")

    index_items = [
        ("01", "THE CRISIS", "Maintainer Burnout & AI Spam",
         "Why siloed code reviews break down during high-volume contribution events like Hacktoberfest.",
         ACCENT_RED),
        ("02", "THE WEB PLATFORM", "Tactile War Room Experience",
         "Handcrafted paper design system, 60fps canvas engine, PR audit bench, and live KaTeX proofs.",
         ACCENT_INDIGO),
        ("03", "60FPS HD ANIMATOR", "Interactive Physics Simulation",
         "4 dynamic canvas visualization modes: P2P Gossip, MinHash Defense, Cold-Start, and OpenVEX.",
         ACCENT_CYAN),
        ("04", "THE 4 PERSONAS", "Algorithmic Due Process",
         "Alice (Vouched), Dan (Denounced), Sybil (Botnet), and Charlie (Newcomer) evaluated in real time.",
         ACCENT_FOREST),
        ("05", "MATHEMATICAL RIGOR", "Formal Proofs & KaTeX Engine",
         "Dijkstra negative-log attenuation, Bayesian Laplace prior, MinHash LSH, and smear defense.",
         ACCENT_GOLD),
        ("06", "LOCAL AI & VERDICT", "Hackathon Compliance & Grand Finale",
         "100% offline open-weight models (all-MiniLM-L6-v2 + Qwen2.5-Coder), 39 passed tests, and verdict.",
         ACCENT_EMERALD)
    ]

    for i, (num, category, title, desc, col) in enumerate(index_items):
        ix = Inches(0.8 + (i % 3) * 3.95)
        iy = Inches(1.8 + (i // 3) * 2.65)
        add_tactile_card(s2, ix, iy, Inches(3.75), Inches(2.4))

        # Top numbered tag
        num_tag = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, ix, iy, Inches(0.7), Inches(0.4))
        num_tag.fill.solid()
        num_tag.fill.fore_color.rgb = col
        num_tag.line.fill.background()
        p_nt = num_tag.text_frame.paragraphs[0]
        p_nt.text = num
        p_nt.font.name = "Georgia"
        p_nt.font.size = Pt(13)
        p_nt.font.bold = True
        p_nt.font.color.rgb = CARD_WHITE
        p_nt.alignment = PP_ALIGN.CENTER

        tb = s2.shapes.add_textbox(ix + Inches(0.2), iy + Inches(0.48), Inches(3.35), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = category
        p.font.name = "Courier New"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col

        p = tf.add_paragraph()
        p.text = title
        p.font.name = "Georgia"
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(2)

        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: ACT I — THE HACKTOBERFEST CRISIS (Problem)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    fill_bg(s3)
    add_header(s3, "The Maintainer Battlefield: AI Spam vs Open Source", "ACT I · THE CRISIS",
               "Why traditional review is broken and naive reputation blocks kill newcomer participation.",
               ribbon_col=ACCENT_RED)

    # Left: The AI Spam Nightmare (Red Tinted Card)
    add_tactile_card(s3, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_col=RGBColor(254, 242, 242), border_col=ACCENT_RED)
    tb3_l = s3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.1), Inches(4.7))
    tf3_l = tb3_l.text_frame
    tf3_l.word_wrap = True

    p = tf3_l.paragraphs[0]
    p.text = "🚨 The Current Crisis (Why Maintainers Burn Out):"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    bad_points = [
        ("Siloed Review Vulnerability: ", "Maintainer Alice rejects a spam PR in Repo A, but Maintainer Bob in Repo B has zero visibility and reviews it from scratch."),
        ("Automated AI PR Storms: ", "Scripted LLMs generate hundreds of near-identical PRs across 50+ repositories in seconds during Hacktoberfest."),
        ("The False Positive Trap: ", "Crude automated heuristics (e.g. 'block users with <5 commits') ban legitimate students and first-time contributors fixing typos."),
        ("Centralized Platform Silos: ", "Central reputation databases introduce single points of failure, censorship risks, and commercial vendor lock-in.")
    ]
    for head, body in bad_points:
        p = tf3_l.add_paragraph()
        p.text = f"• {head}"
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_RED
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # Right: The TrustMesh Solution (Green Tinted Card)
    add_tactile_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_col=RGBColor(236, 253, 245), border_col=ACCENT_FOREST)
    tb3_r = s3.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.7))
    tf3_r = tb3_r.text_frame
    tf3_r.word_wrap = True

    p = tf3_r.paragraphs[0]
    p.text = "✔ The TrustMesh Paradigm (How We Solve It):"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_FOREST

    good_points = [
        ("Peer-to-Peer Gossip Web: ", "Repositories exchange Ed25519-signed vouches directly. When one project detects a spam wave, all peers are immunized."),
        ("Bayesian Laplace Due Process: ", "Accounts with zero history start at E[T] = 0.50 with wide uncertainty—routing to human triage, NEVER auto-rejection."),
        ("MinHash LSH Campaign Detection: ", "Collapses synonym and paraphrased spam variants across repositories in real time without external cloud APIs."),
        ("Asymmetric Negative Isolation: ", "Rogue maintainers cannot smear honest contributors; hostile untrusted denouncements are quarantined harmlessly.")
    ]
    for head, body in good_points:
        p = tf3_r.add_paragraph()
        p.text = f"• {head}"
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_FOREST
        p.space_before = Pt(8)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 4: ACT II — THE LIVE WEB PLATFORM (War Room Experience)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    fill_bg(s4)
    add_header(s4, "The TrustMesh War Room: Tactile Web Platform", "ACT II · THE WEB EXPERIENCE",
               "A handcrafted editorial interface providing maintainers with a real-time defense operations deck.")

    # 3 Distinct Feature Zones
    features = [
        ("01 · 60fps HD Canvas Animator",
         "Interactive Real-Time Telemetry",
         "Hardware-accelerated HTML5 canvas rendering peer-to-peer reputation propagation, multi-hop Dijkstra attenuation, and coordinated campaign bursts at 60fps.",
         ACCENT_INDIGO),
        ("02 · PR Audit Simulator Bench",
         "Live Multi-Persona Testing Sandbox",
         "Interactive sandbox evaluating real-world contributor personas with instant cryptographic verdict badges: ALLOW_VOUCHED, QUARANTINE_DEN, and HONEST_NEWCOMER_TRIAGE.",
         ACCENT_FOREST),
        ("03 · Mathematical Proof Renderer",
         "Formal KaTeX LaTeX Formulations",
         "Every verdict is accompanied by verifiable mathematical proofs: Dijkstra negative-log shortest paths, Beta-Binomial Bayesian updates, and MinHash Jaccard collisions.",
         ACCENT_GOLD)
    ]

    for i, (title, subtitle, desc, col) in enumerate(features):
        fy = Inches(1.8 + i * 1.68)
        add_tactile_card(s4, Inches(0.8), fy, Inches(5.4), Inches(1.52))

        # Color indicator stripe
        st = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), fy, Inches(0.12), Inches(1.52))
        st.fill.solid()
        st.fill.fore_color.rgb = col
        st.line.fill.background()

        tb = s4.shapes.add_textbox(Inches(1.1), fy + Inches(0.1), Inches(4.9), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Georgia"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p = tf.add_paragraph()
        p.text = subtitle
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED

        p = tf.add_paragraph()
        p.text = desc
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(3)

    # Right: Screenshot Photo Frame with Browser Shell
    site_cap_path = Path("/tmp/site_hero_capture.png")
    if site_cap_path.exists():
        add_tactile_card(s4, Inches(6.5), Inches(1.8), Inches(6.0), Inches(5.1), bg_col=CARD_CREAM)
        s4.shapes.add_picture(str(site_cap_path), Inches(6.65), Inches(2.1), width=Inches(5.7))
        tb_c = s4.shapes.add_textbox(Inches(6.65), Inches(6.35), Inches(5.7), Inches(0.45))
        p_c = tb_c.text_frame.paragraphs[0]
        p_c.text = "▲ Live TrustMesh War Room: https://dhruvv26420-jpg.github.io/Check_All_In/"
        p_c.font.name = "Courier New"
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = ACCENT_INDIGO

    # =========================================================================
    # SLIDE 5: ACT II — 60FPS HD CANVAS SIMULATION ENGINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    fill_bg(s5)
    add_header(s5, "Interactive 60fps HD Canvas Simulation Engine", "ACT II · SIMULATION ENGINE",
               "Real-time visual telemetry illustrating cryptographic gossip, graph decay, and campaign clustering.")

    # Left: Explanation & Modes
    add_tactile_card(s5, Inches(0.8), Inches(1.8), Inches(5.3), Inches(5.1))
    tb5_l = s5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.7), Inches(4.7))
    tf5 = tb5_l.text_frame
    tf5.word_wrap = True

    p = tf5.paragraphs[0]
    p.text = "4 Interactive Canvas Modes:"
    p.font.name = "Georgia"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_INDIGO

    modes = [
        ("Mode 1 · P2P WoT Attestation Gossip", "Ed25519-signed vouchers pulse across network hops. Transitive trust decays smoothly via Dijkstra negative-log weights."),
        ("Mode 2 · Coordinated Campaign Defense", "Spatiotemporal MinHash bursts illuminate in red. Cross-repo clustering quarantines the coordinated wave in under 1 second."),
        ("Mode 3 · Bayesian Cold-Start Triage", "First-time contributors enter with wide epistemic variance (Var=0.0833), routing safely to maintainer probation."),
        ("Mode 4 · Cryptographic Review & OpenVEX", "Verdicts are packaged into machine-readable signed OpenVEX attestation payloads for automated GitHub CI pipelines.")
    ]
    for sm_title, sm_desc in modes:
        p = tf5.add_paragraph()
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

    # Right: Photo Frame with Cropped Video Player Screenshot
    crop_video_path = Path("/tmp/crop_video_player.png")
    if crop_video_path.exists():
        add_tactile_card(s5, Inches(6.4), Inches(1.8), Inches(6.1), Inches(5.1), bg_col=CARD_CREAM)
        s5.shapes.add_picture(str(crop_video_path), Inches(6.55), Inches(2.1), width=Inches(5.8))
        tb_cap = s5.shapes.add_textbox(Inches(6.55), Inches(6.35), Inches(5.8), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live 1920×960 HD Video Animator embedded in the website with speed & mode controls"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10.5)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: ACT III — THE 4 STORYTELLING PERSONAS (Character-Full!)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    fill_bg(s6)
    add_header(s6, "The 4 Contributor Personas & Audit Simulator", "ACT III · ALGORITHMIC DUE PROCESS",
               "How TrustMesh evaluates incoming pull requests using real-world contributor personas.")

    personas = [
        ("👩‍💻 Alice: Trusted Contributor", "ALLOW_VOUCHED", ACCENT_FOREST, RGBColor(236, 253, 245),
         "PR #101: Fix memory leak in connection pool",
         "Web-of-Trust path: 2 hops (Weight 0.85). Vouched by Repo B and Repo C. Fast-tracked directly to maintainer review."),

        ("🦹 Dan: Malicious Actor", "QUARANTINE_DEN", ACCENT_RED, RGBColor(254, 242, 242),
         "PR #202: Add hidden telemetry logging",
         "Corroborated denouncements backed by concrete near-duplicate fingerprints. Negative isolation protects from retaliatory smears."),

        ("🤖 Sybil Botnet #14", "QUARANTINE_CAM", ACCENT_RED, RGBColor(254, 242, 242),
         "PR #303: Automated spam PR wave across 12 repos",
         "MinHash LSH hit: Jaccard similarity >= 0.85 within 600 seconds. Cross-repo campaign flag quarantines entire cluster instantly."),

        ("🌱 Charlie: Honest Newcomer", "HONEST_NEWCOMER_TRIAGE", ACCENT_GOLD, RGBColor(255, 251, 235),
         "PR #404: Fix typo in documentation README",
         "Bayesian Laplace prior E[T]=0.50, Variance=0.0833. First-time contributor is never auto-blocked; routed to gentle probation review.")
    ]

    for i, (p_name, badge, badge_col, bg_col, pr_title, desc) in enumerate(personas):
        px = Inches(0.8 + (i % 2) * 5.95)
        py = Inches(1.8 + (i // 2) * 2.65)
        add_tactile_card(s6, px, py, Inches(5.75), Inches(2.4), bg_col=bg_col, border_col=badge_col)

        tb = s6.shapes.add_textbox(px + Inches(0.3), py + Inches(0.15), Inches(5.15), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = p_name
        p.font.name = "Georgia"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL

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
    # SLIDE 7: ACT IV — MATHEMATICAL RIGOR & LATEX PROOFS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    fill_bg(s7)
    add_header(s7, "Mathematical Foundations & Formal KaTeX Proofs", "ACT IV · MATHEMATICAL RIGOR",
               "Every verdict is mathematically justified through probabilistic inference and graph theory.")

    # Left: The 4 mathematical pillars
    add_tactile_card(s7, Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.1))
    tb7_l = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.9), Inches(4.7))
    tf7_l = tb7_l.text_frame
    tf7_l.word_wrap = True

    p = tf7_l.paragraphs[0]
    p.text = "Formal Mathematical Formulations:"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_INDIGO

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
        p = tf7_l.add_paragraph()
        p.text = f"{m_title}"
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_CHARCOAL
        p.space_before = Pt(6)

        p_f = tf7_l.add_paragraph()
        p_f.text = f"   {m_form}"
        p_f.font.name = "Courier New"
        p_f.font.size = Pt(10)
        p_f.font.bold = True
        p_f.font.color.rgb = ACCENT_INDIGO

        p_d = tf7_l.add_paragraph()
        p_d.text = f"   {m_desc}"
        p_d.font.name = "Calibri"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Photo Frame with Cropped Verdict LaTeX Screenshot
    crop_verdict_path = Path("/tmp/crop_verdicts_detail.png")
    if crop_verdict_path.exists():
        add_tactile_card(s7, Inches(6.6), Inches(1.8), Inches(5.9), Inches(5.1), bg_col=CARD_CREAM)
        s7.shapes.add_picture(str(crop_verdict_path), Inches(6.75), Inches(2.2), width=Inches(5.6))
        tb_cap = s7.shapes.add_textbox(Inches(6.75), Inches(6.35), Inches(5.6), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live interactive PR Verdict simulator with collapsible KaTeX mathematical proofs"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: ACT V — 100% LOCAL OPEN-WEIGHT AI ARCHITECTURE
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    fill_bg(s8)
    add_header(s8, "100% Local Open-Weight AI Architecture", "ACT V · AI IN PRODUCT COMPLIANCE",
               "Strict compliance with Hack Day Sonipat rules: zero cloud APIs, zero telemetry, 100% offline CPU inference.")

    # Model 1 Card
    add_tactile_card(s8, Inches(0.8), Inches(1.8), Inches(5.75), Inches(5.1), bg_col=RGBColor(238, 242, 255), border_col=ACCENT_INDIGO)
    tb8_l = s8.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.15), Inches(4.7))
    tf8_l = tb8_l.text_frame
    tf8_l.word_wrap = True

    p = tf8_l.paragraphs[0]
    p.text = "Model 1: Sentence Transformers"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_INDIGO

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
        p.font.color.rgb = ACCENT_INDIGO
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # Model 2 Card
    add_tactile_card(s8, Inches(6.75), Inches(1.8), Inches(5.75), Inches(5.1), bg_col=RGBColor(236, 253, 245), border_col=ACCENT_FOREST)
    tb8_r = s8.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.15), Inches(4.7))
    tf8_r = tb8_r.text_frame
    tf8_r.word_wrap = True

    p = tf8_r.paragraphs[0]
    p.text = "Model 2: Local Code LLM"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_FOREST

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
        p.font.color.rgb = ACCENT_FOREST
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = b
        run.font.bold = False
        run.font.color.rgb = TEXT_CHARCOAL

    # =========================================================================
    # SLIDE 9: ACT VI — GITHUB CODE EXPLORER & 39/39 TESTS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    fill_bg(s9)
    add_header(s9, "Open Source Transparency & Automated Tests", "ACT VI · CODE EXPLORER & TESTS",
               "Judges can inspect all 10 core Python source files directly inside the website with syntax highlighting.")

    # Left: Test Matrix Card
    add_tactile_card(s9, Inches(0.8), Inches(1.8), Inches(5.3), Inches(5.1))
    tb9_l = s9.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(4.7), Inches(4.7))
    tf9_l = tb9_l.text_frame
    tf9_l.word_wrap = True

    p = tf9_l.paragraphs[0]
    p.text = "Automated Test Matrix (39 Passed):"
    p.font.name = "Georgia"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_FOREST

    tests = [
        ("✔ test_records.py (7 passed)", "Ed25519 signatures, tampering, key pinning, hash chains."),
        ("✔ test_node.py (6 passed)", "Transitive decay, sybil dampening, retraction semantics."),
        ("✔ test_campaign.py (6 passed)", "MinHash 64-perm LSH candidate extraction, cosine bursts."),
        ("✔ test_graph.py (5 passed)", "Directed peering, Dijkstra attenuation, negative isolation."),
        ("✔ test_evaluator.py (6 passed)", "Unified evaluation engine & Bayesian cold-start probation."),
        ("✔ test_simulation.py (5 passed)", "End-to-end multi-signal attack and defense simulation runs.")
    ]
    for t_head, t_body in tests:
        p = tf9_l.add_paragraph()
        p.text = t_head
        p.font.name = "Courier New"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_FOREST
        p.space_before = Pt(5)

        p2 = tf9_l.add_paragraph()
        p2.text = f"   {t_body}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # Right: Photo Frame with Git Panel Screenshot
    crop_git_path = Path("/tmp/crop_git_panel.png")
    if crop_git_path.exists():
        add_tactile_card(s9, Inches(6.4), Inches(1.8), Inches(6.1), Inches(5.1), bg_col=CARD_CREAM)
        s9.shapes.add_picture(str(crop_git_path), Inches(6.55), Inches(2.1), width=Inches(5.8))
        tb_cap = s9.shapes.add_textbox(Inches(6.55), Inches(6.35), Inches(5.8), Inches(0.45))
        p_cap = tb_cap.text_frame.paragraphs[0]
        p_cap.text = "▲ Live GitHub-themed code inspector with file tree, line numbers & dark syntax highlight"
        p_cap.font.name = "Calibri"
        p_cap.font.size = Pt(10)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 10: GRAND FINALE — WHY TEAM CHECK_ALL_IN WINS
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    fill_bg(s10)
    add_top_ribbon(s10, ACCENT_FOREST)

    add_tactile_card(s10, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3), bg_col=CARD_WHITE)

    # Top Green Accent Banner
    cb10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.15))
    cb10.fill.solid()
    cb10.fill.fore_color.rgb = ACCENT_FOREST
    cb10.line.fill.background()

    tb10 = s10.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(10.9), Inches(5.6))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p = tf10.paragraphs[0]
    p.text = "❖  HACK DAY SONIPAT · PROBLEM 07 VERDICT"
    p.font.name = "Georgia"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_FOREST

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
        ("Interactive Web Experience: ", "Features 60fps HD animation engine, PR audit simulator, KaTeX proofs, and GitHub code viewer."),
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
    p_final.font.color.rgb = ACCENT_INDIGO
    p_final.space_before = Pt(16)

    p_url = tf10.add_paragraph()
    p_url.text = "🌐 Live Site: https://dhruvv26420-jpg.github.io/Check_All_In/  ·  GitHub: github.com/dhruvv26420-jpg/Check_All_In"
    p_url.font.name = "Courier New"
    p_url.font.size = Pt(12)
    p_url.font.bold = True
    p_url.font.color.rgb = ACCENT_FOREST
    p_url.space_before = Pt(4)

    # Save presentation
    out_path = Path("/Users/dhruvverma/.gemini/antigravity/scratch/trustmesh/Check_All_In.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_ultimate_deck()
