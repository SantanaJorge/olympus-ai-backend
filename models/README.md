# Camada de Models

Esta camada define os modelos de chat e a orquestracao com LLMs, prompts e tools.

## Funcionamento

As classes desta camada herdam de `Model` (definida em `model.py`).
Cada modelo declara prompt, LLM e ferramentas; a execucao e feita via `AgentExecutor` do LangChain.

### Principais Componentes

- `model.py`: classe base abstrata com inicializacao, invoke/stream, formatacao de thought e contagem de tokens via tiktoken.
- `gpt.py`: modelo de proposito geral (`name = "gpt"`, alias no agente).
- `calculadora.py`: modelo com tools matematicas (`somar`, `subtrair`, `multiplicar`, `dividir`, `potencia`, `avaliar_expressao`).
- `diagnostic.py`: modelo especialista em diagnostico, com multitarefa e integracao com services.

## Como Criar um Novo Model

1. Crie um arquivo em `models/`.
2. Importe `Model`.
3. Defina `name`, `description`, `llm` e `prompt`.
4. Opcionalmente, defina `tools`, `agents`, `verbose` e `return_intermediate_steps`.
5. Associe o modelo a um agente na pasta `agents/`.

### Template (Blank Example)

Copie e cole o codigo abaixo para criar um novo model:

```python
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from .model import Model


class MeuModelo(Model):
    name = "meu-modelo"
    description = "Modelo base para tarefas especificas"

    llm = ChatOpenAI(
        model_name="gpt-5.1",
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    tools = []
    agents = []

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Voce e um assistente especializado."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
```
