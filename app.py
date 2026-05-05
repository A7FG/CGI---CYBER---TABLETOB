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
from reportlab.pdfgen import canvas
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

# ─────────────────────────────────────────────
#  COLOUR PALETTE — Artsy & Creative
# ─────────────────────────────────────────────
GOLD     = "#D79922"
CREAM    = "#EFE2BA"
ORANGE   = "#F13C20"
BLUE     = "#4056A1"
LAVENDER = "#C5CBE3"
CGI_RED  = "#DC1431"

# Derived shades
TEXT_DARK   = "#1a1d2e"
TEXT_MUTED  = "#5a6b7d"
BG_PAGE     = "#fafaf6"
BG_CARD     = "#ffffff"
BORDER_SOFT = "#e6e7eb"

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
    background-color: {BG_PAGE} !important;
    color: {TEXT_DARK} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main {{
    background-color: {BG_PAGE} !important;
    font-family: 'Inter', sans-serif !important;
}}
.block-container {{
    max-width: 860px;
    padding: 2rem 2rem 4rem;
    margin: auto;
    background-color: {BG_PAGE} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {BLUE} !important;
    border-right: 4px solid {GOLD} !important;
}}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li {{
    color: {LAVENDER} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {{
    color: #ffffff !important;
}}
[data-testid="stSidebar"] code {{
    background: rgba(255,255,255,0.15) !important;
    color: {CREAM} !important;
    border: none !important;
    padding: 0.1rem 0.4rem !important;
}}
[data-testid="stMetricValue"] > div {{
    color: {CREAM} !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {LAVENDER} !important;
}}
[data-testid="stSidebarNav"] {{ display: none !important; }}

/* ── Hide sidebar collapse arrow / header decoration ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"],
button[kind="header"],
button[data-testid="baseButton-header"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}}

/* ── Body text ── */
p, span, label, li {{
    font-family: 'Inter', sans-serif !important;
    color: {TEXT_DARK};
}}
h1, h2, h3, h4 {{
    font-family: 'Inter', sans-serif !important;
    color: {TEXT_DARK};
}}
[data-testid="stMarkdownContainer"] p {{
    color: {TEXT_DARK} !important;
}}
[data-testid="stMarkdownContainer"] strong {{
    color: {TEXT_DARK} !important;
    font-weight: 700;
}}

/* ── Header banner ── */
.header-banner {{
    background: linear-gradient(120deg, {BLUE} 0%, #2f4082 100%);
    border: 1px solid {BLUE};
    border-top: 5px solid {ORANGE};
    border-radius: 14px;
    padding: 1.6rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 6px 20px rgba(64,86,161,0.2);
}}
.header-text h1 {{
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 0.2rem;
}}
.header-text p {{
    font-size: 0.85rem;
    color: {LAVENDER} !important;
    margin: 0;
}}

/* ── Stage card ── */
.stage-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SOFT};
    border-left: 5px solid {ORANGE};
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}}
.stage-card h3 {{
    color: {ORANGE} !important;
    margin: 0 0 0.4rem;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.stage-card .timestamp {{
    color: {GOLD} !important;
    font-size: 0.82rem;
    font-family: monospace;
    margin-bottom: 0.8rem;
    font-weight: 700;
}}
.stage-card p {{
    color: {TEXT_DARK} !important;
    font-size: 0.94rem;
    line-height: 1.7;
    margin: 0;
}}

/* ── MITRE tag ── */
.mitre-tag {{
    display: inline-block;
    background: {BLUE};
    border: none;
    color: #ffffff !important;
    border-radius: 6px;
    padding: 0.25rem 0.8rem;
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
    background: #ecfdf5;
    border: 1.5px solid #10b981;
    color: #064e3b !important;
}}
.feedback-correct strong {{ color: #065f46 !important; }}
.feedback-partial {{
    background: {CREAM};
    border: 1.5px solid {GOLD};
    color: #78350f !important;
}}
.feedback-partial strong {{ color: #78350f !important; }}
.feedback-poor {{
    background: #fef2f2;
    border: 1.5px solid {ORANGE};
    color: #7f1d1d !important;
}}
.feedback-poor strong {{ color: #7f1d1d !important; }}

/* ── Timer ── */
.timer-box {{
    background: {BG_CARD};
    border: 1.5px solid {LAVENDER};
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-size: 1rem;
    font-family: monospace;
    color: {TEXT_DARK} !important;
    margin-bottom: 1.2rem;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    font-weight: 700;
}}
.timer-warning {{ color: {GOLD} !important; font-weight: 800; }}
.timer-critical {{ color: {ORANGE} !important; font-weight: 800; }}

/* ── Result card ── */
.result-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SOFT};
    border-radius: 14px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}}
.result-card .big-score {{
    font-size: 4.5rem;
    font-weight: 800;
    color: {ORANGE} !important;
    line-height: 1;
}}
.result-card .classification {{
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 0.6rem;
}}
.result-card .sub {{
    font-size: 0.88rem;
    color: {TEXT_MUTED} !important;
    margin-top: 0.4rem;
}}

/* ── Decision rows ── */
.decision-row {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SOFT};
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: {TEXT_DARK} !important;
}}

/* ── Certificate banner ── */
.cert-banner {{
    background: linear-gradient(135deg, {CREAM} 0%, #f4ecc9 100%);
    border: 2px solid {GOLD};
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}}
.cert-banner h2 {{
    color: {ORANGE} !important;
    font-size: 1.4rem;
    margin: 0 0 0.5rem;
    font-weight: 800;
}}
.cert-banner p {{
    color: #78350f !important;
    margin: 0;
    font-size: 0.95rem;
}}

/* ── Streamlit form ── */
div[data-testid="stForm"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}
.stRadio label,
.stRadio > div > label {{
    color: {TEXT_DARK} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}}
.stRadio > div {{ gap: 0.5rem; }}

/* ── Buttons (Submit / Begin / Continue) ── */
.stButton > button,
.stFormSubmitButton > button {{
    background: {ORANGE} !important;
    background-color: {ORANGE} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 2rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 3px 10px rgba(241,60,32,0.35) !important;
    transition: all 0.2s !important;
}}
.stButton > button p,
.stButton > button span,
.stButton > button div,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span,
.stFormSubmitButton > button div {{
    color: #ffffff !important;
}}
.stButton > button:hover,
.stFormSubmitButton > button:hover {{
    background: #d12d12 !important;
    background-color: #d12d12 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(241,60,32,0.45) !important;
}}
.stButton > button:disabled,
.stFormSubmitButton > button:disabled {{
    background: {LAVENDER} !important;
    background-color: {LAVENDER} !important;
    color: {TEXT_MUTED} !important;
    opacity: 0.8 !important;
    box-shadow: none !important;
}}

/* ── Download buttons ── */
.stDownloadButton > button,
.stDownloadButton > button p,
.stDownloadButton > button span {{
    background: {BLUE} !important;
    background-color: {BLUE} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 10px rgba(64,86,161,0.3) !important;
}}
.stDownloadButton > button:hover {{
    background: #2f4082 !important;
    background-color: #2f4082 !important;
}}

/* ── Text input ── */
.stTextInput > div > div > input {{
    background: {BG_CARD} !important;
    color: {TEXT_DARK} !important;
    border: 1.5px solid {LAVENDER} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 2px rgba(64,86,161,0.2) !important;
}}
.stTextInput label,
.stTextInput > label {{
    color: {TEXT_DARK} !important;
    font-weight: 600 !important;
}}

/* ── Code blocks (main area — cream on near-black for clear contrast) ── */
.main code,
.main pre,
.main .stCode,
.main .stCode pre,
.main [data-testid="stCodeBlock"],
.main [data-testid="stCodeBlock"] pre,
.main [data-testid="stCodeBlock"] code {{
    background: #1a1d2e !important;
    border: 1px solid {BLUE} !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 0.85rem !important;
}}
.main [data-testid="stCodeBlock"] code span,
.main pre code,
.main pre code span {{
    color: #ffffff !important;
    background: transparent !important;
}}

/* ── Sidebar inline code (high contrast on blue) ── */
[data-testid="stSidebar"] code {{
    background: rgba(255,255,255,0.18) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.15rem 0.5rem !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    background: {CREAM} !important;
    border: 1px solid {GOLD} !important;
    color: {TEXT_DARK} !important;
    border-radius: 8px !important;
}}
[data-testid="stAlert"] p {{
    color: #78350f !important;
}}

hr {{ border-color: {BORDER_SOFT} !important; }}
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
TIMER_SECS = 150

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
        logo_html = '<div style="font-size:2rem;font-weight:900;color:#ffffff;letter-spacing:-0.05em;">CGI</div>'
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
#  PDF — CERTIFICATE (Canvas-based, reliable)
# ─────────────────────────────────────────────
def generate_certificate(name, role, score, classification):
    buffer = BytesIO()
    PAGE_W, PAGE_H = 297*mm, 210*mm  # landscape A4

    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))

    # ── Background (cream) ──
    c.setFillColor(colors.HexColor(CREAM))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ── Outer thick gold border ──
    c.setStrokeColor(colors.HexColor(GOLD))
    c.setLineWidth(6)
    c.rect(8*mm, 8*mm, PAGE_W - 16*mm, PAGE_H - 16*mm, fill=0, stroke=1)

    # ── Inner thin blue accent ──
    c.setStrokeColor(colors.HexColor(BLUE))
    c.setLineWidth(0.8)
    c.rect(13*mm, 13*mm, PAGE_W - 26*mm, PAGE_H - 26*mm, fill=0, stroke=1)

    # ── Top corner accents ──
    c.setFillColor(colors.HexColor(ORANGE))
    c.rect(8*mm, PAGE_H - 14*mm, 60*mm, 6*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(BLUE))
    c.rect(PAGE_W - 68*mm, 8*mm, 60*mm, 6*mm, fill=1, stroke=0)

    cx = PAGE_W / 2
    y  = PAGE_H - 38*mm

    # ── Title ──
    c.setFillColor(colors.HexColor(ORANGE))
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(cx, y, "Certificate of Completion")
    y -= 12*mm

    # ── Subtitles ──
    c.setFillColor(colors.HexColor(BLUE))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(cx, y, "CGI Cybersecurity Tabletop Exercise")
    y -= 5*mm
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.setFont("Helvetica", 10)
    c.drawCentredString(cx, y, "Spearphishing Incident Response Simulation")
    y -= 14*mm

    # ── Awarded to ──
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(cx, y, "This certifies that")
    y -= 12*mm

    c.setFillColor(colors.HexColor(BLUE))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(cx, y, name)
    y -= 6*mm

    if role:
        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(cx, y, role)
        y -= 8*mm
    else:
        y -= 4*mm

    # ── Score statement ──
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.setFont("Helvetica", 11)
    c.drawCentredString(cx, y, "has successfully completed the exercise with a score of")
    y -= 12*mm

    c.setFillColor(colors.HexColor(ORANGE))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(cx, y, f"{score}/100")
    y -= 8*mm

    c.setFillColor(colors.HexColor(BLUE))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, y, classification)
    y -= 14*mm

    # ── Footer ──
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.setFont("Helvetica", 10)
    c.drawCentredString(cx, y, f"Completed: {datetime.now().strftime('%d %B %Y')}")
    y -= 5*mm
    c.drawCentredString(cx, y, "MITRE ATT&CK Framework — Spearphishing Kill Chain (T1566.001)")
    y -= 9*mm

    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, y, "Issued by CGI Cybersecurity Practice  |  Confidential — Training Use Only")
    y -= 4.5*mm
    c.drawCentredString(cx, y, "Developed by 5yber  |  Delivered in partnership with CGI Cybersecurity Practice")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────
