import streamlit as st
import streamlit.components.v1 as components

# -------------------------------
# Baserow Connection
# -------------------------------

from baserow.client import BaserowClient
import uuid
from datetime import datetime


# -------------------------------
# Baserow Connection
# -------------------------------

# Initialize the ONE AND ONLY client for your self-hosted Baserow
# This uses st.cache_resource to create the client once and reuse it.
@st.cache_resource
def get_baserow_client():
    return BaserowClient(
        url='http://baserow.goxmit.com/',  # Your self-hosted API URL
        token=st.secrets['BASEROW_TOKEN']     # Your Database Token
    )

# This variable will be used by ALL functions in your app
client = get_baserow_client()

# -------------------------------
# Page configuration
# -------------------------------

st.set_page_config(
    page_title="Inventory Health Quick Check",
    page_icon="📦",
    layout="centered"
)

# -------------------------------
# Question definitions (constants)
# -------------------------------
QUESTIONS = [
    {
        "question": "What percentage of your inventory has not sold in the last 6 months?",
        "options": [
            "< 10%",
            "10–25%",
            "25–50%",
            "> 50%"
        ],
        "scores": [20, 15, 8, 0]
    },
    {
        "question": "How often do you experience stockouts of top-selling items?",
        "options": [
            "Rarely",
            "Monthly",
            "Weekly",
            "Constantly"
        ],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "How would you describe your warehouse inventory today?",
        "options": [
            "Well balanced and organized",
            "Full but manageable",
            "Full of slow-moving items",
            "Chaotic and hard to track"
        ],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "How many hours per week does your team spend fixing inventory issues?",
        "options": [
            "< 5 hours",
            "5–15 hours",
            "15–30 hours",
            "> 30 hours"
        ],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "What is your approximate annual inventory turnover?",
        "options": [
            "> 12x",
            "8–12x",
            "4–8x",
            "< 4x"
        ],
        "scores": [20, 15, 8, 0]
    }
]

# -------------------------------
# Question's Progress Colors
# -------------------------------

PROGRESS_COLORS = [
    "#ef4444",  # Q1 - red
    "#f97316",  # Q2 - orange
    "#facc15",  # Q3 - yellow
    "#16a34a",  # Q4 - green
    "#800080",  # Q5 - purple
]
# COMPLETED_COLOR = "#93c5fd"   # muted blue
UPCOMING_COLOR = "#e5e7eb"    # light gray

# -------------------------------
# Session state initialization (GLOBAL)
# -------------------------------

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

