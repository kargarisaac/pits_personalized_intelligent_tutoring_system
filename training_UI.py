import streamlit as st
from slides import Slide, SlideDeck
import json
from openai import OpenAI
from pathlib import Path
from conversation_engine import initialize_chatbot, chat_interface, load_chat_store


def show_training_UI(user_name, study_subject):
    """
    Display the training user interface with slides and an interactive chatbot.

    Args:
        user_name (str): The name of the current user
        study_subject (str): The subject being studied/discussed

    The function creates a two-column layout:
    - Left column (70%): Displays slides with optional narration
    - Right column (30%): Interactive chatbot interface
    """
    # Load the slide deck from cached JSON file
    slide_deck = SlideDeck.load_from_file("cache/slides.json")

    # Set up the sidebar with topic and navigation controls
    st.sidebar.markdown("## " + slide_deck.topic)
    current_slide_index = st.sidebar.number_input(
        "Slide Number",
        min_value=0,
        max_value=len(slide_deck.slides) - 1,
        value=0,
        step=1,
    )

    # Get the current slide based on the index
    current_slide = slide_deck.slides[current_slide_index]

    # Add a toggle button for narration display
    if st.sidebar.button("Toggle narration"):
        st.session_state.show_narration = not st.session_state.get(
            "show_narration", False
        )

    # Create two columns: 70% for slides, 30% for chatbot
    col1, col2 = st.columns([0.7, 0.3], gap="medium")

    # Left column: Display the current slide with optional narration
    with col1:
        st.markdown(
            current_slide.render(
                display_narration=st.session_state.get("show_narration", False)
            ),
            unsafe_allow_html=True,
        )

    # Right column: Set up the chatbot interface
    with col2:
        st.header("💬 P.I.T.S. Chatbot")
        # Display welcome message
        st.success(
            f"Hello {user_name}. I'm here to answer questions about {study_subject}"
        )
        # Load the chat history
        chat_store = load_chat_store()
        # Create a scrollable container for chat messages
        container = st.container(height=600)
        # Get the current slide content as context
        context = current_slide.render(display_narration=False)
        # Initialize the chatbot with user info and context
        agent = initialize_chatbot(
            user_name, study_subject, chat_store, container, context
        )
        # Display the chat interface
        chat_interface(agent, chat_store, container)
