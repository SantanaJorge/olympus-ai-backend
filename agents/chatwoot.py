from .agent import Agent
from models.chatwoot import ChatwootModel


class ChatwootAgent(Agent):
    """Agente de atendimento especializado para o Chatwoot, com acesso ao OneDrive."""

    model = ChatwootModel
    model_aliases = ["gpt-4.1-mini"]
    owned_by = "Zeus"
    hidden = True