#  PDF — REPORT (white pages, dark text)
# ─────────────────────────────────────────────
def generate_pdf(total, classification):
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               leftMargin=20*mm, rightMargin=20*mm,
                               topMargin=20*mm,  bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    blue   = colors.HexColor(BLUE)
    orange = colors.HexColor(ORANGE)
    gold   = colors.HexColor(GOLD)
    dark   = colors.HexColor(TEXT_DARK)
    mute   = colors.HexColor(TEXT_MUTED)

    title_style = ParagraphStyle("T", parent=styles["Title"],
                                  textColor=blue,   fontSize=22, spaceAfter=4)
    h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                  textColor=orange, fontSize=13, spaceBefore=14, spaceAfter=4)
    body_style  = ParagraphStyle("B", parent=styles["Normal"],
                                  textColor=dark,   fontSize=10, leading=15, spaceAfter=4)
    label_style = ParagraphStyle("L", parent=styles["Normal"],
                                  textColor=mute,   fontSize=9)

    story = []
    story.append(Paragraph("CGI Cybersecurity Tabletop Exercise", title_style))
    story.append(Paragraph("Spearphishing Incident Response Simulation — Confidential Report", label_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=orange, spaceAfter=12))

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
        ("TEXTCOLOR",     (0,0), (0,-1),  mute),
        ("TEXTCOLOR",     (1,0), (1,-1),  dark),
        ("FONTNAME",      (1,4), (1,5),   "Helvetica-Bold"),
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#fafaf6")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
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
        ("BACKGROUND",    (0,0), (-1,0),  blue),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,-1),(-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (-1,-1), dark),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [colors.white, colors.HexColor("#f7f5ec")]),
        ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor(CREAM)),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#d1d5db")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(ct)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Stage-by-Stage Analysis", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db"), spaceAfter=8))

    for key, label in zip(STAGE_KEYS, STAGES):
        answer             = st.session_state.answers.get(key, "No answer recorded")
        ans_idx            = st.session_state.answer_indices.get(key, 0)
        quality, analysis_text = QUESTIONS[key]["analysis"][ans_idx]
        score              = st.session_state.scores[key]
        tid, tname         = MITRE_TAGS[key]

        ql   = {"correct": "✓ Optimal", "partial": "~ Adequate", "poor": "✗ Insufficient"}[quality]
        qcol = {"correct": colors.HexColor("#059669"),
                "partial": colors.HexColor(GOLD),
                "poor":    colors.HexColor(ORANGE)}[quality]

        story.append(Paragraph(f"{label} Stage — {tid}: {tname}", h2_style))
        dt = Table([
            ["Decision Made",  answer],
            ["Assessment",     ql],
            ["Points Awarded", f"{score} / 20"],
        ], colWidths=[38*mm, 122*mm])
        dt.setStyle(TableStyle([
            ("FONTNAME",      (0,0), (0,-1),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("TEXTCOLOR",     (0,0), (0,-1),  mute),
            ("TEXTCOLOR",     (1,0), (1,0),   dark),
            ("TEXTCOLOR",     (1,1), (1,1),   qcol),
            ("TEXTCOLOR",     (1,2), (1,2),   dark),
            ("FONTNAME",      (1,1), (1,1),   "Helvetica-Bold"),
            ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#fafaf6")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        story.append(dt)
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Impact Analysis:</b> {analysis_text}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#e5e7eb"), spaceAfter=6))

    story.append(Paragraph("Recommendations", h2_style))
    recs = {
        "Incident Response Ready":          "Your decisions demonstrate strong IR maturity across the full spearphishing kill chain. Maintain quarterly tabletops and expand to APT and ransomware scenarios.",
        "Operationally Aware":              "You show solid awareness but have gaps in one or more stages. Review IR playbooks, especially around MITRE T1078 session containment and T1041 exfiltration response.",
        "Needs Procedural Reinforcement":   "Several decisions indicate procedural gaps. Prioritise formal IR training, implement SIEM runbooks aligned to the spearphishing kill chain, and establish clear escalation paths.",
        "High Organisational Risk Profile": "Immediate action required. Engage an MSSP or IR retainer, develop a documented IR plan covering the T1566.001 attack path, and conduct a full security posture review.",
    }
    story.append(Paragraph(recs[classification], body_style))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=orange, spaceAfter=6))
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
    if score >= 90: return ("Incident Response Ready",          "#059669")
    if score >= 70: return ("Operationally Aware",              "#059669")
    if score >= 50: return ("Needs Procedural Reinforcement",   GOLD)
    return                  ("High Organisational Risk Profile", ORANGE)

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

    # ── Elapsed time for the whole exercise ──
    elapsed_seconds = int((datetime.now() - st.session_state.start_time).total_seconds())
    e_m, e_s = divmod(elapsed_seconds, 60)
    if e_m >= 60:
        e_h, e_m = divmod(e_m, 60)
        elapsed_str = f"{e_h}h {e_m}m {e_s}s"
    else:
        elapsed_str = f"{e_m}m {e_s}s"

    st.markdown(f"""
    <div class="result-card">
        <div class="big-score">{total}<span style="font-size:1.5rem;color:{TEXT_MUTED}">/100</span></div>
        <div class="classification" style="color:{colour}">{classification}</div>
        <div class="sub">
            {st.session_state.name} &nbsp;|&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M UTC")}<br/>
            ⏱ Total time: <strong>{elapsed_str}</strong> &nbsp;|&nbsp; MITRE ATT&CK — Spearphishing Kill Chain (T1566.001)
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
            <span style="color:{TEXT_MUTED};font-size:0.8rem">&nbsp;{tid}</span>
            — {answer}</span>
            <span style="color:{ORANGE};font-weight:700">{score}/20</span>
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
