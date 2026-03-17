import os

from langchain_openai import OpenAIEmbeddings
from .rag import Backend, TypeAccess, WebRAG

class Research(WebRAG):
    description = """
        Agente de Pesquisa (Research).
        Realiza buscas na web (via Tavily) para encontrar informações atualizadas
        e as armazena na base de conhecimento (RAG) para uso futuro.
    """

    backend = Backend.WEAVIATE
    collection_name = "ZEUSAI_Research"
    text_key = "content"
    type_access = TypeAccess.ALL
    max_query_results = 5
    max_web_results = 5
    skip_init_checks = True

    tavily_api_key = os.getenv("TAVILY_API_KEY")

    embedding = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
