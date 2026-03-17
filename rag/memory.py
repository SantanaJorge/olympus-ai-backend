# arquivo: agents/memory_collections.py

import os

from langchain_openai import OpenAIEmbeddings

from .rag import Backend, RAG, TypeAccess


class Memory(RAG):
    description = """
        Memória de longo prazo das conversas dos usuários do ZeusAI.
        Uma linha = um trecho/mensagem que você decidiu salvar como importante.
    """

    backend = Backend.WEAVIATE
    collection_name = "ZEUSAI_Memory"
    text_key = "content"
    type_access = TypeAccess.ALL
    max_query_results = 5

    # Campos extras que queremos poder ver no metadata
    metadata_fields = [
        "user_id",
        "chat_id",
        "role",
        "importance",
        "timestamp",
        "tags",
    ]

    # Embeddings da OpenAI (não deixar hardcoded em produção)
    embedding = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Client do Weaviate
    skip_init_checks = True
    port = 8080
