# Camada de Agents

Esta camada expõe agentes declarativos para dois tipos de integração:

1. Endpoints de ferramentas (rotas customizadas, com `callback`).
2. Endpoints OpenAI-compatíveis (`/v1/models` e `/v1/chat/completions`) via agentes de chat.

## Funcionamento

As classes desta camada herdam de `Agent` (definida em `agent.py`).
Ao instanciar a classe, o registro é automático no servidor singleton.

### Principais Componentes

- `agent_definition`: metadados do agente (nome, descrição, schema de parâmetros, retorno).
- `urls` (ou `url`): lista de paths para aliases da mesma callback.
- `method` + `callback`: usados para endpoints de ferramentas.
- `model`: obrigatório; aceita classe ou instância de `models.model.Model`.

## Como Criar um Agente de Chat

1. Crie um arquivo em `agents/`.
2. Importe `Agent`.
3. Defina `model` com a classe (ou instância) do seu modelo.
4. Só implemente `chat(...)`/`chat_stream(...)` se quiser sobrescrever o comportamento padrão.
5. Instancie a classe no final do arquivo.

Exemplo:

```python
from .agent import Agent
from models.gpt import GPT


class MeuChatAgent(Agent):
    model = GPT


MeuChatAgent()
```
