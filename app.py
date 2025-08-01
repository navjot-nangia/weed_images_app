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

    Attributes:
        species_dir (Path): Directory containing subfolders of species with JPG images.
        max_questions (int): Total number of quiz questions.
        species_metadata (dict): Dictionary mapping species names to lists of image paths.
    """

    def __init__(self, species_dir: str, max_questions: int = 5):
        """
        Initializes the quiz with the given species directory and max questions.

        Args:
            species_dir (str): Path to the directory containing species folders.
            max_questions (int): Maximum number of questions in the quiz.
        """
        self.species_dir = Path(species_dir)
        self.max_questions = max_questions
        self.species_metadata = self.map_species_to_images()

    def map_species_to_images(self):
        """
        Maps each species (subfolder name) to a list of image file paths.

        Returns:
            dict: A dictionary of species and their corresponding image paths.
        """
        species_metadata = defaultdict(list)
        for sub_dir in self.species_dir.iterdir():
            if sub_dir.is_dir():
                species_name = sub_dir.name
                for img_path in sub_dir.glob("*.JPG"):
                    species_metadata[species_name].append(str(img_path))
        
        # Save metadata to a JSON file for reference or debugging
        with open("data.json", "w") as f:
            json.dump(species_metadata, f, indent=4)

        return dict(species_metadata)

    def load_new_question(self):
        """
        Randomly selects a species and an image, then prepares options 
        including one correct and three incorrect answers. Updates Streamlit session state.
        """
        species_name = random.choice(list(self.species_metadata.keys()))
        image_path = random.choice(self.species_metadata[species_name])

        # Prepare three wrong options
        all_species = list(self.species_metadata.keys())
        wrong_choices = random.sample([s for s in all_species if s != species_name], 3)
        options = wrong_choices + [species_name]
        random.shuffle(options)

        # Update session state with new question data
        st.session_state.current_image_path = image_path
        st.session_state.correct_answer = species_name
        st.session_state.options = options
        st.session_state.answered = False

# --- Initialize Quiz ---
quiz = WeedQuiz(species_dir="assets", max_questions=5)

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
if "current_image_path" not in st.session_state:
    quiz.load_new_question()

# --- Display Quiz UI ---
MAX_QUESTIONS = quiz.max_questions

if st.session_state.question_num <= MAX_QUESTIONS:
    st.title("🌱 Weed Identification Quiz")
    st.markdown(f"**Question {st.session_state.question_num} of {MAX_QUESTIONS}**")
    st.markdown("What is the name of this weed?")

    # Display the quiz image
    img = Image.open(st.session_state.current_image_path)
    st.image(img, caption="Identify this weed", use_container_width=True)

    # Radio button for selecting answer
    selected = st.radio("Choose the correct species:", st.session_state.options, key=st.session_state.question_num)

    # Layout for Submit and Next buttons
    col1, col2 = st.columns([1, 1])

    with col1:
        submit_clicked = st.button("Submit Answer", key="submit")

    with col2:
        next_clicked = st.button("Next Question", key="next", disabled=not st.session_state.answered)

    # Submit logic
    if submit_clicked and not st.session_state.answered:
        st.session_state.answered = True
        if selected == st.session_state.correct_answer:
            st.success("✅ Correct!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Wrong! The correct answer was **{st.session_state.correct_answer}**.")

    # Next question logic
    if next_clicked and st.session_state.answered:
        st.session_state.question_num += 1
        if st.session_state.question_num <= MAX_QUESTIONS:
            quiz.load_new_question()
        else:
            # Quiz completed
            st.session_state.current_image_path = None

else:
    # Quiz Complete Page
    st.title("🎉 Quiz Complete!")
    st.markdown(f"Your final score: **{st.session_state.score} / {MAX_QUESTIONS}**")

    # Restart option
    if st.button("Play Again"):
        st.session_state.score = 0
        st.session_state.question_num = 1
        st.session_state.answered = False
        st.session_state.correct_answer = ""
        st.session_state.options = []
        quiz.load_new_question()
