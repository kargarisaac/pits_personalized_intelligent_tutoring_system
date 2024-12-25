from llama_index.core import VectorStoreIndex, TreeIndex, load_index_from_storage
from llama_index.core import StorageContext
from global_settings import INDEX_STORAGE


def build_indexes(nodes):
    """
    Build or load Vector and Tree indexes for document processing.

    This function attempts to load existing indexes from storage first. If loading fails,
    it creates new indexes from the provided nodes and persists them to storage.

    The function creates two types of indexes:
    1. VectorStoreIndex:
        - Converts text into vector embeddings for semantic search
        - Optimized for question-answering and similarity searches
        - Used for finding relevant content based on meaning rather than exact matches
        - Used in:
            * quiz_builder.py: Generates quiz questions by searching relevant content
            * conversation_engine.py: Powers Q&A interactions and semantic search

    2. TreeIndex:
        - Creates a hierarchical structure of the document content
        - Used for understanding document organization and relationships
        - Enables multi-level summarization capabilities
        - Used in:
            * training_material_builder.py: Creates structured training content and
              generates slide content using hierarchical querying

    Args:
        nodes (List[Node]): List of LlamaIndex document nodes containing the processed text data

    Returns:
        tuple: A pair of indexes:
            - vector_index (VectorStoreIndex): For semantic search and Q&A operations
            - tree_index (TreeIndex): For hierarchical document structure and summarization

    Storage:
        Indexes are stored in the directory specified by INDEX_STORAGE (from global_settings).
        - Vector index is stored with index_id="vector"
        - Tree index is stored with index_id="tree"
    """
    try:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
        vector_index = load_index_from_storage(storage_context, index_id="vector")
        tree_index = load_index_from_storage(storage_context, index_id="tree")
        print("All indices loaded from storage.")
    except Exception as e:
        print(f"Error occurred while loading indices: {e}")
        storage_context = StorageContext.from_defaults()
        vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
        vector_index.set_index_id("vector")
        tree_index = TreeIndex(nodes, storage_context=storage_context)
        tree_index.set_index_id("tree")
        storage_context.persist(persist_dir=INDEX_STORAGE)
        print("New indexes created and persisted.")
    return vector_index, tree_index
