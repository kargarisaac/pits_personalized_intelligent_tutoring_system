# pip install llama-index-program-evaporate

from llama_index.core import TreeIndex, load_index_from_storage
from llama_index.core.storage import StorageContext
from llama_index.core.extractors import KeywordExtractor
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.program.evaporate.df import DFRowsProgram
from llama_index.core.schema import TextNode
from llama_index.llms.openai import OpenAI

from global_settings import STORAGE_PATH, INDEX_STORAGE, CACHE_FILE, SLIDES_FILE
from logging_functions import log_action
from document_uploader import ingest_documents
from slides import Slide, SlideDeck
import pandas as pd
import streamlit as st
from collections import Counter


def generate_slides(topic):
    """
    Generates a complete slide deck with narration for a given topic using LLM and document embeddings.

    This function creates a comprehensive training material package by processing source documents,
    extracting relevant information, and generating structured content using LLM capabilities.

    Detailed Process Flow:
    1. Document Processing:
        - Loads pre-ingested documents or processes new ones via ingest_documents()
        - Documents are embedded and stored as nodes with metadata

    2. Keyword Analysis:
        - Extracts summaries from document nodes
        - Uses KeywordExtractor to identify key concepts (top 10 keywords per summary)
        - Counts keyword frequencies across all documents
        - Filters out generic terms using LLM to keep topic-specific keywords
        - Creates a refined keyword list for course structure

    3. Course Structure Generation:
        - Uses LLM to create a hierarchical course outline
        - Ensures coverage of all important keywords
        - Structures content from basic to advanced concepts
        - Organizes content into sections and subsections
        - Converts outline into a structured DataFrame

    4. Content Generation:
        - Loads pre-built tree index for context retrieval
        - For each topic in the outline:
            * Generates expert-level narration using document context
            * Creates concise bullet points (max 7 per slide)
            * Builds slide objects with section, topic, narration, and bullets
        - Combines all slides into a complete deck

    Some notes:
    - The summaries serve as:
        Condensed representations of document sections
        Source for keyword extraction (better than using full text)
        Intermediate step between raw documents and final content
        Way to reduce noise and focus on key concepts

    - The keyword system serves multiple purposes:
        Identifies core concepts from source materials
        Ensures course coverage of important topics
        Guides the LLM in creating a comprehensive course outline
        Acts as a content validation mechanism
        Helps maintain focus on topic-specific concepts

    - The TreeIndex is chosen over a VectorIndex for several reasons:
        It creates a hierarchical representation of documents, similar to a table of contents
        Better for preserving document structure and relationships between concepts
        More suitable for educational content where topics build upon each other
        Provides "compact" response mode that summarizes information from multiple related nodes
        Better at maintaining context when generating comprehensive explanations

    - The workflow is:
        Documents are processed into a TreeIndex for structured retrieval
        Summaries are extracted to identify key concepts
        Keywords guide course outline creation
        TreeIndex provides context for detailed content generation
        Each component ensures the final content is:
            Comprehensive (keywords)
            Well-structured (tree)
            Coherent (summaries)
            Properly sequenced (hierarchical structure)

    Args:
        topic (str): The main subject for which to generate training materials.
                    Should be specific enough to guide content generation but
                    broad enough to allow comprehensive coverage.

    Returns:
        None: Saves the generated slide deck to SLIDES_FILE location.
              The saved deck contains:
              - Complete slide hierarchy
              - Section and subsection organization
              - Detailed narration for each slide
              - Bullet points for visual presentation
    """
    # Initialize OpenAI LLM with specific parameters
    llm = OpenAI(temperature=0.5, model="gpt-4o-mini", max_tokens=4096)

    # Step 1: Load and process documents
    with st.spinner("Loading documents..."):
        # Get embedded document nodes from cache or new ingestion
        embedded_nodes = ingest_documents()
        st.info("Docs loaded!")

    # Step 2: Extract and process keywords
    with st.spinner("Preparing summaries and keywords..."):
        # Create nodes from document summaries
        summary_nodes = []
        for node in embedded_nodes:
            summary = node.metadata["section_summary"]
            summary_node = TextNode(text=summary)
            summary_nodes.append(summary_node)

        # Extract keywords from summaries using KeywordExtractor
        # Keywords are extracted to:
        # 1. Identify main concepts from source materials
        key_extractor = KeywordExtractor(keywords=10)
        entities = key_extractor.extract(summary_nodes)

        # Flatten and count keyword occurrences
        flattened_keywords = []
        for entity in entities:
            if "excerpt_keywords" in entity:
                excerpt_keywords = entity["excerpt_keywords"]
                flattened_keywords.extend(
                    [keyword.strip() for keyword in excerpt_keywords.split(",")]
                )

        # 2. Count frequency to find important terms
        keyword_counts = Counter(flattened_keywords)

        # Sort keywords by frequency
        sorted_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )
        keywords_only = [keyword for keyword, count in sorted_keywords if count > 1]

        # Filter out generic keywords using LLM
        specific_keywords = ""
        for i in range(0, len(keywords_only), 15):
            group = keywords_only[i : i + 15]
            group_str = ", ".join(group)
            # 3. Filter to keep only topic-specific terms
            response = llm.complete(
                f"""Eliminate any keyword which is generic and not precisely 
                specific to the topic of {topic}. 
                Format as comma separated. List just the remaining keywords: 
                {group_str}"""
            )
            specific_keywords += str(response) + ","
        st.info("Keywords and summaries prepared!")

    # Step 3: Generate course outline
    with st.spinner("Creating the course outline..."):
        # Generate structured outline using LLM
        response = llm.complete(
            f"""Create a structured course outline for a course about {topic}. 
            The outline should be divided in sections and each section should 
            be divided in several topics. Each section should have a sufficient
            number of topics to cover the entire knowledge area. The outline 
            will contain a gradual introduction of concepts, starting with a 
            general introduction on the subject and then covering more advanced areas. 
            Respond with one line per section using this format: 
            <SECTION TITLE, TOPIC 1, TOPIC 2, TOPIC 3, ... TOPIC n>. 
            Make sure the outline completely covers these keywords: {specific_keywords}"""
        )

        # Convert outline to DataFrame
        df = pd.DataFrame(
            {"Section": pd.Series(dtype="str"), "Topics": pd.Series(dtype="str")}
        )
        df_rows_program = DFRowsProgram.from_defaults(
            pydantic_program_cls=OpenAIPydanticProgram, df=df
        )
        result_obj = df_rows_program(input_str=response)
        outline = result_obj.to_df(existing_df=df)
        st.info("Course outline complete!")

    # Step 4: Generate slides and narration
    with st.spinner(
        "Creating the course slides and narration. This might take a while..."
    ):
        # Load index for context retrieval
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
        tree_index = load_index_from_storage(storage_context, index_id="tree")

        # Generate slides for each topic in the outline
        slides = []
        for index, row in outline.iterrows():
            section = row["Section"]
            topics = row["Topics"].split("; ")
            for slide_topic in topics:
                print(f"Generating content for: {section} - {slide_topic}")
                # Create query engine for context retrieval
                query_engine = tree_index.as_query_engine(response_mode="compact")
                # Generate narration using retrieved context
                narration = str(
                    query_engine.query(
                        f"You are an expert {topic} trainer. You are now covering the section titled '{section}'. Introduce and explain the concept of '{slide_topic}' to your students. Respond as you are the trainer."
                    )
                )
                # Generate bullet points from narration
                summary = llm.complete(
                    f"Summarize the essential concepts from this text as maximum 7 very short slide bullets without verbs: {narration}\n The general topic of the presentation is {topic}\n The slide title is {section+'-'+slide_topic} List the bullets separated with semicolons like this: BULLET1, BULLET2, ...: "
                )
                bullets = str(summary).split(";")
                # Create and store slide
                slide = Slide(section, slide_topic, narration, bullets)
                slides.append(slide)
        st.info("Slides and narration generated!")

    # Create and save final slide deck
    slide_deck = SlideDeck(topic, slides)
    slide_deck.save_to_file(SLIDES_FILE)
