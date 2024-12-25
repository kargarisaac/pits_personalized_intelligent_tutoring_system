import streamlit as st
import pandas as pd
from global_settings import QUIZ_FILE


def show_quiz(topic):
    """
    Display an interactive quiz interface using Streamlit and return the user's performance.

    Args:
        topic (str): The subject matter of the quiz to be displayed

    Returns:
        tuple: (level, score) where level is the user's assessed knowledge level
        and score is their numerical score, or None if quiz is not submitted
    """
    # Display the quiz header with the topic
    st.markdown(f"### Let's test your knowledge on {topic} with a quiz:")

    # Load quiz questions from CSV file
    df = pd.read_csv(QUIZ_FILE)

    # Dictionary to store user's answers
    answers = {}

    # Display each question as a radio button group
    for index, row in df.iterrows():
        question = row["Question_text"]
        options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
        answers[row["Question_no"]] = st.radio(
            question, options, index=None, key=row["Question_no"]
        )

    # Check if all questions have been answered
    all_answered = all(answer is not None for answer in answers.values())

    if all_answered:
        # Show submit button only when all questions are answered
        if st.button("SUBMIT ANSWERS"):
            score = 0
            # Calculate score by comparing user answers with correct answers
            for q_no in answers:
                user_answer_text = answers[q_no]
                correct_answer_text = df.loc[
                    df["Question_no"] == q_no, "Correct_answer"
                ].iloc[0]
                if user_answer_text == correct_answer_text:
                    score += 1

            # Calculate knowledge level based on score
            max_score = len(df)
            third_of_max = max_score / 3
            level = ""

            # Assign knowledge level based on score ranges
            if score <= third_of_max:
                level = "Beginner"
            elif third_of_max < score <= 2 * third_of_max:
                level = "Intermediate"
            else:
                level = "Advanced"

            # Display results to user
            st.write(f"Your score is: {score}/{max_score}")
            st.write(f"Your level of knowledge: {level}")
            return level, score
