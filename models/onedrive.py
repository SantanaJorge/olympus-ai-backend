import datetime as dt

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from stores.onedrive import OneDrive
from llm import LLM
from .model import Model


class OneDriveModel(Model):
    name = "onedrive"

    description = (
        "Assistente especializado em busca de documentos do OneDrive. "
        "Use para encontrar informações em arquivos, documentos e conteúdos sincronizados."
    )

    verbose = True
    return_intermediate_steps = True

    llm = LLM("gpt-5-mini", temperature=0.1)

    tools = [OneDrive().as_tool()]

    thought_labels = {
        "OneDrive": "Buscando nos documentos do OneDrive...",
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
                Você é um assistente especializado em busca de documentos e informações
                armazenados no **OneDrive** da organização.

                **HOJE:** {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

                ---

                # Ferramenta disponível

                ## `OneDrive`
                Base de conhecimento com documentos sincronizados do OneDrive.
                Use para qualquer pergunta sobre conteúdo de arquivos, documentos ou procedimentos.

                ---

                # Como agir

                - Sempre consulte o OneDrive antes de responder.
                - Cite o documento de origem quando encontrar informação relevante.
                - Se não encontrar resultado, informe claramente — não invente. Fale apenas que nao achou nada relacionado nos documentos.
                - Seja objetivo: destaque a informação relevante sem reproduzir o documento inteiro.
                """,
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