# -------------------------------
# Progress Colors Function
# -------------------------------
def colored_progress_bar(progress, color):
    st.markdown(
        f"""
        <div style="background-color: #e5e7eb; border-radius: 8px; height: 12px;">
            <div style="
                width: {int(progress * 100)}%;
                background-color: {color};
                height: 12px;
                border-radius: 8px;
                transition: width 0.3s ease;">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Segmented Progress Bar Function
# -------------------------------
def segmented_progress_bar(current_index, total):
    segments_html = ""

    for i in range(total):
        if i <= current_index:
            color = PROGRESS_COLORS[i] 
        else:
            color = UPCOMING_COLOR

        segments_html += f"""
        <div style="
            flex: 1;
            background-color: {color};
            height: 12px;
            border-radius: 6px;
            margin-right: 6px;
        "></div>
        """

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
        ">
            {segments_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Custom CSS
# -------------------------------

def semicircle_score(score, color):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <div style="
                width: 220px;
                height: 110px;
                background: {color};
                border-radius: 220px 220px 0 0;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    bottom: 10px;
                    width: 100%;
                    text-align: center;
                    color: white;
                    font-size: 2rem;
                    font-weight: 700;
                ">
                    {score} / 100
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown(
    """
    <style>
    div[data-testid="stButton"] > button {
        background-color: #1f4fd8;
        color: white;
        border-radius: 6px;
        height: 3em;
        font-size: 1rem;
        font-weight: 600;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #163bb3;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# -------------------------------
# Session state initialization
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ---------- Landing Page ----------
def landing_page():
    col1, col2 = st.columns([1, 8])

    with col1:
        st.image("assets/logo.svg", width=50)

    with col2:
        st.markdown("### Inventory Health **Quick Check**")

    st.markdown("---")

    # Centered headline + subheading
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>Is Your Inventory Costing You Money?</h2>
            <p style="font-size: 1.05rem;">
                Answer <strong>5 quick questions</strong> and get an 
                <strong>Inventory Health Score</strong><br>
                -plus <strong>clear, practical next steps</strong>.
            </p>
            <p style="color: #6b7280; font-size: 0.95rem;">
                • No email required &nbsp;&nbsp;•&nbsp;&nbsp; Takes under 3 minutes &nbsp;&nbsp;•&nbsp;&nbsp; Diagnostic only
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Centered CTA button
    col1, col2, col3 = st.columns([1, 2, 1])


    with col2:
        if st.button("▶ Start the Quick Check", use_container_width=True):

            # Create session only if it doesn't already exist
            if "session_id" not in st.session_state:
                create_assessment_session()

            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.page = "quiz"
            st.rerun()

# -------------------------------
# Create Session
# -------------------------------


def create_assessment_session():
    session_token = str(uuid.uuid4())

    row = client.create_database_table_row(
        st.secrets["SESSIONS_TABLE_ID"],
        {
            "session_token": session_token,
            "created": datetime.utcnow().isoformat(),
        }
    )

    st.session_state.session_id = row["id"]
    st.session_state.session_token = session_token


# -------------------------------
# Start the quiz
# -------------------------------

def quiz_page():
    q_index = st.session_state.current_question
    total_questions = len(QUESTIONS)
    question_data = QUESTIONS[q_index]

    # Progress

    
#    progress = (q_index + 1) / total_questions
 #   color = PROGRESS_COLORS[q_index]

    st.markdown(f"**Question {q_index + 1} of {total_questions}**")
    #st.progress(progress)
    #colored_progress_bar(progress, color)
    segmented_progress_bar(q_index, total_questions)

    st.markdown("<br>", unsafe_allow_html=True)

    # Question text
    st.markdown(f"### {question_data['question']}")

    # Pre-select previous answer if it exists
    previous_answer = st.session_state.answers.get(q_index, None)

    answer = st.radio(
        "",
        question_data["options"],
        index=question_data["options"].index(previous_answer)
        if previous_answer else 0,
        key=f"question_{q_index}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    # Back button (only from Question 2 onward)
    with col1:
        if q_index > 0:
            if st.button("‹ Back"):
                st.session_state.current_question -= 1
                st.rerun()

    # Next / Finish button
    with col3:
        if st.button("Next ›" if q_index < total_questions - 1 else "Finish"):
            st.session_state.answers[q_index] = answer

            if q_index < total_questions - 1:
                st.session_state.current_question += 1
            else:
                st.session_state.page = "results"

            st.rerun()

# -------------------------------
# Result calculation: Scoring logic function
# -------------------------------
def calculate_score():
    total_score = 0
    max_score = 0

    for i, q in enumerate(QUESTIONS):
        selected_answer = st.session_state.answers.get(i)
        if selected_answer:
            answer_index = q["options"].index(selected_answer)
            total_score += q["scores"][answer_index]
        max_score += max(q["scores"])

    percentage = int((total_score / max_score) * 100)
    return total_score, max_score, percentage

# -------------------------------
# Result calculation: Score classification function
# -------------------------------
def score_band(percentage):
    if percentage >= 75:
        return {
            "label": "Healthy",
            "color": "#16a34a",
            "headline": "Your Inventory Is in Good Shape",
            "message": "You have solid control over your inventory, with only minor optimization opportunities."
        }
    elif percentage >= 45:
        return {
            "label": "At Risk",
            "color": "#f97316",
            "headline": "Your Inventory Is Leaking Money",
            "message": "You’re carrying avoidable costs and inefficiencies that will compound if left unchecked."
        }
    else:
        return {
            "label": "Critical",
            "color": "#ef4444",
            "headline": "Your Inventory Is Actively Hurting Cash Flow",
            "message": "Excess stock, stockouts, and manual fixes are draining time and working capital."
        }
    
# -------------------------------
# Contact lookup or creation
# -------------------------------

def get_or_create_contact(email):
    st.write("🔍 Looking up contact:", email)

    contacts_page = client.list_database_table_rows(
        table_id=st.secrets["CONTACTS_TABLE_ID"],
        size=100
    )

    for row in contacts_page.results:
        st.write("Found existing contact row:", row)
        if row.get("email") == email:
            st.write("✅ Existing contact matched")
            return row["id"]

    st.write("➕ No existing contact found. Creating new one.")

    created = client.create_database_table_row(
        table_id=st.secrets["CONTACTS_TABLE_ID"],
        record={
            "Email": email,
            "role": "prospect",
            "created": datetime.utcnow().isoformat()
        }
    )

    st.write("🆕 Created contact:", created)

    return created["id"]


# -------------------------------
# Result calculation: Results page layout
# -------------------------------
def results_page():
    total_score, max_score, percentage = calculate_score()
    band = score_band(percentage)

    # -------------------------------
    # Header
    # -------------------------------
    st.markdown("### Inventory Health Results")
    st.markdown("---")

    # -------------------------------
    # Score Display (SEMICIRCLE)
    # -------------------------------
    semicircle_score(percentage, band["color"])

    st.markdown(
        f"""
        <div style="text-align:center; margin-top:8px;">
            <p style="font-size:1.2rem; font-weight:600;">
                Inventory Health Score
            </p>
            <span style="
                display:inline-block;
                padding:6px 14px;
                border-radius:999px;
                background-color:{band['color']};
                color:white;
                font-size:0.85rem;
                font-weight:600;
            ">
                {band['label']}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # Interpretation
    # -------------------------------
    st.markdown(
        f"""
        <div style="text-align:center;">
            <h3>{band['headline']}</h3>
            <p style="font-size:1.05rem; color:#374151;">
                {band['message']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    ########################################################################


    # -------------------------------
    # Report + Booking CTAs (2 Columns)
    # -------------------------------
    st.markdown(
        """
        <style>
        .orange-btn button {
            background-color: #f97316;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            width: 100%;
            height: 3em;
        }
        .orange-btn button:hover {
            background-color: #ea580c;
            color: white;
        }

        .green-btn button {
            background-color: #16a34a;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            width: 100%;
            height: 3em;
        }
        .green-btn button:hover {
            background-color: #15803d;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns(2)

    # -------------------------------
    # LEFT: PDF Report Email Capture
    # -------------------------------
    with col_left:
        st.markdown("#### Get Your PDF Report")
        st.markdown(
            "Want a **detailed, stakeholder-ready summary** of your results?\n\n"
            "**Enter your email** and we’ll send you the full report."
        )

        if "email_submitted" not in st.session_state:
            st.session_state.email_submitted = False

        if not st.session_state.email_submitted:
            with st.form("pdf_email_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@company.com",
                    label_visibility="collapsed"
                )

                st.markdown('<div class="orange-btn">', unsafe_allow_html=True)
                submit_pdf = st.form_submit_button("Download PDF Report")
                st.markdown('</div>', unsafe_allow_html=True)

                if submit_pdf:
                    if not email or "@" not in email:
                        st.error("Please enter a valid email address.")
                    else:                        
                        contact_id = get_or_create_contact(email)

                        save_result_to_baserow(
                            contact_id=contact_id,
                            percentage=percentage,
                            max_score=max_score,
                            health_level=band["label"]
                        )


                        st.session_state.email_submitted = True
                        st.success("✅ Your report is being prepared and will arrive shortly.")
        else:
            st.info("📩 Your report request has already been submitted.")

    # -------------------------------
    # RIGHT: Booking CTA
    # -------------------------------
    with col_right:
        st.markdown("#### Need SKU-Level Clarity?")
        st.markdown(
            """
            **Book a 30-Minute Inventory Health Alignment Call**

            • Discuss your results  
            • Review your real inventory data  
            • Identify hidden opportunities
            """
        )

        st.markdown('<div class="green-btn">', unsafe_allow_html=True)
        book_call = st.button("Book a Call →")
        st.markdown('</div>', unsafe_allow_html=True)

        if book_call:
            st.session_state.page = "booking"  # or redirect to external link
            st.rerun()


    ########################################################################

    # -------------------------------
    # Navigation Actions
    # -------------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("↺ Retake Assessment"):
            st.session_state.page = "landing"
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.email_submitted = False
            st.rerun()

    with col2:
        st.button("View Improvement Plan →", disabled=True)

# -------------------------------
# Save assessment result
# -------------------------------
def save_result_to_baserow(contact_id, percentage, max_score, health_level):
    client.create_database_table_row(
        st.secrets["RESULTS_TABLE_ID"],
        {
            "session": [st.session_state.session_id],
            "contact": [contact_id],
            "overall_score": percentage,
            "max_score_possible": max_score,
            "assessment_version": "v1",
            "health_level": health_level,
            "report_status": "requested",
            "created": datetime.utcnow().isoformat(),
        }
    )

# -------------------------------
# Page Routing: Session state definitions
# -------------------------------

#elif st.session_state.page == "results":
#    results_page()

if st.session_state.page == "landing":
    landing_page()

elif st.session_state.page == "quiz":
    quiz_page()

elif st.session_state.page == "results":
    results_page()
