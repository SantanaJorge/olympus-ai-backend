import os

#from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from .rag import Backend, RAG, TypeAccess


class Library(RAG):
    description = """
        Biblioteca de conhecimento.
        Use esta ferramenta para buscar informações técnicas, manuais, documentações e procedimentos.
        Apenas busca é permitida.
    """

    backend = Backend.WEAVIATE
    #collection_name = "VERBA_Embedding_text_embedding_3_small"
    #collection_name = "VERBA_Embedding_nomic_embed_text"
    collection_name = "VERBA_Embedding_text_embedding_3_large"

    text_key = "content"
    
    type_access = TypeAccess.READ
    max_query_results = 5

    #embedding = OllamaEmbeddings(
    #    model="nomic-embed-text",
    #)
    embedding = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    skip_init_checks = True
    port = 8080
