from .agent import Agent
from models.web_search import WebSearchModel


class WebSearchAgent(Agent):
    """Agente de busca na web via Tavily."""

    model = WebSearchModel
    owned_by = "Zeus"
    hidden = False
