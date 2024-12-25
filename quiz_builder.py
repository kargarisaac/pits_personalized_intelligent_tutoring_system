# prepares quizz questions based on the uploaded files

from llama_index.core import load_index_from_storage, StorageContext
from llama_index.program.evaporate.df import DFRowsProgram
from llama_index.program.openai import OpenAIPydanticProgram
from global_settings import INDEX_STORAGE, QUIZ_SIZE, QUIZ_FILE
import pandas as pd


def build_quiz(topic: str) -> pd.DataFrame:
    """
    Builds a quiz by generating questions based on a given topic using a vector index.

    Args:
        topic (str): The subject matter for which quiz questions should be generated.

    Returns:
        pd.DataFrame: A DataFrame containing the generated quiz questions with columns:
            - Question_no: Sequential number of the question
            - Question_text: The actual question
            - Option1-4: Multiple choice options
            - Correct_answer: The correct option
            - Rationale: Explanation for the correct answer

    The function also saves the quiz to a CSV file specified in QUIZ_FILE.
    """
    df = pd.DataFrame(
        {
            "Question_no": pd.Series(dtype="int"),
            "Question_text": pd.Series(dtype="str"),
            "Option1": pd.Series(dtype="str"),
            "Option2": pd.Series(dtype="str"),
            "Option3": pd.Series(dtype="str"),
            "Option4": pd.Series(dtype="str"),
            "Correct_answer": pd.Series(dtype="str"),
            "Rationale": pd.Series(dtype="str"),
        }
    )
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    vector_index = load_index_from_storage(storage_context, index_id="vector")
    # This creates a program that can process and structure data into DataFrame rows.
    # It uses OpenAI's model to help parse unstructured data into a structured format
    # defined by Pydantic models.
    df_rows_program = DFRowsProgram.from_defaults(
        pydantic_program_cls=OpenAIPydanticProgram, df=df
    )
    # This creates a query engine from a vector index (presumably created earlier).
    # Vector indices are used for semantic search and similarity matching in documents.
    query_engine = vector_index.as_query_engine()
    # This sends a prompt to the query engine to generate quiz questions about a specific topic. The prompt specifies:
    # Number of questions (QUIZ_SIZE)
    # Topic to cover
    # Format (4 options per question)
    # Requirements (general questions, correct answer, rationale)
    response = query_engine.query(
        f"Create {QUIZ_SIZE} different quiz questions relevant for testing a candidate's knowledge about {topic}. Each question will have 4 answer options. Questions must be general topic-related, not specific to the provided text. For each question, provide also the correct answer and the answer rationale. The rationale must not make any reference to the provided context, any exams or the topic name. Only one answer option should be correct."
    )
    # This converts the generated quiz questions into a structured DataFrame format:
    # Processes the response through the DataFrame Rows Program
    # Converts the result into a DataFrame, incorporating any existing data
    result_obj = df_rows_program(input_str=response)
    # Saves the final DataFrame to a CSV file without including the index column.
    new_df = result_obj.to_df(existing_df=df)
    new_df.to_csv(QUIZ_FILE, index=False)
    return new_df
