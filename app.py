import streamlit as st
import random
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from io import BytesIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CGI Cyber Tabletop Exercise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

/* ── Main content width ── */
.block-container {
    max-width: 860px;
    padding: 2rem 2rem 4rem;
    margin: auto;
}

/* ── Header banner ── */
.header-banner {
    background: linear-gradient(135deg, #161b22 0%, #1f2937 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.header-banner h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 0 0 0.3rem;
}
.header-banner p {
    font-size: 0.95rem;
    color: #8b949e;
    margin: 0;
}

/* ── Stage card ── */
.stage-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #58a6ff;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.stage-card h3 {
    color: #58a6ff;
    margin: 0 0 0.4rem;
    font-size: 1.05rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.stage-card .timestamp {
    color: #f0883e;
    font-size: 0.85rem;
    font-family: monospace;
    margin-bottom: 0.8rem;
}
.stage-card p {
    color: #c9d1d9;
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0;
}

/* ── Feedback box ── */
.feedback-box {
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.92rem;
    line-height: 1.6;
}
.feedback-correct {
    background: #0d2818;
    border: 1px solid #238636;
    color: #3fb950;
}
.feedback-partial {
    background: #1c1a00;
    border: 1px solid #9e6a03;
    color: #e3b341;
}
.feedback-poor {
    background: #1c0a0a;
    border: 1px solid #6e1a1a;
    color: #f85149;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    background: #1f2937;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.85rem;
    color: #58a6ff;
    margin-bottom: 1rem;
}

/* ── Result card ── */
.result-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.result-card .big-score {
    font-size: 4rem;
    font-weight: 800;
    color: #58a6ff;
    line-height: 1;
}
.result-card .classification {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 0.5rem;
}
.result-card .sub {
    font-size: 0.88rem;
    color: #8b949e;
    margin-top: 0.3rem;
}

/* ── Decision summary row ── */
.decision-row {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.7rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] h2 {
    color: #58a6ff;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Streamlit overrides ── */
div[data-testid="stForm"] {
    background: transparent;
    border: none;
    padding: 0;
}
.stRadio label { color: #c9d1d9 !important; }
.stButton > button {
    background: #238636;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1.8rem;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}
.stButton > button:hover { background: #2ea043; }
.stTextInput > div > div > input {
    background: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
}
code, pre {
    background: #161b22 !important;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #79c0ff !important;
    font-size: 0.85rem !important;
}
hr { border-color: #21262d; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SCENARIO DATA
# ─────────────────────────────────────────────
SCENARIOS = {
    "A": {
        "detection_email": """\
From:    it-support@companny-secure.com
To:      j.wilson@company.com
Subject: [URGENT] Credential Verification Required
Date:    Mon, 14 Oct  08:41:03 +0000

Your account requires immediate verification.
Action required within 2 hours or access will be suspended.

→ http://secure-company-login.co/verify?token=8f3kLmP""",
        "siem_log": """\
[SIEM ALERT — HIGH]  08:55:14 UTC
─────────────────────────────────────────
User Account : hr.jane@company.com
Source IP    : 185.234.219.12
Geo-location : Kaliningrad, RU
Auth Method  : Password (no MFA)
Status       : SUCCESS
Prior failed : 0  (clean auth — no brute force)
Session Age  : 4m 32s  →  active""",
        "email_header": """\
[MAIL GATEWAY ALERT]  09:09:47 UTC
─────────────────────────────────────────
Received-From : mail.unknown-host.ru
To            : hr.jane@company.com
Subject       : Payroll Update Q4 — Action Required
Attachment    : payroll_update.xlsm  (macro-enabled)
VirusTotal    : 6/72 engines flagged
Sandbox       : Outbound callback attempt detected""",
        "network_alert": """\
[NETWORK DLP ALERT]  09:24:58 UTC
─────────────────────────────────────────
Protocol     : HTTPS (port 443)
Source       : WS-HR-042  (hr.jane — internal)
Destination  : 91.108.56.14  (unclassified external)
Transfer     : 4.2 GB outbound
Duration     : 11 minutes
Classification: Potential data exfiltration event""",
    }
}

STAGES = ["Detection", "Response", "Containment", "Communication", "Recovery"]

QUESTIONS = {
    "detection": {
        "time": "08:42 UTC",
        "title": "Stage 1 — Threat Detection",
        "context": (
            "A member of staff has forwarded a suspicious email to the shared security inbox. "
            "You are the on-call analyst. Review the artefact below and decide how to proceed."
        ),
        "options": ["Ignore — likely spam", "Escalate to IT helpdesk", "Inspect headers and analyse the link"],
        "scores":  [4, 12, 20],
        "analysis": [
            ("poor",    "Ignoring phishing indicators leaves the attacker undetected. "
                        "Credential harvesting links are designed to look legitimate — "
                        "dismissing without analysis allows initial access to succeed."),
            ("partial", "Escalating to IT reduces dwell time before credential compromise "
                        "and is better than no action. However, generic helpdesk staff may "
                        "lack the tooling to perform header or URL analysis effectively."),
            ("correct", "Inspecting mail headers exposes spoofed sender domains and relay "
                        "chains. Sandboxing or safely expanding the URL reveals phishing "
                        "infrastructure. This is the correct first technical response — "
                        "it produces evidence and prevents credential harvesting."),
        ],
    },
    "response": {
        "time": "08:55 UTC",
        "title": "Stage 2 — Incident Response",
        "context": (
            "Your SIEM has triggered a high-severity alert. A company account has authenticated "
            "successfully from an unusual foreign IP with no prior failed attempts, suggesting "
            "valid credentials were used. A session is currently active."
        ),
        "options": ["Ignore — could be a VPN or traveller", "Force password reset", "Investigate the active session scope", "Immediately disable the account"],
        "scores":  [3, 10, 15, 20],
        "analysis": [
            ("poor",    "Dismissing a successful foreign login without MFA as a VPN artefact "
                        "is a critical error. The attacker session remains active and can "
                        "begin lateral movement or data access immediately."),
            ("partial", "A password reset invalidates credentials but does NOT terminate an "
                        "existing session token. An attacker already authenticated may retain "
                        "access until the session expires — typically hours."),
            ("partial", "Scoping the session — checking what resources were accessed, what "
                        "data was read, and whether privilege escalation occurred — is a "
                        "sound investigative step, but delays direct containment."),
            ("correct", "Disabling the account immediately terminates all active sessions "
                        "and prevents re-authentication. This is the fastest containment "
                        "action and is fully reversible once the incident is scoped."),
        ],
    },
    "containment": {
        "time": "09:10 UTC",
        "title": "Stage 3 — Containment",
        "context": (
            "A macro-enabled attachment has been received on an internal workstation. "
            "Gateway sandbox analysis detected an outbound callback attempt, "
            "suggesting a dropper or C2 beacon. The machine is currently live on the network."
        ),
        "options": ["Wait for antivirus scan to complete", "Notify IT and log the ticket", "Pull and review endpoint logs", "Immediately isolate the machine from the network"],
        "scores":  [4, 10, 14, 20],
        "analysis": [
            ("poor",    "Waiting for AV to complete while a live C2 beacon is active allows "
                        "the attacker to download second-stage payloads, establish persistence, "
                        "or begin lateral movement across the network."),
            ("partial", "Logging a ticket initiates a paper trail and involves IT, but does "
                        "nothing to stop active malware execution or network propagation. "
                        "Administrative action is not containment."),
            ("partial", "Log analysis improves understanding of what the malware has done, "
                        "but reviewing logs takes time and the machine remains network-connected "
                        "throughout, allowing continued C2 communication."),
            ("correct", "Network isolation immediately severs the C2 channel and prevents "
                        "lateral movement. The machine is preserved for forensic analysis "
                        "while the blast radius is contained. This is the textbook response."),
        ],
    },
    "communication": {
        "time": "09:25 UTC",
        "title": "Stage 4 — Communication & Data Loss",
        "context": (
            "A DLP alert has fired. Over 4GB of data has been transferred outbound from an "
            "internal workstation associated with the compromised account to an unclassified "
            "external IP. The transfer is ongoing."
        ),
        "options": ["Continue monitoring to gather more intelligence", "Initiate forensic imaging of the endpoint", "Block the outbound traffic immediately"],
        "scores":  [6, 14, 20],
        "analysis": [
            ("poor",    "Passive monitoring during an active exfiltration event is indefensible. "
                        "Every second of delay increases the volume of data lost and the "
                        "regulatory and reputational exposure for the organisation."),
            ("partial", "Forensic imaging preserves evidence and is critical for post-incident "
                        "review and legal proceedings — but it takes 20–60 minutes. "
                        "Exfiltration must be stopped first; forensics follows containment."),
            ("correct", "Blocking outbound traffic to the destination IP stops the exfiltration "
                        "immediately. This is the correct priority — stop the bleed first, "
                        "then preserve evidence. Firewall rules can be applied in seconds."),
        ],
    },
    "recovery": {
        "time": "10:00 UTC",
        "title": "Stage 5 — Recovery & Governance",
        "context": (
            "Systems have been cleaned and backups verified. Management is applying pressure "
            "to restore services immediately. Before resuming operations, you must identify "
            "the first governance priority."
        ),
        "options": ["Delay restoration — further monitoring needed", "Brief executive leadership", "Engage legal and compliance teams", "Notify affected customers directly"],
        "scores":  [5, 14, 20, 10],
        "analysis": [
            ("partial", "Further monitoring has merit, but indefinite delay without a "
                        "governance decision is not a strategy. It causes business disruption "
                        "without a defined security or legal objective."),
            ("partial", "Briefing executives is a necessary governance step and ensures "
                        "leadership accountability, but without legal and compliance input, "
                        "the organisation may act in breach of its regulatory obligations."),
            ("correct", "Legal and compliance engagement is the first priority. Under GDPR "
                        "(and equivalent frameworks), the organisation may have a 72-hour "
                        "mandatory breach notification window. Legal counsel must determine "
                        "obligations before any public or customer communication is made."),
            ("partial", "Customer notification may be legally required, but communicating "
                        "before legal and compliance have assessed the scope risks inaccurate "
                        "disclosure, regulatory penalties, and unnecessary reputational damage."),
        ],
    },
}

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "stage": -1,
        "name": "",
        "role": "",
        "start_time": datetime.now(),
        "scores": dict.fromkeys(["detection", "response", "containment", "communication", "recovery"], 0),
        "answers": {},
        "answer_indices": {},
        "showed_feedback": dict.fromkeys(["detection", "response", "containment", "communication", "recovery"], False),
        "scenario": random.choice(list(SCENARIOS.keys())),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

STAGE_KEYS = ["detection", "response", "containment", "communication", "recovery"]

def advance():
    st.session_state.stage += 1
    st.rerun()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    if st.session_state.stage < 0:
        return

    with st.sidebar:
        st.markdown("## 🛡️ CGI Tabletop")
        st.markdown("---")

        total = sum(st.session_state.scores.values())
        st.metric("Current Score", f"{total} / 100")

        elapsed = int((datetime.now() - st.session_state.start_time).total_seconds())
        m, s = divmod(elapsed, 60)
        st.metric("Elapsed Time", f"{m:02d}:{s:02d}")

        st.markdown("---")
        st.markdown("**Progress**")

        for i, (key, label) in enumerate(zip(STAGE_KEYS, STAGES)):
            stage_score = st.session_state.scores[key]
            max_scores = [20, 20, 20, 20, 20]
            max_s = max_scores[i]

            if st.session_state.stage > i:
                st.markdown(f"✅ **{label}** &nbsp; `{stage_score}/{max_s}`")
            elif st.session_state.stage == i:
                st.markdown(f"🟡 **{label}** &nbsp; *(active)*")
            else:
                st.markdown(f"⬜ {label}")

        if st.session_state.name:
            st.markdown("---")
            st.markdown(f"👤 **{st.session_state.name}**")
            if st.session_state.role:
                st.markdown(f"🏷️ *{st.session_state.role}*")

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="header-banner">
        <h1>🛡️ CGI Cybersecurity Tabletop Exercise</h1>
        <p>Incident Response & Decision-Making Simulation &nbsp;|&nbsp; Confidential — Training Use Only</p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FEEDBACK RENDERER
# ─────────────────────────────────────────────
def render_feedback(stage_key, answer_idx):
    quality, text = QUESTIONS[stage_key]["analysis"][answer_idx]
    css_class = {
        "correct": "feedback-correct",
        "partial": "feedback-partial",
        "poor":    "feedback-poor",
    }[quality]
    icons = {"correct": "✅", "partial": "⚠️", "poor": "❌"}
    score = QUESTIONS[stage_key]["scores"][answer_idx]
    max_s = max(QUESTIONS[stage_key]["scores"])

    st.markdown(f"""
    <div class="feedback-box {css_class}">
        <strong>{icons[quality]} Impact Analysis &nbsp;|&nbsp; Score: {score}/{max_s}</strong><br><br>
        {text}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  STAGE RENDERER
# ─────────────────────────────────────────────
def render_stage(stage_idx):
    render_sidebar()
    render_header()

    key = STAGE_KEYS[stage_idx]
    q   = QUESTIONS[key]
    sc  = SCENARIOS[st.session_state.scenario]

    artifact_map = {
        "detection":     sc["detection_email"],
        "response":      sc["siem_log"],
        "containment":   sc["email_header"],
        "communication": sc["network_alert"],
        "recovery":      None,
    }

    st.markdown(f"""
    <div class="stage-card">
        <h3>{q['title']}</h3>
        <div class="timestamp">⏱ {q['time']} — Simulated incident timeline</div>
        <p>{q['context']}</p>
    </div>
    """, unsafe_allow_html=True)

    if artifact_map[key]:
        st.code(artifact_map[key], language="text")

    already_answered = st.session_state.showed_feedback[key]

    with st.form(key=f"form_{key}"):
        choice = st.radio(
            "**Select your response:**",
            q["options"],
            index=None,
            disabled=already_answered,
        )
        submitted = st.form_submit_button(
            "Submit Decision" if not already_answered else "Decision Submitted",
            disabled=already_answered,
        )

    if submitted and choice and not already_answered:
        idx = q["options"].index(choice)
        st.session_state.scores[key]          = q["scores"][idx]
        st.session_state.answers[key]         = choice
        st.session_state.answer_indices[key]  = idx
        st.session_state.showed_feedback[key] = True
        st.rerun()

    if already_answered:
        render_feedback(key, st.session_state.answer_indices[key])
        st.button("Continue to Next Stage →", on_click=advance)

# ─────────────────────────────────────────────
#  PDF REPORT
# ─────────────────────────────────────────────
def generate_pdf(total, classification, colour_hex):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm,  bottomMargin=20*mm,
    )
    styles = getSampleStyleSheet()
    accent = colors.HexColor(colour_hex)

    title_style = ParagraphStyle(
        "Title2", parent=styles["Title"],
        textColor=accent, fontSize=20, spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "H2a", parent=styles["Heading2"],
        textColor=accent, fontSize=13, spaceBefore=14, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body2", parent=styles["Normal"],
        fontSize=10, leading=15, spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#888888"),
    )

    story = []

    story.append(Paragraph("CGI Cybersecurity Tabletop Exercise", title_style))
    story.append(Paragraph("Incident Response Simulation — Confidential Report", label_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent, spaceAfter=12))

    meta = [
        ["Participant", st.session_state.name],
        ["Role / Team",  st.session_state.role or "Not specified"],
        ["Completed",    datetime.now().strftime("%d %B %Y, %H:%M UTC")],
        ["Total Score",  f"{total} / 100"],
        ["Classification", classification],
    ]
    t = Table(meta, colWidths=[45*mm, 120*mm])
    t.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",   (0, 0), (0, -1),  colors.HexColor("#888888")),
        ("TEXTCOLOR",   (1, 0), (1, -1),  colors.black),
        ("FONTNAME",    (1, 3), (1, 4),   "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Score breakdown table
    story.append(Paragraph("Score Breakdown", h2_style))
    score_data = [["Stage", "Your Decision", "Score", "Max"]]
    for key, label in zip(STAGE_KEYS, STAGES):
        score_data.append([
            label,
            st.session_state.answers.get(key, "—"),
            str(st.session_state.scores[key]),
            "20",
        ])
    score_data.append(["TOTAL", "", str(total), "100"])

    st2 = Table(score_data, colWidths=[35*mm, 95*mm, 15*mm, 15*mm])
    st2.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  accent),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",     (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.HexColor("#f9f9f9"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(st2)
    story.append(Spacer(1, 16))

    # Per-stage analysis
    story.append(Paragraph("Stage-by-Stage Analysis", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=8))

    for key, label in zip(STAGE_KEYS, STAGES):
        answer    = st.session_state.answers.get(key, "No answer recorded")
        ans_idx   = st.session_state.answer_indices.get(key, 0)
        quality, analysis_text = QUESTIONS[key]["analysis"][ans_idx]
        score     = st.session_state.scores[key]

        quality_label = {"correct": "✓ Optimal", "partial": "~ Adequate", "poor": "✗ Insufficient"}[quality]
        quality_colour = {"correct": colors.HexColor("#238636"), "partial": colors.HexColor("#9e6a03"), "poor": colors.HexColor("#da3633")}[quality]

        story.append(Paragraph(f"{label} Stage", h2_style))

        detail = [
            ["Decision Made", answer],
            ["Assessment",    quality_label],
            ["Points Awarded", f"{score} / 20"],
        ]
        dt = Table(detail, colWidths=[38*mm, 122*mm])
        dt.setStyle(TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",  (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (1, 1), (1, 1),   quality_colour),
            ("FONTNAME",  (1, 1), (1, 1),   "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ]))
        story.append(dt)
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Impact Analysis:</b> {analysis_text}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#eeeeee"), spaceAfter=6))

    # Recommendations
    story.append(Paragraph("Recommendations", h2_style))
    recs = {
        "Incident Response Ready": (
            "Your decisions demonstrate strong incident response maturity. "
            "Focus on maintaining tabletop exercises quarterly, refining runbooks, "
            "and expanding threat simulation coverage to advanced persistent threat scenarios."
        ),
        "Operationally Aware": (
            "You show solid awareness but have gaps in one or more critical stages. "
            "Review your organisation's IR playbooks, particularly around containment sequencing "
            "and legal/compliance notification timelines. Consider a dedicated IR retainer."
        ),
        "Needs Procedural Reinforcement": (
            "Several decisions indicate procedural gaps that could lead to significant breach "
            "impact in a real incident. Prioritise formal IR training, implement SIEM alert "
            "response runbooks, and establish clear escalation paths for security events."
        ),
        "High Organisational Risk Profile": (
            "This result indicates significant exposure. Immediate steps should include "
            "formal IR training for all relevant staff, engagement with an MSSP or IR retainer, "
            "development of a documented incident response plan, and a full security posture review."
        ),
    }
    story.append(Paragraph(recs[classification], body_style))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=accent, spaceAfter=6))
    story.append(Paragraph(
        "This report is confidential and produced for training purposes only. "
        "CGI Group Inc. — Cybersecurity Practice.",
        label_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

def classify(score):
    if score >= 90: return ("Incident Response Ready",    "#238636")
    if score >= 70: return ("Operationally Aware",        "#2ea043")
    if score >= 50: return ("Needs Procedural Reinforcement", "#9e6a03")
    return           ("High Organisational Risk Profile", "#da3633")

# ─────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────

# ── WELCOME ──
if st.session_state.stage == -1:
    render_header()

    st.markdown("""
    <div class="stage-card">
        <h3>Exercise Overview</h3>
        <div class="timestamp">Simulated Scenario — Internal Training</div>
        <p>
        You are a cybersecurity analyst responding to a live incident. 
        Over five stages — <strong>Detection, Response, Containment, Communication,</strong> and <strong>Recovery</strong> — 
        you will receive real-time threat artefacts and must make decisions under pressure.<br><br>
        Each decision is scored and analysed. A full PDF report will be generated on completion.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="e.g. Jane Wilson")
    with col2:
        role = st.text_input("Role / Team (optional)", placeholder="e.g. SOC Analyst")

    if st.button("Begin Exercise →"):
        if name.strip():
            st.session_state.name = name.strip()
            st.session_state.role = role.strip()
            advance()
        else:
            st.warning("Please enter your name to begin.")

# ── STAGES 0–4 ──
elif 0 <= st.session_state.stage <= 4:
    render_stage(st.session_state.stage)

# ── REPORT ──
elif st.session_state.stage == 5:
    render_sidebar()
    render_header()

    total = sum(st.session_state.scores.values())
    classification, colour = classify(total)

    st.markdown(f"""
    <div class="result-card">
        <div class="big-score">{total}<span style="font-size:1.5rem;color:#8b949e">/100</span></div>
        <div class="classification" style="color:{colour}">{classification}</div>
        <div class="sub">Exercise completed by {st.session_state.name} &nbsp;|&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M UTC")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Decision Summary")
    for key, label in zip(STAGE_KEYS, STAGES):
        score   = st.session_state.scores[key]
        answer  = st.session_state.answers.get(key, "—")
        ans_idx = st.session_state.answer_indices.get(key, 0)
        quality = QUESTIONS[key]["analysis"][ans_idx][0]
        icon    = {"correct": "✅", "partial": "⚠️", "poor": "❌"}[quality]
        st.markdown(f"""
        <div class="decision-row">
            <span>{icon} <strong>{label}</strong> — {answer}</span>
            <span style="color:#58a6ff;font-weight:700">{score}/20</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    pdf = generate_pdf(total, classification, colour)
    st.download_button(
        label="📄 Download Full PDF Report",
        data=pdf,
        file_name=f"tabletop_report_{st.session_state.name.replace(' ','_')}.pdf",
        mime="application/pdf",
    )

    if st.button("🔄 Restart Exercise"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        
