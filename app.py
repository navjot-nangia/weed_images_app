import streamlit as st
import json
from PIL import Image

st.set_page_config(page_title="🌿 Weed ID Quiz", layout="centered")

# --- Background and Styling ---
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #f1f8e9, #e0f7fa);
        }
        .main {
            background-color: #ffffffcc;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
        }
        h1, h3, h5 {
            text-align: center;
        }
        .stButton>button {
            font-size: 1.2em;
            padding: 0.6em 1.2em;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Quiz Data ---
@st.cache_data
def load_quiz():
    with open("quiz_data.json", "r") as f:
        return json.load(f)

questions = load_quiz()

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "start"
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# --- Navigation Functions ---
def start_quiz():
    st.session_state.page = "quiz"
    st.session_state.score = 0
    st.session_state.question_index = 0
    st.session_state.answered = False
    st.session_state.selected_option = None

def next_question():
    st.session_state.question_index += 1
    st.session_state.answered = False
    st.session_state.selected_option = None
    if st.session_state.question_index >= len(questions):
        st.session_state.page = "end"

# --- START Page ---
if st.session_state.page == "start":
    st.markdown("<h1>🌿 WEEDS QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Can you identify these weeds?</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Quiz", use_container_width=True):
            start_quiz()

# --- QUIZ Page ---
elif st.session_state.page == "quiz":
    q = questions[st.session_state.question_index]

    st.markdown(f"<h5>Score: {st.session_state.score} / {st.session_state.question_index}</h5>", unsafe_allow_html=True)
    st.image(Image.open(q["image_path"]), use_container_width=True)
    st.subheader(q["question"])

    # Disable radio if answered
    disabled = st.session_state.answered

    selected = st.radio(
        "Choose one:",
        q["options"],
        index=q["options"].index(st.session_state.selected_option) if st.session_state.selected_option else None,
        disabled=disabled,
        key=f"question_{st.session_state.question_index}"
    )

    if not disabled:
        st.session_state.selected_option = selected

    if st.button("Submit", disabled=disabled) and not st.session_state.answered and selected:
        st.session_state.answered = True
        if selected == q["correctAnswer"]:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {q['correctAnswer']}")

    if st.session_state.answered:
        st.button("Next", on_click=next_question)

# --- END Page ---
elif st.session_state.page == "end":
    st.balloons()
    st.markdown("<h1>🎉 Quiz Complete!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3>Your Final Score:</h3>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:green; text-align:center'>{st.session_state.score} / {len(questions)}</h2>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Restart Quiz"):
        st.session_state.page = "start"
