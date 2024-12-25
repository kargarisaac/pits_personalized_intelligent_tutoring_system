# Conversation storage currently not working

import os
import json
import streamlit as st
from openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from global_settings import INDEX_STORAGE, CONVERSATION_FILE


def load_chat_store():
    """
    Load or create a new SimpleChatStore for storing conversation history.

    Returns:
        SimpleChatStore: A chat store object either loaded from CONVERSATION_FILE
                        or newly created if the file doesn't exist.
    """
    try:
        chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
    except FileNotFoundError:
        chat_store = SimpleChatStore()
    return chat_store


def display_messages(chat_store, container):
    """
    Display all messages from the chat history in a Streamlit container.

    Args:
        chat_store (SimpleChatStore): The chat store containing conversation history
        container (streamlit.container): Streamlit container to display messages in
    """
    with container:
        for message in chat_store.get_messages(key="0"):
            with st.chat_message(message.role):
                st.markdown(message.content)


def initialize_chatbot(user_name, study_subject, chat_store, container, context):
    """
    Initialize and configure the chatbot with necessary components.

    # OpenAIAgent vs ChatEngine
    The code uses OpenAIAgent instead of ChatEngine for several important reasons:
    1. Tool Integration:
    - OpenAIAgent is specifically designed to work with tools (like the QueryEngineTool in this code)
    - It can decide when and how to use these tools during conversation
    - ChatEngine is more basic and doesn't have built-in tool-using capabilities
    2. Function Calling:
    - OpenAIAgent leverages OpenAI's function calling feature
    - This allows for more structured and reliable tool usage
    - The agent can intelligently decide whether to use the study materials tool or respond directly
    3. Memory Management:
    - Both support memory, but OpenAIAgent has better integration with tools and memory simultaneously
    - The memory buffer helps maintain context while staying within token limits
    4. System Prompt Control:
    - OpenAIAgent provides better control over system prompts
    - It maintains the role (PITS, personal tutor) more consistently throughout the conversation
    5. Flexibility:
    - OpenAIAgent can be extended with multiple tools
    - It's easier to add new capabilities (like web search, calculators, etc.) in the future
    - The main trade-off is that OpenAIAgent is specifically tied to OpenAI's models, while ChatEngine is more model-agnostic. However, for this specific use case (a tutoring system with access to study materials), the benefits of OpenAIAgent's tool-using capabilities outweigh this limitation.

    Args:
        user_name (str): Name of the user for personalized interaction
        study_subject (str): The subject being studied
        chat_store (SimpleChatStore): Store for maintaining conversation history
        container (streamlit.container): Streamlit container for displaying messages
        context (str): Current slide content for context-aware responses

    Returns:
        OpenAIAgent: Configured agent with study materials tool and memory
    """
    # This creates a memory buffer for the chatbot. It stores the conversation history
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000, chat_store=chat_store, chat_store_key="0"
    )
    # Loading the vector index from storage
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    vector_index = load_index_from_storage(storage_context, index_id="vector")
    # Creating a query engine with top-3 similar results
    study_materials_engine = vector_index.as_query_engine(similarity_top_k=3)
    # Creating a tool that can be used by the agent to search study materials
    study_materials_tool = QueryEngineTool(
        query_engine=study_materials_engine,
        metadata=ToolMetadata(
            name="study_materials",
            description=(
                f"Provides official information about "
                f"{study_subject}. Use a detailed plain "
                f"text question as input to the tool."
            ),  # Describes how to use this tool
        ),
    )
    # Creating the OpenAI agent with the tool and memory
    agent = OpenAIAgent.from_tools(
        tools=[study_materials_tool],
        memory=memory,
        system_prompt=(
            f"Your name is PITS, a personal tutor. Your "
            f"purpose is to help {user_name} study and "
            f"better understand the topic of: "
            f"{study_subject}. We are now discussing the "
            f"slide with the following content: {context}"
        ),  # Defines the agent's role and context
    )
    display_messages(chat_store, container)
    return agent


def chat_interface(agent, chat_store, container):
    """
    Handle the chat interface and user interactions.

    Args:
        agent (OpenAIAgent): The configured chatbot agent
        chat_store (SimpleChatStore): Store for maintaining conversation history
        container (streamlit.container): Streamlit container for displaying messages
    """
    prompt = st.chat_input("Type your question here:")
    if prompt:
        with container:
            with st.chat_message("user"):
                st.markdown(prompt)
            response = str(agent.chat(prompt))
            with st.chat_message("assistant"):
                st.markdown(response)
        chat_store.persist(CONVERSATION_FILE)
