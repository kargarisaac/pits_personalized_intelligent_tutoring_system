from global_settings import STORAGE_PATH, CACHE_FILE, DEFAULT_MODEL_PROVIDER
from logging_functions import log_action
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.core import SimpleDirectoryReader
from llama_index.core.storage.kvstore import SimpleKVStore
from llama_index.embeddings.openai import OpenAIEmbedding
import os


def ingest_documents(model_provider=None):
    """
    Processes and ingests documents from a specified storage path for use in the application.

    This function performs several key operations:
    1. Reads documents from the STORAGE_PATH directory
    2. Logs each document upload
    3. Initializes or loads an existing cache
    4. Processes documents through an ingestion pipeline that:
       - Splits text into manageable chunks
       - Generates summaries
       - Creates embeddings using OpenAI's embedding model

    Args:
        model_provider (str, optional): The model provider to use for processing.
            Defaults to DEFAULT_MODEL_PROVIDER if None.

    Returns:
        list: A list of processed nodes containing the document chunks with their
             embeddings and metadata.

    Raises:
        FileNotFoundError: If STORAGE_PATH directory doesn't exist
        Exception: If there are issues with document processing or embedding generation
    """
    if model_provider is None:
        model_provider = DEFAULT_MODEL_PROVIDER

    documents = SimpleDirectoryReader(STORAGE_PATH, filename_as_id=True).load_data()

    for doc in documents:
        print(doc.id_)
        log_action(f"File '{doc.id_}' uploaded user", action_type="UPLOAD")

    # Initialize cache with SimpleKVStore
    cache = (
        SimpleKVStore.from_persist_path(CACHE_FILE)
        if os.path.isfile(CACHE_FILE)
        else SimpleKVStore()
    )
    ingest_cache = IngestionCache(cache=cache)

    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(chunk_size=1024, chunk_overlap=20),
            SummaryExtractor(summaries=["self"]),
            OpenAIEmbedding(),
        ],
        cache=ingest_cache,
    )

    nodes = pipeline.run(documents=documents)

    # Persist the pipeline state
    pipeline.persist(persist_dir=CACHE_FILE)
    return nodes
