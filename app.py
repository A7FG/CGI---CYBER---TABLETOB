import streamlit as st
import random
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Cyber Tabletop Exercise", layout="wide")

# -------------------- HEADER --------------------
st.markdown("""
<style>
.center-box {max-width: 800px; margin: auto;}
.block-container {padding-top: 2rem;}
</style>
<div style="text-align:center; border-bottom:1px solid #ddd; margin-bottom:25px;">
<h2>CGI Cybersecurity Table-Top Exercise</h2>
<p>Incident Response & Decision-Making Simulation</p>
</div>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "stage" not in st.session_state:
    st.session_state.stage = -1
    st.session_state.name = ""
    st.session_state.start_time = datetime.now()
    st.session_state.scores = dict.fromkeys(
        ["detection","response","containment","communication","recovery"], 0
    )
    st.session_state.answers = {}

def advance():
    st.session_state.stage += 1
    st.rerun()

# -------------------- SIDEBAR --------------------
def render_sidebar():
    if st.session_state.stage == -1:
        return

    st.sidebar.title("Exercise Progress")
    st.sidebar.metric("Current Score", f"{sum(st.session_state.scores.values())}/100")

    labels = ["Detection","Response","Containment","Communication","Recovery"]
    for i, lbl in enumerate(labels):
        if st.session_state.stage > i:
            st.sidebar.markdown(f"✅ {lbl}")
        elif st.session_state.stage == i:
            st.sidebar.markdown(f"🟡 {lbl} (Current)")
        else:
            st.sidebar.markdown(f"⬜ {lbl}")

# -------------------- ANALYSIS ENGINE --------------------
def analyse_stage(stage, answer):
    analysis = {
        "detection": {
            "Ignore": "Ignoring phishing indicators increases attacker dwell time and enables credential compromise.",
            "Escalate to IT": "Correct escalation reduces attacker dwell time before lateral movement.",
            "Inspect headers and link": "Strong technical validation that prevents credential harvesting."
        },
        "response": {
            "Ignore": "Active attacker sessions remain operational without intervention.",
            "Password reset": "Useful but incomplete if attacker session token remains valid.",
            "Investigate session": "Proper scoping step before decisive action.",
            "Disable account": "Immediate containment of compromised credentials."
        },
        "containment": {
            "Wait": "Allows malware execution and internal propagation.",
            "Notify IT": "Administrative step that does not stop spread.",
            "Check logs": "Improves visibility but not containment.",
            "Isolate machine": "Correct containment action preventing lateral movement."
        },
        "communication": {
            "Monitor": "Passive stance during exfiltration increases damage.",
            "Forensics": "Important but secondary to stopping data loss.",
            "Block traffic": "Correct immediate action to protect data."
        },
        "recovery": {
            "Delay": "Business disruption without improving security.",
            "Notify execs": "Governance step but incomplete alone.",
            "Legal/compliance": "Ensures regulatory and reputational protection.",
            "Inform customers": "Premature before internal alignment."
        }
    }
    return analysis[stage].get(answer, "No analysis available.")

# -------------------- PDF --------------------
def generate_pdf(total, classification):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Cybersecurity Tabletop Exercise Report", styles['Title']))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Participant: {st.session_state.name}", styles['Normal']))
    story.append(Paragraph(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Score: {total}/100", styles['Heading2']))
    story.append(Paragraph(f"Classification: {classification}", styles['Heading3']))
    story.append(Spacer(1,24))

    for stage in ["detection","response","containment","communication","recovery"]:
        answer = st.session_state.answers.get(stage, "No answer")
        analysis = analyse_stage(stage, answer)

        story.append(Paragraph(f"<b>{stage.capitalize()} Stage</b>", styles['Heading2']))
        story.append(Paragraph(f"<b>Your decision:</b> {answer}", styles['Normal']))
        story.append(Paragraph(f"<b>Impact analysis:</b> {analysis}", styles['Normal']))
        story.append(Spacer(1,18))

    doc.build(story)
    buffer.seek(0)
    return buffer

def classify(score):
    if score >= 90: return "Incident Response Ready"
    if score >= 70: return "Operationally Aware"
    if score >= 50: return "Needs Procedural Reinforcement"
    return "High Organisational Risk Profile"

# -------------------- START --------------------
if st.session_state.stage == -1:
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.session_state.name = st.text_input("Enter your name to begin:")
    if st.button("Start Exercise") and st.session_state.name:
        advance()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- DETECTION --------------------
elif st.session_state.stage == 0:
    render_sidebar()
    st.markdown("**08:42 — Detection Stage**")

    emails = [
"""From: it-support@companny-secure.com
Subject: Urgent Credential Verification
Link: http://secure-company-login.co""",
"""From: helpdesk@company-it.net
Subject: Security Alert
Link: http://verify-now-company.net"""
    ]
    st.code(random.choice(emails), language="text")

    with st.form("detection"):
        choice = st.radio("Your decision:",
            ["Ignore", "Escalate to IT", "Inspect headers and link"], index=None)
        if st.form_submit_button("Submit") and choice:
            st.session_state.scores["detection"] = [4,12,20][
                ["Ignore","Escalate to IT","Inspect headers and link"].index(choice)]
            st.session_state.answers["detection"] = choice
            advance()

