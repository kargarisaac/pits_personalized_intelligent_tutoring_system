import streamlit as st
import os
from session_functions import save_session
from logging_functions import log_action
from global_settings import STORAGE_PATH
from document_uploader import ingest_documents
from training_material_builder import generate_slides
from index_builder import build_indexes
from quiz_builder import build_quiz
import pandas as pd


def user_onboarding():
    """
    Handles the user onboarding process in the Streamlit application.

    This function manages:
    - User name collection
    - Study subject selection
    - Study goal definition
    - File upload functionality
    - Difficulty level selection
    - Quiz assessment option
    - Document processing and indexing
    - Training material generation

    The function uses Streamlit session state to maintain user data across reruns
    and integrates with various backend services for document processing and quiz generation.

    Returns:
        None
    """
    # Get user's name
    user_name = st.text_input("What is your name?")
    if not user_name:
        return

    # Store user name in session state
    st.session_state["user_name"] = user_name
    st.write(f"Hello {user_name}. It's nice meeting you!")

    # Get study subject
    study_subject = st.text_input("What subject would you like to study?")
    if not study_subject:
        return

    # Store study subject in session state
    st.session_state["study_subject"] = study_subject
    st.write(f"Okay {user_name}, let's focus on {study_subject}.")

    # Get study goal
    study_goal = st.text_input(
        "Detail any specific goal for your study or just leave it blank:",
        key="Study Goal",
    )
    st.session_state["study_goal"] = study_goal or "No specific goal"

    # Handle file upload if study goal is provided
    if study_goal:
        st.write("Do you want to upload any study materials?")
        uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
        finish_upload = st.button("FINISH UPLOAD")

        # Process uploaded files
        if finish_upload and uploaded_files:
            saved_file_names = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(STORAGE_PATH, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_file_names.append(uploaded_file.name)
                st.write(f"You have uploaded {uploaded_file.name}")

            # Store uploaded files information in session state
            st.session_state["uploaded_files"] = saved_file_names
            st.session_state["finish_upload"] = True
            st.info("Uploading files...")

    # Handle difficulty level selection
    if "finish_upload" in st.session_state or "difficulty_level" in st.session_state:
        st.write("Please select your current knowledge level on the topic")
        difficulty_level = st.radio(
            "Current knowledge:",
            ["Beginner", "Intermediate", "Advanced", "Take a quiz to assess"],
        )
        st.session_state["difficulty_level"] = difficulty_level
        proceed_button = st.button("Proceed")
        st.write(f"Your choice: {difficulty_level}")

        # Process user selection and generate materials
        if proceed_button:
            save_session(st.session_state)
            if difficulty_level == "Take a quiz to assess":
                st.info("Proceeding to quiz. Ingesting study materials first...")
                nodes = ingest_documents()
                st.info("Materials loaded. Preparing indexes...")
                keyword_index, vector_index = build_indexes(nodes)
                st.info("Indexing complete. Generating quiz...")
                quiz = build_quiz(study_subject)
                st.session_state["show_quiz"] = True
                st.rerun()
                st.info("Indexing complete. Generating slides...")
                generate_slides(study_subject)
            else:
                # Log user's study preferences and generate materials
                log_action(
                    f"{user_name} wants to study the topic of {study_subject}, "
                    f"aiming to achieve the following goal: '{study_goal}'. "
                    f"The user uploaded {len(uploaded_files)} files and has self-assessed "
                    f"their current knowledge on the topic as {difficulty_level}",
                    action_type="ONBOARDING",
                )
                st.info(f"Proceeding with difficulty level {difficulty_level}")
                st.info("Ingesting study materials first...")
                nodes = ingest_documents()
                st.info("Materials loaded. Preparing indexes...")
                keyword_index, vector_index = build_indexes(nodes)
                st.info("Indexing complete. Generating slides...")
                generate_slides(study_subject)
