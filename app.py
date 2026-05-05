import streamlit as st
import random
import time
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CGI Cyber Tabletop Exercise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette (Cosmic Artistry) ──
C1  = "#212A31"   # dark navy
C2  = "#2E3944"   # deep teal-grey
C3  = "#124E66"   # vivid teal
C4  = "#748D92"   # muted blue-grey
C5  = "#D3D9D4"   # light grey
CGI_RED = "#DC1431"

# ─────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────
def get_logo_base64():
    try:
        with open("cgi_logo.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

LOGO_B64 = get_logo_base64()

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body {{
    background-color: {C1} !important;
    color: {C5} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main {{
    background-color: {C1} !important;
    font-family: 'Inter', sans-serif !important;
}}
.block-container {{
    max-width: 860px;
    padding: 2rem 2rem 4rem;
    margin: auto;
    background-color: {C1} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {C2} !important;
    border-right: 2px solid {C3} !important;
}}
[data-testid="stSidebar"] * {{
    color: {C5} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] strong {{
    color: #ffffff !important;
}}
[data-testid="stMetricValue"] > div {{
    color: #ffffff !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {C4} !important;
}}
[data-testid="stSidebarNav"] {{ display: none !important; }}

/* ── General text ── */
p, span, div, label, li {{
    font-family: 'Inter', sans-serif !important;
    color: {C5};
}}
h1, h2, h3, h4 {{
    font-family: 'Inter', sans-serif !important;
    color: #ffffff;
}}
[data-testid="stMarkdownContainer"] p {{
    color: {C5} !important;
}}
[data-testid="stMarkdownContainer"] strong {{
    color: #ffffff !important;
}}

/* ── Header banner ── */
.header-banner {{
    background: linear-gradient(120deg, {C2} 0%, {C3} 100%);
    border: 1px solid {C3};
    border-top: 5px solid {CGI_RED};
    border-radius: 14px;
    padding: 1.6rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}}
.header-text h1 {{
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 0.2rem;
}}
.header-text p {{
    font-size: 0.85rem;
    color: {C5} !important;
    margin: 0;
}}

/* ── Stage card ── */
.stage-card {{
    background: {C2};
    border: 1px solid {C3};
    border-left: 5px solid {CGI_RED};
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}}
.stage-card h3 {{
    color: {CGI_RED} !important;
    margin: 0 0 0.4rem;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.stage-card .timestamp {{
    color: #f59e0b !important;
    font-size: 0.82rem;
    font-family: monospace;
    margin-bottom: 0.8rem;
    font-weight: 600;
}}
.stage-card p {{
    color: {C5} !important;
    font-size: 0.94rem;
    line-height: 1.7;
    margin: 0;
}}

/* ── MITRE tag ── */
.mitre-tag {{
    display: inline-block;
    background: {C3};
    border: 1.5px solid {C4};
    color: #ffffff !important;
    border-radius: 6px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-family: monospace;
    margin-bottom: 1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}}

/* ── Feedback boxes ── */
.feedback-box {{
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.92rem;
    line-height: 1.7;
}}
.feedback-correct {{
    background: #0d3320;
    border: 1.5px solid #34d399;
    color: #6ee7b7 !important;
}}
.feedback-partial {{
    background: #2d2000;
    border: 1.5px solid #fbbf24;
    color: #fde68a !important;
}}
.feedback-poor {{
    background: #2d0a0a;
    border: 1.5px solid {CGI_RED};
    color: #fca5a5 !important;
}}

/* ── Timer ── */
.timer-box {{
    background: {C2};
    border: 1.5px solid {C3};
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-size: 1rem;
    font-family: monospace;
    color: #ffffff !important;
    margin-bottom: 1.2rem;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-weight: 700;
}}
.timer-warning {{ color: #fbbf24 !important; font-weight: 800; }}
.timer-critical {{ color: {CGI_RED} !important; font-weight: 800; }}

/* ── Result card ── */
.result-card {{
    background: {C2};
    border: 1px solid {C3};
    border-radius: 14px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}}
.result-card .big-score {{
    font-size: 4.5rem;
    font-weight: 800;
    color: {CGI_RED} !important;
    line-height: 1;
}}
.result-card .classification {{
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 0.6rem;
    color: #ffffff !important;
}}
.result-card .sub {{
    font-size: 0.88rem;
    color: {C4} !important;
    margin-top: 0.4rem;
}}

/* ── Decision rows ── */
.decision-row {{
    background: {C2};
    border: 1px solid {C3};
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: {C5} !important;
}}

/* ── Certificate banner ── */
.cert-banner {{
    background: linear-gradient(135deg, {C2} 0%, {C3} 100%);
    border: 2px solid {CGI_RED};
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}}
.cert-banner h2 {{
    color: #ffffff !important;
    font-size: 1.4rem;
    margin: 0 0 0.5rem;
    font-weight: 800;
}}
.cert-banner p {{
    color: {C5} !important;
    margin: 0;
    font-size: 0.95rem;
}}

/* ── Streamlit widgets ── */
div[data-testid="stForm"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}
.stRadio label,
.stRadio > div > label {{
    color: {C5} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}}
.stRadio > div {{
    gap: 0.5rem;
}}

/* ── Button fix — ensure text is always visible ── */
.stButton > button,
.stButton > button p,
.stButton > button span,
.stFormSubmitButton > button,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span {{
    background: {CGI_RED} !important;
    background-color: {CGI_RED} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 2rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 2px 8px rgba(220,20,49,0.4) !important;
}}
.stButton > button:hover,
.stFormSubmitButton > button:hover {{
    background: #b01228 !important;
    background-color: #b01228 !important;
    color: #ffffff !important;
}}
.stButton > button:disabled,
.stFormSubmitButton > button:disabled {{
    background: {C3} !important;
    background-color: {C3} !important;
    color: {C4} !important;
    opacity: 0.7 !important;
}}

/* ── Download button ── */
.stDownloadButton > button,
.stDownloadButton > button p {{
    background: {C3} !important;
    color: #ffffff !important;
    border: 1px solid {C4} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stDownloadButton > button:hover {{
    background: {C2} !important;
    border-color: #ffffff !important;
}}

/* ── Text input ── */
.stTextInput > div > div > input {{
    background: {C2} !important;
    color: #ffffff !important;
    border: 1.5px solid {C3} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTextInput label,
.stTextInput > label {{
    color: {C5} !important;
    font-weight: 600 !important;
}}

/* ── Code blocks ── */
code, pre, .stCode {{
    background: {C2} !important;
    border: 1px solid {C3} !important;
    border-radius: 8px !important;
    color: {C5} !important;
    font-size: 0.85rem !important;
}}

/* ── Alert / info ── */
[data-testid="stAlert"] {{
    background: {C2} !important;
    border: 1px solid {C3} !important;
    color: {C5} !important;
    border-radius: 8px !important;
}}

hr {{ border-color: {C3} !important; }}

/* ── Hide the keyboard_double icon / deploy button ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
header[data-testid="stHeader"] {{
    display: none !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MITRE ATT&CK TAGS
# ─────────────────────────────────────────────
MITRE_TAGS = {
    "detection":     ("T1566.001", "Spearphishing Attachment"),
    "response":      ("T1078",     "Valid Accounts"),
    "containment":   ("T1059.001", "PowerShell / Macro Execution"),
    "communication": ("T1041",     "Exfiltration Over C2 Channel"),
    "recovery":      ("T1486",     "Post-Incident Governance"),
}

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

STAGES     = ["Detection", "Response", "Containment", "Communication", "Recovery"]
STAGE_KEYS = ["detection", "response", "containment", "communication", "recovery"]
TIMER_SECS = 60

QUESTIONS = {
    "detection": {
        "time": "08:42 UTC",
        "title": "Stage 1 — Threat Detection",
        "context": (
            "A member of staff has forwarded a suspicious email to the shared security inbox. "
            "You are the on-call analyst. Review the artefact below and decide how to proceed. "
            "This email exhibits hallmarks of a MITRE ATT&CK T1566.001 spearphishing attachment campaign."
        ),
        "options": ["Ignore — likely spam", "Escalate to IT helpdesk", "Inspect headers and analyse the link"],
        "scores":  [4, 12, 20],
        "analysis": [
            ("poor",    "Ignoring phishing indicators leaves the attacker undetected. "
                        "Credential harvesting links in spearphishing campaigns (T1566.001) are crafted to "
                        "appear legitimate — dismissing without analysis allows initial access to succeed."),
            ("partial", "Escalating to IT reduces dwell time before credential compromise "
                        "and is better than no action. However, generic helpdesk staff may "
                        "lack the tooling to perform header or URL analysis effectively."),
            ("correct", "Inspecting mail headers exposes spoofed sender domains and relay "
                        "chains consistent with T1566.001 TTPs. Sandboxing or safely expanding the URL reveals phishing "
                        "infrastructure. This is the correct first technical response — "
                        "it produces evidence and prevents credential harvesting."),
        ],
    },
    "response": {
        "time": "08:55 UTC",
        "title": "Stage 2 — Incident Response",
        "context": (
            "Your SIEM has triggered a high-severity alert. A company account has authenticated "
            "successfully from an unusual foreign IP with no prior failed attempts. "
            "This is consistent with T1078 (Valid Accounts) — the attacker is using harvested credentials. "
            "A session is currently active."
        ),
        "options": ["Ignore — could be a VPN or traveller", "Force password reset", "Investigate the active session scope", "Immediately disable the account"],
        "scores":  [3, 10, 15, 20],
        "analysis": [
            ("poor",    "Dismissing a successful foreign login without MFA as a VPN artefact "
                        "is a critical error. The attacker session remains active and can "
                        "begin lateral movement or data access immediately, consistent with T1078 abuse."),
            ("partial", "A password reset invalidates credentials but does NOT terminate an "
                        "existing session token. An attacker already authenticated may retain "
                        "access until the session expires — typically hours."),
            ("partial", "Scoping the session — checking what resources were accessed, what "
                        "data was read, and whether privilege escalation occurred — is a "
                        "sound investigative step, but delays direct containment."),
            ("correct", "Disabling the account immediately terminates all active sessions "
                        "and prevents re-authentication. This is the fastest containment "
                        "action against T1078 and is fully reversible once the incident is scoped."),
        ],
    },
    "containment": {
        "time": "09:10 UTC",
        "title": "Stage 3 — Containment",
        "context": (
            "A macro-enabled attachment has been opened on an internal workstation. "
            "Gateway sandbox analysis detected an outbound callback attempt — "
            "this is consistent with T1059.001 (PowerShell/macro execution) used to establish C2. "
            "The machine is currently live on the network."
        ),
        "options": ["Wait for antivirus scan to complete", "Notify IT and log the ticket", "Pull and review endpoint logs", "Immediately isolate the machine from the network"],
        "scores":  [4, 10, 14, 20],
        "analysis": [
            ("poor",    "Waiting for AV to complete while a live C2 beacon is active allows "
                        "the attacker to download second-stage payloads and establish persistence "
                        "via T1059.001 macros — a common next step in spearphishing kill chains."),
            ("partial", "Logging a ticket initiates a paper trail and involves IT, but does "
                        "nothing to stop active macro execution or network propagation. "
                        "Administrative action is not containment."),
            ("partial", "Log analysis improves understanding of what the macro has executed, "
                        "but reviewing logs takes time and the machine remains network-connected "
                        "throughout, allowing continued C2 communication."),
            ("correct", "Network isolation immediately severs the C2 channel established via "
                        "T1059.001 macro execution and prevents lateral movement. "
                        "The machine is preserved for forensic analysis while the blast radius is contained."),
        ],
    },
    "communication": {
        "time": "09:25 UTC",
        "title": "Stage 4 — Communication & Data Loss",
        "context": (
            "A DLP alert has fired. Over 4GB of data has been transferred outbound from an "
            "internal workstation to an unclassified external IP. "
            "This is consistent with T1041 — Exfiltration Over C2 Channel, "
            "a common final-stage action in spearphishing campaigns. The transfer is ongoing."
        ),
        "options": ["Continue monitoring to gather more intelligence", "Initiate forensic imaging of the endpoint", "Block the outbound traffic immediately"],
        "scores":  [6, 14, 20],
        "analysis": [
            ("poor",    "Passive monitoring during an active T1041 exfiltration event is indefensible. "
                        "Every second of delay increases the volume of data lost and the "
                        "regulatory and reputational exposure for the organisation."),
            ("partial", "Forensic imaging preserves evidence and is critical for post-incident "
                        "review and legal proceedings — but it takes 20–60 minutes. "
                        "Exfiltration must be stopped first; forensics follows containment."),
            ("correct", "Blocking outbound traffic to the destination IP stops the T1041 exfiltration "
                        "immediately. This is the correct priority — stop the bleed first, "
                        "then preserve evidence. Firewall rules can be applied in seconds."),
        ],
    },
    "recovery": {
        "time": "10:00 UTC",
        "title": "Stage 5 — Recovery & Governance",
        "context": (
            "Systems have been cleaned and backups verified following the spearphishing compromise. "
            "The full attack chain — T1566.001 → T1078 → T1059.001 → T1041 — has been documented. "
            "Management is applying pressure to restore services immediately. "
            "Identify the first governance priority before resuming operations."
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
                        "mandatory breach notification window following a spearphishing-induced breach. "
                        "Legal counsel must determine obligations before any public communication."),
            ("partial", "Customer notification may be legally required, but communicating "
                        "before legal and compliance have assessed the scope risks inaccurate "
                        "disclosure, regulatory penalties, and unnecessary reputational damage."),
        ],
    },
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def build_shuffled_orders():
    orders = {}
    for key, q in QUESTIONS.items():
        idx = list(range(len(q["options"])))
        random.shuffle(idx)
        orders[key] = idx
    return orders

def init_state():
    defaults = {
        "stage": -1,
        "name": "",
        "role": "",
        "start_time": datetime.now(),
        "scores": dict.fromkeys(STAGE_KEYS, 0),
        "answers": {},
        "answer_indices": {},
        "showed_feedback": dict.fromkeys(STAGE_KEYS, False),
        "scenario": random.choice(list(SCENARIOS.keys())),
        "shuffled_orders": build_shuffled_orders(),
        "stage_start_time": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

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
            sc = st.session_state.scores[key]
            if st.session_state.stage > i:
                st.markdown(f"✅ **{label}** &nbsp; `{sc}/20`")
            elif st.session_state.stage == i:
                st.markdown(f"🟡 **{label}** &nbsp; *(active)*")
            else:
                st.markdown(f"⬜ {label}")
        st.markdown("---")
        st.markdown("**Attack Path**")
        st.markdown("MITRE ATT&CK — Spearphishing")
        for key in STAGE_KEYS:
            tid, tname = MITRE_TAGS[key]
            done   = st.session_state.stage > STAGE_KEYS.index(key)
            active = st.session_state.stage == STAGE_KEYS.index(key)
            prefix = "✅" if done else ("🟡" if active else "⬜")
            st.markdown(f"{prefix} `{tid}` {tname}")
        if st.session_state.name:
            st.markdown("---")
            st.markdown(f"👤 **{st.session_state.name}**")
            if st.session_state.role:
                st.markdown(f"🏷️ *{st.session_state.role}*")

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
def render_header():
    if LOGO_B64:
        logo_html = f'<img src="data:image/jpeg;base64,{LOGO_B64}" style="height:52px;border-radius:8px;" alt="CGI"/>'
    else:
        logo_html = f'<div style="font-size:2rem;font-weight:900;color:#ffffff;letter-spacing:-0.05em;">CGI</div>'
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-text">
            <h1>Cybersecurity Tabletop Exercise</h1>
            <p>Spearphishing Incident Response Simulation &nbsp;|&nbsp; Confidential — Training Use Only</p>
        </div>
        <div>{logo_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FEEDBACK
# ─────────────────────────────────────────────
def render_feedback(stage_key, answer_idx):
    quality, text = QUESTIONS[stage_key]["analysis"][answer_idx]
    css   = {"correct": "feedback-correct", "partial": "feedback-partial", "poor": "feedback-poor"}[quality]
    icons = {"correct": "✅", "partial": "⚠️", "poor": "❌"}
    score = QUESTIONS[stage_key]["scores"][answer_idx]
    max_s = max(QUESTIONS[stage_key]["scores"])
    st.markdown(f"""
    <div class="feedback-box {css}">
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

    key        = STAGE_KEYS[stage_idx]
    q          = QUESTIONS[key]
    sc         = SCENARIOS[st.session_state.scenario]
    tid, tname = MITRE_TAGS[key]

    artifact_map = {
        "detection":     sc["detection_email"],
        "response":      sc["siem_log"],
        "containment":   sc["email_header"],
        "communication": sc["network_alert"],
        "recovery":      None,
    }

    st.markdown(f'<div class="mitre-tag">MITRE ATT&CK &nbsp;·&nbsp; {tid} — {tname}</div>', unsafe_allow_html=True)
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
    order            = st.session_state.shuffled_orders[key]
    shuffled_options = [q["options"][i] for i in order]

    if already_answered:
        render_feedback(key, st.session_state.answer_indices[key])
        st.button("Continue to Next Stage →", on_click=advance)
        return

    # Timer placeholder
    timer_ph = st.empty()

    with st.form(key=f"form_{key}"):
        choice    = st.radio("**Select your response:**", shuffled_options, index=None)
        submitted = st.form_submit_button("Submit Decision")

    if submitted and choice:
        original_idx = order[shuffled_options.index(choice)]
        st.session_state.scores[key]          = q["scores"][original_idx]
        st.session_state.answers[key]         = choice
        st.session_state.answer_indices[key]  = original_idx
        st.session_state.showed_feedback[key] = True
        st.rerun()

    # Live countdown loop
    if key not in st.session_state.stage_start_time:
        st.session_state.stage_start_time[key] = time.time()

    while True:
        elapsed   = time.time() - st.session_state.stage_start_time[key]
        remaining = max(0, TIMER_SECS - int(elapsed))
        m2, s2    = divmod(remaining, 60)
        css_class = "timer-critical" if remaining <= 10 else ("timer-warning" if remaining <= 20 else "")
        timer_ph.markdown(f"""
        <div class="timer-box">
            ⏱ Time Remaining: <span class="{css_class}">{m2:02d}:{s2:02d}</span>
        </div>
        """, unsafe_allow_html=True)

        if remaining == 0:
            worst = min(range(len(q["scores"])), key=lambda i: q["scores"][i])
            st.session_state.scores[key]          = q["scores"][worst]
            st.session_state.answers[key]         = "⏰ Time expired — no decision made"
            st.session_state.answer_indices[key]  = worst
            st.session_state.showed_feedback[key] = True
            st.rerun()
        time.sleep(1)

# ─────────────────────────────────────────────
#  PDF — CERTIFICATE
# ─────────────────────────────────────────────
def generate_certificate(name, role, score, classification):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               leftMargin=25*mm, rightMargin=25*mm,
                               topMargin=20*mm,  bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    r      = colors.HexColor(CGI_RED)
    navy   = colors.HexColor(C1)
    teal   = colors.HexColor(C3)
    light  = colors.HexColor(C5)

    story = [Spacer(1, 10*mm)]

    border_data = [[Paragraph(f"""
        <para align="center">
        <font size="28" color="{CGI_RED}"><b>Certificate of Completion</b></font><br/><br/>
        <font size="11" color="{C4}">CGI Cybersecurity Tabletop Exercise</font><br/>
        <font size="10" color="{C4}">Spearphishing Incident Response Simulation</font><br/><br/>
        <font size="11" color="{C5}">This certifies that</font><br/><br/>
        <font size="24" color="#ffffff"><b>{name}</b></font><br/>
        <font size="10" color="{C4}">{role if role else 'Participant'}</font><br/><br/>
        <font size="11" color="{C5}">has successfully completed the exercise with a score of</font><br/><br/>
        <font size="32" color="{CGI_RED}"><b>{score}/100</b></font><br/>
        <font size="13" color="#ffffff"><b>{classification}</b></font><br/><br/>
        <font size="10" color="{C4}">Completed: {datetime.now().strftime('%d %B %Y')}</font><br/>
        <font size="10" color="{C4}">MITRE ATT&amp;CK Framework — Spearphishing Kill Chain (T1566.001)</font><br/><br/>
        <font size="9" color="{C4}">Issued by CGI Cybersecurity Practice &nbsp;|&nbsp; Confidential — Training Use Only</font><br/>
        <font size="9" color="{C4}">Developed by 5yber &nbsp;|&nbsp; Delivered in partnership with CGI Cybersecurity Practice</font>
        </para>
    """, styles["Normal"])]]

    bt = Table(border_data, colWidths=[160*mm])
    bt.setStyle(TableStyle([
        ("BOX",           (0,0), (-1,-1), 3,  r),
        ("BACKGROUND",    (0,0), (-1,-1),     colors.HexColor(C2)),
        ("TOPPADDING",    (0,0), (-1,-1), 24),
        ("BOTTOMPADDING", (0,0), (-1,-1), 24),
        ("LEFTPADDING",   (0,0), (-1,-1), 24),
        ("RIGHTPADDING",  (0,0), (-1,-1), 24),
    ]))
    story.append(bt)
    doc.build(story)
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────
#  PDF — REPORT
# ─────────────────────────────────────────────
def generate_pdf(total, classification):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               leftMargin=20*mm, rightMargin=20*mm,
                               topMargin=20*mm,  bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    r      = colors.HexColor(CGI_RED)
    c1     = colors.HexColor(C1)
    c2     = colors.HexColor(C2)
    c3     = colors.HexColor(C3)
    c4     = colors.HexColor(C4)
    c5     = colors.HexColor(C5)
    white  = colors.white

    title_style = ParagraphStyle("T2",  parent=styles["Title"],
                                  textColor=r,     fontSize=20, spaceAfter=4)
    h2_style    = ParagraphStyle("H2a", parent=styles["Heading2"],
                                  textColor=r,     fontSize=13, spaceBefore=14, spaceAfter=4)
    body_style  = ParagraphStyle("B2",  parent=styles["Normal"],
                                  textColor=c5,    fontSize=10, leading=15, spaceAfter=4)
    label_style = ParagraphStyle("Lb",  parent=styles["Normal"],
                                  textColor=c4,    fontSize=9)

    story = []
    story.append(Paragraph("CGI Cybersecurity Tabletop Exercise", title_style))
    story.append(Paragraph("Spearphishing Incident Response Simulation — Confidential Report", label_style))
    story.append(HRFlowable(width="100%", thickness=2, color=r, spaceAfter=12))

    meta = [
        ["Participant",     st.session_state.name],
        ["Role / Team",     st.session_state.role or "Not specified"],
        ["Completed",       datetime.now().strftime("%d %B %Y, %H:%M UTC")],
        ["Attack Scenario", "Spearphishing — MITRE ATT&CK T1566.001 Kill Chain"],
        ["Total Score",     f"{total} / 100"],
        ["Classification",  classification],
    ]
    t = Table(meta, colWidths=[50*mm, 120*mm])
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("TEXTCOLOR",     (0,0), (0,-1),  c4),
        ("TEXTCOLOR",     (1,0), (1,-1),  c5),
        ("FONTNAME",      (1,4), (1,5),   "Helvetica-Bold"),
        ("BACKGROUND",    (0,0), (-1,-1), c1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    story.append(Paragraph("MITRE ATT&CK Spearphishing Kill Chain", h2_style))
    chain_data = [["Stage", "Technique ID", "Technique Name", "Score", "Max"]]
    for key, label in zip(STAGE_KEYS, STAGES):
        tid, tname = MITRE_TAGS[key]
        chain_data.append([label, tid, tname, str(st.session_state.scores[key]), "20"])
    chain_data.append(["TOTAL", "", "", str(total), "100"])
    ct = Table(chain_data, colWidths=[28*mm, 22*mm, 80*mm, 14*mm, 14*mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  c3),
        ("TEXTCOLOR",     (0,0), (-1,0),  white),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,-1),(-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (-1,-1), c5),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [c2, c1]),
        ("GRID",          (0,0), (-1,-1), 0.5, c3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(ct)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Stage-by-Stage Analysis", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c3, spaceAfter=8))

    for key, label in zip(STAGE_KEYS, STAGES):
        answer             = st.session_state.answers.get(key, "No answer recorded")
        ans_idx            = st.session_state.answer_indices.get(key, 0)
        quality, analysis_text = QUESTIONS[key]["analysis"][ans_idx]
        score              = st.session_state.scores[key]
        tid, tname         = MITRE_TAGS[key]

        ql   = {"correct": "✓ Optimal", "partial": "~ Adequate", "poor": "✗ Insufficient"}[quality]
        qcol = {"correct": colors.HexColor("#34d399"),
                "partial": colors.HexColor("#fbbf24"),
                "poor":    colors.HexColor("#f87171")}[quality]

        story.append(Paragraph(f"{label} Stage — {tid}: {tname}", h2_style))
        dt = Table([
            ["Decision Made",  answer],
            ["Assessment",     ql],
            ["Points Awarded", f"{score} / 20"],
        ], colWidths=[38*mm, 122*mm])
        dt.setStyle(TableStyle([
            ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("TEXTCOLOR",     (0,0), (0,-1),  c4),
            ("TEXTCOLOR",     (1,0), (1,0),   c5),
            ("TEXTCOLOR",     (1,1), (1,1),   qcol),
            ("TEXTCOLOR",     (1,2), (1,2),   c5),
            ("FONTNAME",      (1,1), (1,1),   "Helvetica-Bold"),
            ("BACKGROUND",    (0,0), (-1,-1), c2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
        ]))
        story.append(dt)
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Impact Analysis:</b> {analysis_text}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.3, color=c3, spaceAfter=6))

    story.append(Paragraph("Recommendations", h2_style))
    recs = {
        "Incident Response Ready":          "Your decisions demonstrate strong IR maturity across the full spearphishing kill chain. Maintain quarterly tabletops and expand to APT and ransomware scenarios.",
        "Operationally Aware":              "You show solid awareness but have gaps in one or more stages. Review IR playbooks, especially around MITRE T1078 session containment and T1041 exfiltration response.",
        "Needs Procedural Reinforcement":   "Several decisions indicate procedural gaps. Prioritise formal IR training, implement SIEM runbooks aligned to the spearphishing kill chain, and establish clear escalation paths.",
        "High Organisational Risk Profile": "Immediate action required. Engage an MSSP or IR retainer, develop a documented IR plan covering the T1566.001 attack path, and conduct a full security posture review.",
    }
    story.append(Paragraph(recs[classification], body_style))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=r, spaceAfter=6))
    story.append(Paragraph(
        "This report is confidential and produced for training purposes only. CGI Group Inc. — Cybersecurity Practice.",
        label_style))
    story.append(Paragraph(
        "Developed by 5yber | Delivered in partnership with CGI Cybersecurity Practice.",
        label_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def classify(score):
    if score >= 90: return ("Incident Response Ready",          "#34d399")
    if score >= 70: return ("Operationally Aware",              "#34d399")
    if score >= 50: return ("Needs Procedural Reinforcement",   "#fbbf24")
    return                  ("High Organisational Risk Profile", "#f87171")

# ─────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────

# ── WELCOME ──
if st.session_state.stage == -1:
    render_header()
    st.markdown(f"""
    <div class="stage-card">
        <h3>Exercise Overview</h3>
        <div class="timestamp">Simulated Scenario — Internal Training &nbsp;|&nbsp; MITRE ATT&CK Framework</div>
        <p>
        You are a cybersecurity analyst responding to a live spearphishing incident.<br><br>
        Over five stages — <strong>Detection, Response, Containment, Communication,</strong> and <strong>Recovery</strong> —
        you will receive real-time threat artefacts drawn from the MITRE ATT&CK spearphishing kill chain
        (<strong>T1566.001 → T1078 → T1059.001 → T1041</strong>) and must make decisions under a
        <strong>60-second time limit per stage</strong>.<br><br>
        Each decision is scored and analysed. A full PDF report is generated on completion.
        Participants scoring <strong>80 or above</strong> will receive a certificate of completion.
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

# ── STAGES ──
elif 0 <= st.session_state.stage <= 4:
    render_stage(st.session_state.stage)

# ── REPORT ──
elif st.session_state.stage == 5:
    render_sidebar()
    render_header()

    total          = sum(st.session_state.scores.values())
    classification, colour = classify(total)

    st.markdown(f"""
    <div class="result-card">
        <div class="big-score">{total}<span style="font-size:1.5rem;color:{C4}">/100</span></div>
        <div class="classification" style="color:{colour}">{classification}</div>
        <div class="sub">
            {st.session_state.name} &nbsp;|&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M UTC")}<br/>
            MITRE ATT&CK — Spearphishing Kill Chain (T1566.001)
        </div>
    </div>
    """, unsafe_allow_html=True)

    if total >= 80:
        st.markdown(f"""
        <div class="cert-banner">
            <h2>🏆 Certificate Unlocked</h2>
            <p>You scored <strong>{total}/100</strong> — you qualify for a certificate of completion.<br/>
            Download it below alongside your full report.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Decision Summary")
    for key, label in zip(STAGE_KEYS, STAGES):
        score   = st.session_state.scores[key]
        answer  = st.session_state.answers.get(key, "—")
        ans_idx = st.session_state.answer_indices.get(key, 0)
        quality = QUESTIONS[key]["analysis"][ans_idx][0]
        icon    = {"correct": "✅", "partial": "⚠️", "poor": "❌"}[quality]
        tid, _  = MITRE_TAGS[key]
        st.markdown(f"""
        <div class="decision-row">
            <span>{icon} <strong>{label}</strong>
            <span style="color:{C4};font-size:0.8rem">&nbsp;{tid}</span>
            — {answer}</span>
            <span style="color:{CGI_RED};font-weight:700">{score}/20</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        pdf = generate_pdf(total, classification)
        st.download_button(
            label="📄 Download Full Report (PDF)",
            data=pdf,
            file_name=f"CGI_Tabletop_Report_{st.session_state.name.replace(' ','_')}.pdf",
            mime="application/pdf",
        )
    with col2:
        if total >= 80:
            cert = generate_certificate(st.session_state.name, st.session_state.role, total, classification)
            st.download_button(
                label="🏆 Download Certificate (PDF)",
                data=cert,
                file_name=f"CGI_Certificate_{st.session_state.name.replace(' ','_')}.pdf",
                mime="application/pdf",
            )
        else:
            st.info(f"Score 80+ to unlock your certificate. You scored {total}/100.")

    if st.button("🔄 Restart Exercise"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
