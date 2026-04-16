import os

from search.tavily import TavilySearch


class WebSearch(TavilySearch):
    """
    Busca web direta via Tavily, sem cache persistente.
    Use para obter informações atualizadas da internet.
    """

    description = """
        Ferramenta de busca na web (via Tavily).
        Use para encontrar informações atualizadas, notícias recentes,
        dados em tempo real ou qualquer conteúdo disponível na internet.
        Apenas busca é permitida.
    """

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    max_web_results = 5
