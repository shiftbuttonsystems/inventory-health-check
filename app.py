import streamlit as st
import streamlit.components.v1 as components
import uuid
from datetime import datetime
import requests

# -------------------------------
# Baserow Configuration
# -------------------------------
BASEROW_BASE_URL = st.secrets.get('BASEROW_BASE_URL', 'https://baserowapp.goxmit.com/api')
BASEROW_TOKEN = st.secrets['BASEROW_TOKEN']

def baserow_api_request(method, endpoint, data=None, params=None):
    """Universal function to call Baserow API"""
    url = f"{BASEROW_BASE_URL}/{endpoint}"
    
    headers = {
        "Authorization": f"Token {BASEROW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    query_params = {"user_field_names": "true"}
    if params:
        query_params.update(params)
    
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=query_params,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Silent error for user, log for debugging
        print(f"Baserow API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="Inventory Health Quick Check",
    page_icon="📦",
    layout="centered"
)


st.markdown(
    """
    <style>
    div[data-testid="stForm"] button {
        background-color: #f97316;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        height: 3em;
        width: 100%;
    }

    div[data-testid="stForm"] button:hover {
        background-color: #ea580c;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------
# Question definitions (constants)
# -------------------------------
QUESTIONS = [
    {
        "question": "Approximately what percentage of your inventory has not sold or been consumed in the past 6 months?",
        "options": ["Less than 10%", "10–25%", "25–50%", "More than 50%"],
        "scores": [20, 15, 8, 0]
    },
    {
        "question": "How often do you experience stockouts or shortages of your highest-demand SKUs or materials?",
        "options": ["Rarely (once or twice per year)", "Occasionally (every few months)", "Frequently (monthly)", "Very frequently (weekly or ongoing)"],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "Which best describes your current inventory position relative to demand?",
        "options": [
            "Inventory levels closely match demand patterns",
            "Generally balanced, with some overstock",
            "Noticeable overstock in slow-moving or seasonal items",
            "Significant mismatch between inventory and actual demand"
        ],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "Approximately how much time does your team spend each week addressing inventory-related issues (manual checks, expediting, exceptions, rework)?",
        "options": ["Less than 5 hours", "5–15 hours", "15–30 hours", "More than 30 hours"],
        "scores": [20, 14, 7, 0]
    },
    {
        "question": "How frequently does your inventory turn over, on average?  (If unsure, choose the closest estimate.) ",
        "options": ["Monthly or faster", "Every 2–3 months", "Every 4–6 months", "Less than twice per year"],
        "scores": [20, 15, 8, 0]
    }
]

HEALTH_MAP = {
    "Healthy": "Healthy",
    "At Risk": "At Risk",
    "Critical": "Critical"
}

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
UPCOMING_COLOR = "#e5e7eb"

# -------------------------------
# Session state initialization
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "session_finalized" not in st.session_state:
    st.session_state.session_finalized = False

# Add this with your other session state initializations:
if "session_token" not in st.session_state:
    st.session_state.session_token = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# -------------------------------
# Segmented Progress Bar Function
# -------------------------------
def segmented_progress_bar(current_index, total):
    segments_html = ""
    for i in range(total):
        color = PROGRESS_COLORS[i] if i <= current_index else UPCOMING_COLOR
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
        <div style="display: flex; align-items: center;">
            {segments_html}
        </div>
        """,
        unsafe_allow_html=True
    )

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

# ---------- Landing Page ----------
def landing_page():
    col1, col2 = st.columns([1, 8])

    with col1:
        st.image("assets/logo.svg", width=50)

    with col2:
        st.markdown("### Inventory Health **Quick Check**")

    st.markdown("---")

    # Headline & intro
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>Is Your Inventory Costing You Money?</h2>
            <p style="font-size: 1.05rem;">
                Answer <strong>5 quick questions</strong> and get an 
                <strong>Inventory Health Score</strong><br>
                plus <strong>clear, practical next steps</strong>.
            </p>
            <p style="color: #6b7280; font-size: 0.95rem;">
                • No email required &nbsp;&nbsp;•&nbsp;&nbsp; Takes under 3 minutes &nbsp;&nbsp;•&nbsp;&nbsp; Diagnostic only
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- SCORE INTERPRETATION (ADD HERE) ----------
    st.markdown("---")

    st.markdown(
        """
        <div style="text-align: center;">
            <h3>How Your Inventory Health Is Scored</h3>
            <p style="color:#6b7280; font-size:0.95rem;">
                Your answers are converted into a simple health score so you know exactly where you stand.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center;">
                <h4>🟢 Healthy</h4>
                <p><strong>70 – 100</strong></p>
                <p style="font-size:0.9rem; color:#374151;">
                    Inventory is generally supporting operations and cash flow.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style="border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center;">
                <h4>🟡 Needs Attention</h4>
                <p><strong>40 – 69</strong></p>
                <p style="font-size:0.9rem; color:#374151;">
                    Noticeable inefficiencies and risk exposure.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div style="border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center;">
                <h4>🔴 High Risk</h4>
                <p><strong>Below 40</strong></p>
                <p style="font-size:0.9rem; color:#374151;">
                    Inventory likely constraining cash, service, or operations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- CTA ----------
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶ Start the Quick Check", use_container_width=True):
            #if "session_id" not in st.session_state:                
            create_assessment_session()

            # Reset quiz state
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.session_finalized = False
            st.session_state.email_submitted = False

            # Navigate to quiz
            st.session_state.page = "quiz"
            st.rerun()


# -------------------------------
# Create Session
# -------------------------------
def create_assessment_session():
    session_token = str(uuid.uuid4())
    
    session_data = {
        "session_token": session_token,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    result = baserow_api_request(
        "POST",
        f"database/rows/table/{st.secrets['SESSIONS_TABLE_ID']}/",
        data=session_data
    )
    
    if result:
        st.session_state.session_id = result["id"]
        st.session_state.session_token = session_token


def reset_session():
    """Simple session reset for restart buttons"""
    # Clear critical session state
    for key in ['session_id', 'session_token', 'session_finalized', 
                'answers', 'current_question', 'email_submitted']:
        if key in st.session_state:
            del st.session_state[key]

# -------------------------------
# Quiz Page
# -------------------------------
def quiz_page():
    q_index = st.session_state.current_question
    total_questions = len(QUESTIONS)
    question_data = QUESTIONS[q_index]

    st.markdown(f"**Question {q_index + 1} of {total_questions}**")
    segmented_progress_bar(q_index, total_questions)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"### {question_data['question']}")

    previous_answer = st.session_state.answers.get(q_index, None)
    default_index = question_data["options"].index(previous_answer) if previous_answer else 0

    answer = st.radio(
        "",
        question_data["options"],
        index=default_index,
        key=f"question_{q_index}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if q_index > 0:
            if st.button("‹ Back"):
                st.session_state.current_question -= 1
                st.rerun()

    with col3:
        button_text = "Next ›" if q_index < total_questions - 1 else "Finish"
        if st.button(button_text):
            st.session_state.answers[q_index] = answer

            if q_index < total_questions - 1:
                st.session_state.current_question += 1
            else:                
                st.session_state.page = "results"

            st.rerun()

# -------------------------------
# Update Session Details
# -------------------------------
def finalize_assessment_session(score, health_label):
    if "session_id" not in st.session_state:
        return
    if st.session_state.get("session_finalized"):
        return

    payload = {
        "completed": True,
        "final_score": score,
        "health_band": health_label,
        "completed_at": datetime.now().strftime("%Y-%m-%d")
    }

    baserow_api_request(
        "PATCH",
        f"database/rows/table/{st.secrets['SESSIONS_TABLE_ID']}/{st.session_state.session_id}/",
        data=payload
    )

    st.session_state.session_finalized = True



# -------------------------------
# Result calculation
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

def score_band(percentage):
    if percentage >= 70:
        return {
            "label": "Healthy",
            "color": "#16a34a",
            "headline": "Your Inventory Is in Good Shape",
            "message": "You have solid control over your inventory, with only minor optimization opportunities."
        }
    elif percentage >= 40:
        return {
            "label": "At Risk",
            "color": "#f97316",
            "headline": "Your Inventory Is Leaking Money",
            "message": "You're carrying avoidable costs and inefficiencies that will compound if left unchecked."
        }
    else:
        return {
            "label": "Critical",
            "color": "#ef4444",
            "headline": "Your Inventory Is Actively Hurting Cash Flow",
            "message": "Excess stock, stockouts, and manual fixes are draining time and working capital."
        }
    

def calculate_question_scores():
    """
    Returns per-question scores as a dict:
    {
        "q1_score": 20,
        "q2_score": 14,
        ...
    }
    """
    scores = {}

    for i, q in enumerate(QUESTIONS):
        selected_answer = st.session_state.answers.get(i)
        if selected_answer:
            answer_index = q["options"].index(selected_answer)
            scores[f"q{i+1}_score"] = q["scores"][answer_index]
        else:
            scores[f"q{i+1}_score"] = 0

    return scores


# -------------------------------
# Contact lookup or creation
# -------------------------------
def get_or_create_contact(email):
    """Find or create contact in Baserow"""
    if not email or "@" not in email:
        st.error("Invalid email address.")
        return None
        
    # Search for existing contact
    search_params = {"filter__email__equal": email, "size": "1"}
    
    existing = baserow_api_request(
        "GET",
        f"database/rows/table/{st.secrets['CONTACTS_TABLE_ID']}/",
        params=search_params
    )
    
    if existing and existing.get('results'):
        return existing['results'][0]['id']
    
    # Create new contact
    new_contact = {
        "email": email,
        "first_name": "",
        "last_name": "",
        "company_name": "",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    created = baserow_api_request(
        "POST",
        f"database/rows/table/{st.secrets['CONTACTS_TABLE_ID']}/",
        data=new_contact
    )
    
    return created['id'] if created else None

# -------------------------------
# Results page
# -------------------------------
def results_page():    
    total_score, max_score, percentage = calculate_score()
    band = score_band(percentage)

    finalize_assessment_session(
        score=percentage,
        health_label=band["label"]
    )

    st.markdown("### Inventory Health Results")
    st.markdown("---")

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

    with col_left:
        st.markdown("#### Get Your PDF Report")
        st.markdown(
            "Want a **detailed, stakeholder-ready summary** of your results?\n\n"
            "**Enter your email** and we'll send you the full report."
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

                submit_pdf = st.form_submit_button("Download PDF Report")
                

                if submit_pdf:
                    if not email or "@" not in email:
                        st.error("Please enter a valid email address.")
                    else:                        
                        contact_id = get_or_create_contact(email)
                        if not contact_id:
                            st.error("Could not save your contact. Please try again.")
                            return
                        
                        if contact_id:
                            success = save_result_to_baserow(
                                contact_id=contact_id,
                                percentage=percentage,
                                max_score=max_score,
                                health_label=band["label"]  # Pass label for potential mapping
                            )
                            if not success:
                                st.error("We couldn't save your results. Please try again.")
                            st.session_state.email_submitted = True
                            st.success("✅ Your report is being prepared and will arrive shortly.")
                            st.session_state.page = "booking"
                            st.rerun()
                            
        else:
            st.info("📩 Your report request has already been submitted.")    


    col1, col2 = st.columns(2)

    with col2:
        
        if st.button("Finish → Book a Call"):
            # ✅ Ensure session is finalized BEFORE navigating
            finalize_assessment_session(percentage, band["label"])          
                    
            # ✅ Navigate to booking page
            st.session_state.page = "booking"
            st.rerun()


# -------------------------------
# Save assessment result
# -------------------------------
def save_result_to_baserow(contact_id, percentage, max_score, health_label):
    """Save assessment result to Baserow"""
    
    # CRITICAL FIX: Check valid options for 'health_level' Single Select field
    # You need to determine what text options are valid in your Baserow table
    
    question_scores = calculate_question_scores()

    result_data = {
        "contact": [contact_id],
        "overall_score": percentage,
        "max_score_possible": max_score,
        "health_level": HEALTH_MAP.get(health_label),
        "assessment_version": "v1",
        "report_status": "requested",
        "created_date": datetime.now().strftime("%Y-%m-%d"),  # European format YYYY-MM-DD
        "assessment_sessions": [st.session_state.session_id] if "session_id" in st.session_state else [],
        "session_token": st.session_state.session_token,
        **question_scores
    }
    
    result = baserow_api_request(
        "POST",
        f"database/rows/table/{st.secrets['RESULTS_TABLE_ID']}/",
        data=result_data
    )
    
    if result:
        st.success("✅ Result saved successfully!")    
        return True
    return False
    # Error is handled silently in baserow_api_request

# -------------------------------
# Set Up Booking
# -------------------------------

def booking_page():
    """
    Final booking page - opens Cal.com in new tab with session token
    """
    st.markdown("### Book Your Inventory Alignment Call")
    st.markdown(
        """
        Schedule a 30-minute call to review your results,
        identify risks, and outline concrete next steps.
        """
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Session token from validated session
    session_token = st.session_state.session_token
    cal_url = f"https://calcom.goxmit.com/oje-admin/claritymeeting?session_token={st.session_state.session_token}"
    
    # Booking button (opens in new tab via target="_blank")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <a href="{cal_url}" target="_blank">
                <button style="
                    width: 80%;
                    max-width: 400px;
                    background-color: #16a34a;
                    color: white;
                    font-weight: 600;
                    border-radius: 8px;
                    height: 3.5em;
                    border: none;
                    font-size: 1.1rem;
                    cursor: pointer;
                    margin: 0 auto;
                    display: block;
                ">
                    📅 Book Your 30-Minute Call
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Help text
    st.markdown(
        """
        <div style="
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 1rem;
            padding: 0 1rem;
        ">
            The booking calendar will open in a new tab.<br>
            We'll have your assessment results ready for our discussion.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Retake button (centered)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↺ Retake Assessment", use_container_width=True):
            reset_session()
            st.session_state.page = "landing"
            st.rerun()
# -------------------------------
# Page Routing
# -------------------------------
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "quiz":
    quiz_page()
elif st.session_state.page == "results":
    results_page()
elif st.session_state.page == "booking":
    booking_page()