# -------------------- RESPONSE --------------------
elif st.session_state.stage == 1:
    render_sidebar()
    st.markdown("**08:55 — Response Stage**")

    st.code("""SIEM LOG:
User: hr.jane
IP: 185.234.219.12 (RU)
Status: Successful Login""")

    with st.form("response"):
        choice = st.radio("Action:",
            ["Ignore", "Password reset", "Investigate session", "Disable account"], index=None)
        if st.form_submit_button("Submit") and choice:
            st.session_state.scores["response"] = [3,10,15,20][
                ["Ignore","Password reset","Investigate session","Disable account"].index(choice)]
            st.session_state.answers["response"] = choice
            advance()

# -------------------- CONTAINMENT --------------------
elif st.session_state.stage == 2:
    render_sidebar()
    st.markdown("**09:10 — Containment Stage**")

    st.code("""Email Header Extract:
Received: unknown-mail.ru
Attachment: payroll_update.xlsm""")

    with st.form("containment"):
        choice = st.radio("Containment approach:",
            ["Wait", "Notify IT", "Check logs", "Isolate machine"], index=None)
        if st.form_submit_button("Submit") and choice:
            st.session_state.scores["containment"] = [4,10,14,20][
                ["Wait","Notify IT","Check logs","Isolate machine"].index(choice)]
            st.session_state.answers["containment"] = choice
            advance()

# -------------------- COMMUNICATION --------------------
elif st.session_state.stage == 3:
    render_sidebar()
    st.markdown("**09:25 — Communication Stage**")

    st.code("""Network Alert:
Outbound transfer 4.2GB → unknown external host""")

    with st.form("communication"):
        choice = st.radio("Priority:",
            ["Monitor", "Forensics", "Block traffic"], index=None)
        if st.form_submit_button("Submit") and choice:
            st.session_state.scores["communication"] = [6,14,20][
                ["Monitor","Forensics","Block traffic"].index(choice)]
            st.session_state.answers["communication"] = choice
            advance()

# -------------------- RECOVERY --------------------
elif st.session_state.stage == 4:
    render_sidebar()
    st.markdown("**10:00 — Recovery Stage**")

    st.code("""Post-Incident Brief:
Systems cleaned. Backups verified.
Pressure from management to resume operations immediately.""")

    with st.form("recovery"):
        choice = st.radio(
            "What is the FIRST governance priority before restoring services?",
            ["Delay", "Notify execs", "Legal/compliance", "Inform customers"],
            index=None
        )
        if st.form_submit_button("Submit") and choice:
            st.session_state.scores["recovery"] = [5,14,20,10][
                ["Delay","Notify execs","Legal/compliance","Inform customers"].index(choice)]
            st.session_state.answers["recovery"] = choice
            advance()

# -------------------- REPORT --------------------
elif st.session_state.stage == 5:
    total = sum(st.session_state.scores.values())
    classification = classify(total)

    st.title("Exercise Complete")
    st.success("Your decisions reflect your incident response maturity.")
    st.info("For detailed forensic feedback on each decision, download the PDF report below.")

    pdf = generate_pdf(total, classification)
    st.download_button("Download PDF Report", pdf, "tabletop_report.pdf")

    if st.button("Run Another Scenario"):
        # reset state cleanly
        st.session_state.stage = 0
        for k in st.session_state.scores:
            st.session_state.scores[k] = 0
        st.session_state.answers = {}
        st.rerun()

