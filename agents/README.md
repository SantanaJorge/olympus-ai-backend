# Camada de Agents

Esta camada expõe agentes declarativos para dois tipos de integração:

1. **Endpoints de chat** — compatíveis com OpenAI (`/v1/models` e `/v1/chat/completions`).
2. **Endpoints de ferramentas** — rotas customizadas com `callback` (quando necessário).

## Funcionamento

As classes desta camada herdam de `Agent` (definida em `agent.py`).
Ao instanciar a classe, o registro é automático no servidor singleton via `__init_subclass__`.
O `agents/__init__.py` importa todos os arquivos `.py` da pasta, acionando esse registro automaticamente ao iniciar o servidor.

## Agentes Disponíveis

### `athena.py` — AthenaAgent

Agente do planner estratégico completo.

```python
class AthenaAgent(Agent):
    model = AthenaModel
    model_aliases = ["athena"]
    owned_by = "zeus"
```

- Modelo: `AthenaModel` (GPT-5.4)
- Ideal para análises complexas, diagnósticos detalhados e planejamento estratégico
- Acessível pelo nome `"athena"` no campo `model` da requisição

---

### `saori.py` — SaoriAgent

Agente do planner ágil e econômico.

```python
class SaoriAgent(Agent):
    model = SaoriModel
    model_aliases = ["saori"]
    owned_by = "zeus"
```

- Modelo: `SaoriModel` (GPT-5-mini)
- Ideal para tarefas simples, respostas rápidas e uso cotidiano
- Acessível pelo nome `"saori"` no campo `model` da requisição

---

## Principais Componentes de `agent.py`

| Atributo | Descrição |
|---|---|
| `model` | Classe ou instância de `Model` (obrigatório) |
| `model_aliases` | Nomes alternativos para referenciar o modelo na API |
| `owned_by` | Organização proprietária (exibido em `/v1/models`) |
| `urls` | Lista de paths para endpoints de ferramentas (opcional) |
| `method` | Método HTTP para endpoints de ferramentas (ex: `"POST"`) |
| `callback` | Função executada ao atingir a rota de ferramenta |

**Métodos principais:**

- `chat(messages, model, request_data)` — executa via `model.invoke()`
- `chat_stream(messages, model, request_data)` — executa via `model.stream()`
- `_to_langchain_history()` — converte mensagens para `HumanMessage`/`AIMessage`
- `_build_generation_params()` — extrai parâmetros LLM da requisição (`temperature`, `top_p`, `max_tokens`, etc.)

## Como Criar um Novo Agente de Chat

1. Crie um arquivo em `agents/`.
2. Importe `Agent` e o modelo desejado.
3. Defina `model` e, opcionalmente, `model_aliases` e `owned_by`.
4. Instancie a classe no final do arquivo.

```python
from .agent import Agent
from models.meu_modelo import MeuModelo


class MeuAgente(Agent):
    model = MeuModelo
    model_aliases = ["meu-agente"]
    owned_by = "minha-org"


MeuAgente()
```

## Como Criar um Agente com Rota de Ferramenta

```python
from .agent import Agent
from models.meu_modelo import MeuModelo


def minha_callback(param1, param2):
    return {"resultado": param1 + param2}


class MeuAgenteComRota(Agent):
    model = MeuModelo
    model_aliases = ["meu-agente"]
    urls = ["/minha-rota"]
    method = "POST"
    callback = minha_callback
    agent_definition = {
        "name": "minha-ferramenta",
        "description": "Descrição da ferramenta",
        "parameters": {
            "param1": {"type": "string", "description": "Primeiro parâmetro"},
            "param2": {"type": "string", "description": "Segundo parâmetro"},
        },
        "returns": {"type": "object"},
    }


MeuAgenteComRota()
```
