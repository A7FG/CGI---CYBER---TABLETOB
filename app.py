import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Cyber Tabletop Exercise", layout="wide")

# -------------------- STYLING --------------------
st.markdown("""
<style>
.app-header {
    width: 100%;
    padding: 18px 0 8px 0;
    margin-bottom: 30px;
    border-bottom: 1px solid #e6e6e6;
    text-align: center;
}
.app-header h1 {
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 1px;
    margin: 0;
}
.app-sub {
    font-size: 13px;
    color: #666;
    margin-top: 4px;
}
.block-container {padding-top: 3rem;}
.center-box {
    max-width: 700px;
    margin: auto;
    text-align: center;
}
</style>

<div class="app-header">
    <h1>CGI Cybersecurity Table-Top Exercise</h1>
    <div class="app-sub">Incident Response & Decision-Making Simulation</div>
</div>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "stage" not in st.session_state:
    st.session_state.stage = -1
    st.session_state.scores = {
        "phishing": 0,
        "response": 0,
        "containment": 0,
        "communication": 0,
        "recovery": 0
    }

def next_stage():
    st.session_state.stage += 1

# -------------------- SIDEBAR --------------------
def render_sidebar():
    if st.session_state.stage == -1:
        return

    stages = [
        ("Detection", "phishing"),
        ("Response", "response"),
        ("Containment", "containment"),
        ("Communication", "communication"),
        ("Recovery", "recovery"),
    ]

    st.sidebar.title("Exercise Progress")
    total_score = sum(st.session_state.scores.values())
    st.sidebar.metric("Current Score", f"{total_score}/100")

    for i, (label, key) in enumerate(stages):
        if st.session_state.stage > i:
            st.sidebar.markdown(f"✅ **{label}**")
        elif st.session_state.stage == i:
            st.sidebar.markdown(f"🟡 **{label} (Current)**")
        else:
            st.sidebar.markdown(f"⬜ {label}")

# -------------------- PDF --------------------
def generate_pdf(total, feedback):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Cybersecurity Tabletop Exercise Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Overall Cyber Awareness Score: {total}/100", styles['Heading2']))
    story.append(Spacer(1, 12))

    for section, text in feedback.items():
        story.append(Paragraph(section, styles['Heading3']))
        story.append(Paragraph(text, styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

def section_feedback(score, good, mid, poor):
    if score >= 18:
        return good
    elif score >= 10:
        return mid
    else:
        return poor

# -------------------- START PAGE --------------------
if st.session_state.stage == -1:
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.write("""
You are participating in a simulated cyber incident affecting your organisation.

Across five stages, you will be required to make decisions that influence
how the incident unfolds. Your choices will be evaluated for awareness,
prioritisation, and adherence to cybersecurity best practices.
""")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Exercise"):
            st.session_state.stage = 0
    with col2:
        if st.button("Exit"):
            st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- DETECTION --------------------
elif st.session_state.stage == 0:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.header("Detection Stage")

    st.write("""
08:42 — An employee from HR forwards you an email asking if it is legitimate.
The email claims to be from IT support requesting urgent credential verification
due to suspicious activity. The link in the email redirects to an unfamiliar domain.
""")

    choice = st.radio(
        "Your decision:",
        [
            "Ignore the report",
            "Escalate the email to IT security",
            "Examine the email headers and inspect the link destination"
        ]
    )

    if st.button("Submit"):
        st.session_state.scores["phishing"] = [4, 12, 20][
            ["Ignore the report",
             "Escalate the email to IT security",
             "Examine the email headers and inspect the link destination"].index(choice)
        ]
        next_stage()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- RESPONSE --------------------
elif st.session_state.stage == 1:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.header("Response Stage")

    st.write("""
08:55 — A SIEM alert indicates a successful login to the HR employee’s account
from an IP address located overseas. This location does not match the user’s profile.
""")

    choice = st.radio(
        "What action do you take?",
        [
            "Ignore the alert as a false positive",
            "Force a password reset",
            "Investigate the login session activity",
            "Disable the account immediately"
        ]
    )

    scores = [3, 10, 15, 20]

    if st.button("Submit"):
        st.session_state.scores["response"] = scores[
            ["Ignore the alert as a false positive",
             "Force a password reset",
             "Investigate the login session activity",
             "Disable the account immediately"].index(choice)
        ]
        next_stage()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- CONTAINMENT --------------------
elif st.session_state.stage == 2:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.header("Containment Stage")

    st.write("""
09:10 — Multiple employees report receiving unusual internal emails from the HR user.
The messages contain strange attachments and links.
""")

    choice = st.radio(
        "Your containment approach:",
        [
            "Wait for additional evidence",
            "Notify IT teams",
            "Inspect email server logs",
            "Isolate the HR employee’s machine from the network"
        ]
    )

    scores = [4, 10, 14, 20]

    if st.button("Submit"):
        st.session_state.scores["containment"] = scores[
            ["Wait for additional evidence",
             "Notify IT teams",
             "Inspect email server logs",
             "Isolate the HR employee’s machine from the network"].index(choice)
        ]
        next_stage()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- COMMUNICATION --------------------
elif st.session_state.stage == 3:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.header("Communication Stage")

    st.write("""
09:25 — Network monitoring detects unusually large outbound file transfers
from internal servers to an unknown external destination.
""")

    choice = st.radio(
        "What do you prioritise?",
        [
            "Continue monitoring the activity",
            "Launch forensic investigation",
            "Block the outbound traffic immediately"
        ]
    )

    scores = [6, 14, 20]

    if st.button("Submit"):
        st.session_state.scores["communication"] = scores[
            ["Continue monitoring the activity",
             "Launch forensic investigation",
             "Block the outbound traffic immediately"].index(choice)
        ]
        next_stage()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- RECOVERY --------------------
elif st.session_state.stage == 4:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.header("Recovery Stage")

    st.write("""
10:00 — It is now evident the organisation has experienced a breach.
Decisions must be made regarding governance and disclosure.
""")

    choice = st.radio(
        "Your governance decision:",
        [
            "Delay communication until more facts are known",
            "Notify executives",
            "Contact legal and compliance teams",
            "Inform customers immediately"
        ]
    )

    scores = [5, 14, 20, 10]

    if st.button("Submit"):
        st.session_state.scores["recovery"] = scores[
            ["Delay communication until more facts are known",
             "Notify executives",
             "Contact legal and compliance teams",
             "Inform customers immediately"].index(choice)
        ]
        next_stage()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- REPORT --------------------
elif st.session_state.stage == 5:
    render_sidebar()
    st.markdown('<div class="center-box">', unsafe_allow_html=True)

    st.title("Exercise Report")

    total = sum(st.session_state.scores.values())
    st.write(f"Overall Cyber Awareness Score: {total}/100")

    feedback = {
        "Phishing Recognition":
        section_feedback(st.session_state.scores["phishing"],
        "Excellent phishing recognition and proactive verification behaviour.",
        "Reasonable action but relied on escalation rather than validation.",
        "Phishing indicators were underestimated."),

        "Incident Response":
        section_feedback(st.session_state.scores["response"],
        "You decisively removed attacker persistence.",
        "Response was adequate but not immediate.",
        "Delayed response allowed attacker activity."),

        "Containment Strategy":
        section_feedback(st.session_state.scores["containment"],
        "Correct containment prevented further spread.",
        "Investigation was prioritised over isolation.",
        "Delayed containment increased internal risk."),

        "Communication Handling":
        section_feedback(st.session_state.scores["communication"],
        "You prioritised data protection effectively.",
        "Investigation occurred without immediate protection.",
        "Monitoring exposed data to risk."),

        "Recovery & Governance":
        section_feedback(st.session_state.scores["recovery"],
        "Proper governance procedures followed.",
        "Partial governance action taken.",
        "Delayed governance response increased risk.")
    }

    for k, v in feedback.items():
        st.subheader(k)
        st.write(v)

    pdf = generate_pdf(total, feedback)
    st.download_button("Download PDF Report", pdf, "tabletop_report.pdf")

    if st.button("Restart"):
        st.session_state.stage = -1
        st.session_state.scores = {k: 0 for k in st.session_state.scores}

    st.markdown('</div>', unsafe_allow_html=True)
