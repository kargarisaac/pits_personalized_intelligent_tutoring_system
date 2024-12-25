from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_embedding_model(model_provider):
    if model_provider == "openai":
        return OpenAIEmbedding()
    elif model_provider == "ollama":
        return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")


def get_llm_model(model_provider, model_name=None):
    if model_provider == "openai":
        from llama_index.llms.openai import OpenAI

        return OpenAI(model="gpt-4-1106-preview", max_tokens=4096)
    elif model_provider == "ollama":
        if not model_name:
            model_name = "qwen2.5:0.5b"
        return Ollama(model=model_name, temperature=0.7)
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")
