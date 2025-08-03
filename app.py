import streamlit as st
import random
import json
from pathlib import Path
from collections import defaultdict
from PIL import Image

# Set Streamlit page configuration
st.set_page_config(page_title="🌿 Weed ID Quiz", layout="centered")

class WeedQuiz:
    """
    A class to handle the logic of the Weed Identification Quiz.
    """
    def __init__(self, species_dir: str):
        self.species_dir = Path(species_dir)
        self.species_metadata = self.map_species_to_images(save_debug=False)

    def map_species_to_images(self, save_debug=False):
        species_metadata = defaultdict(list)
        for sub_dir in self.species_dir.iterdir():
            if sub_dir.is_dir():
                species_name = sub_dir.name
                for img_path in list(sub_dir.glob("*.JPG")) + list(sub_dir.glob("*.jpg")):
                    species_metadata[species_name].append(str(img_path))

        if save_debug:
            with open("data.json", "w") as f:
                json.dump(species_metadata, f, indent=4)

        return dict(species_metadata)

    def load_new_question(self):
        species_name = random.choice(list(self.species_metadata.keys()))
        image_path = random.choice(self.species_metadata[species_name])

        all_species = list(self.species_metadata.keys())
        wrong_choices = random.sample([s for s in all_species if s != species_name], 3)
        options = wrong_choices + [species_name]
        random.shuffle(options)

        st.session_state.current_image_path = image_path
        st.session_state.correct_answer = species_name
        st.session_state.options = options
        st.session_state.answered = False
        st.session_state.pop("selected_option", None)  # Reset selection

# --- Helper Functions ---
def init_session_state():
    defaults = {
        "score": 0,
        "question_num": 1,
        "answered": False,
        "correct_answer": "",
        "options": [],
        "current_image_path": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_quiz():
    st.session_state.score = 0
    st.session_state.question_num = 1
    st.session_state.answered = False
    st.session_state.correct_answer = ""
    st.session_state.options = []
    st.session_state.current_image_path = None
    st.session_state.quiz_started = False
    st.session_state.pop("selected_option", None)
    st.session_state.pop("feedback", None)

# --- Initialize ---
quiz = WeedQuiz(species_dir="assets")
init_session_state()

# --- Question count input before quiz starts ---
if "max_questions" not in st.session_state:
    st.session_state.max_questions = 5  # default value

if st.session_state.question_num == 1 and not st.session_state.get("quiz_started", False):
    st.title("🌱 Weed Identification Quiz Setup")
    st.session_state.max_questions = st.number_input("How many questions do you want?", min_value=1, max_value=50, value=5, step=1)

    def start_quiz():
        st.session_state.quiz_started = True
        quiz.load_new_question()

    st.button("Start Quiz", on_click=start_quiz)
    st.stop()

# --- Load First Question if Needed ---
if st.session_state.current_image_path is None:
    quiz.load_new_question()

# --- UI Layout ---
if st.session_state.question_num <= st.session_state.max_questions:
    st.title("🌱 Weed Identification Quiz")
    st.markdown(f"**Question {st.session_state.question_num} of {st.session_state.max_questions}**")
    st.progress(st.session_state.question_num / st.session_state.max_questions)
    st.markdown("What is the name of this weed?")

    # Display score
    st.markdown(f"**Current Score:** {st.session_state.score} / {st.session_state.max_questions}")

    # Display image
    img = Image.open(st.session_state.current_image_path)
    st.image(img, caption="Identify this weed", use_container_width=True)

    # Answer selection
    selected = st.radio("Choose the correct species:", st.session_state.options, key="selected_option")

    def handle_submit():
        if not st.session_state.answered:
            st.session_state.answered = True
            if st.session_state.selected_option == st.session_state.correct_answer:
                st.session_state.score += 1
                st.session_state.feedback = "correct"
            else:
                st.session_state.feedback = "wrong"

    def handle_next():
        st.session_state.question_num += 1
        if st.session_state.question_num <= st.session_state.max_questions:
            quiz.load_new_question()
        else:
            st.session_state.current_image_path = None  # Triggers quiz complete
        st.session_state.feedback = None

    # Show feedback from last question
    if "feedback" in st.session_state:
        if st.session_state.feedback == "correct":
            st.success("✅ Correct!")
        elif st.session_state.feedback == "wrong":
            st.error(f"❌ Wrong! The correct answer was **{st.session_state.correct_answer}**.")

    # Buttons with on_click handlers
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("✅ Submit Answer", on_click=handle_submit, disabled=st.session_state.answered)
    with col2:
        st.button("➡️ Next Question", on_click=handle_next, disabled=not st.session_state.answered)

# --- Quiz Complete ---
else:
    st.title("🎉 Quiz Complete!")
    st.markdown(f"Your final score: **{st.session_state.score} / {st.session_state.max_questions}**")

    st.button("🔁 Play Again", on_click=reset_quiz)
