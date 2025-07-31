import streamlit as st
import random
import json
import os
from PIL import Image

st.set_page_config(page_title="🌿 Weed ID Quiz", layout="centered")

# --- Load Quiz Data ---
@st.cache_data
def load_quiz_data():
    with open("quiz_data.json", "r") as f:
        return json.load(f)

data = load_quiz_data()
MAX_QUESTIONS = 5  # You can change the number of rounds here

# --- Initialize Session State ---
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_num" not in st.session_state:
    st.session_state.question_num = 1
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = ""
if "options" not in st.session_state:
    st.session_state.options = []
if "current_species" not in st.session_state:
    st.session_state.current_species = None

# --- Setup a New Question ---
def load_new_question():
    species_entry = random.choice(data["species_metadata"])
    correct_answer = os.path.splitext(os.path.basename(species_entry["image_path"]))[0]
    all_species = list(set(data["weed_species"]) - {correct_answer})
    wrong_choices = random.sample(all_species, 3)
    options = wrong_choices + [correct_answer]
    random.shuffle(options)

    st.session_state.current_species = species_entry
    st.session_state.correct_answer = correct_answer
    st.session_state.options = options
    st.session_state.answered = False

# --- Load New Question at Start ---
if st.session_state.current_species is None:
    load_new_question()

# --- Display Quiz ---
if st.session_state.question_num <= MAX_QUESTIONS:
    st.title("🌱 Weed Identification Quiz")
    st.markdown(f"**Question {st.session_state.question_num} of {MAX_QUESTIONS}**")
    st.markdown(f"**{data['Question']}**")

    img = Image.open(st.session_state.current_species["image_path"])
    st.image(img, caption="Identify this weed", use_container_width=True)

    selected = st.radio("Choose the correct species:", st.session_state.options, key=st.session_state.question_num)

    col1, col2 = st.columns([1, 1])

    with col1:
        submit_clicked = st.button("Submit Answer", key="submit")

    with col2:
        next_clicked = st.button("Next Question", key="next", disabled=not st.session_state.answered)

    if submit_clicked and not st.session_state.answered:
        st.session_state.answered = True
        if selected == st.session_state.correct_answer:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Wrong! The correct answer was **{st.session_state.correct_answer}**.")

    if next_clicked and st.session_state.answered:
        st.session_state.question_num += 1
        if st.session_state.question_num <= MAX_QUESTIONS:
            load_new_question()
        else:
            st.session_state.current_species = None  # End of quiz

else:
    st.title("🎉 Quiz Complete!")
    st.markdown(f"Your final score: **{st.session_state.score} / {MAX_QUESTIONS}**")

    if st.button("Play Again"):
        st.session_state.score = 0
        st.session_state.question_num = 1
        st.session_state.answered = False
        st.session_state.correct_answer = ""
        st.session_state.options = []
        st.session_state.current_species = None
