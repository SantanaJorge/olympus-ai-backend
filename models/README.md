# Camada de Models

Esta camada define os modelos de chat e a orquestração com LLMs, prompts e tools.

## Funcionamento

As classes desta camada herdam de `Model` (definida em `model.py`).
Cada modelo declara prompt, LLM e ferramentas; a execução é feita via `AgentExecutor` do LangChain.

## Modelos Disponíveis

### `model.py` — Classe Base

Classe abstrata com:

- `invoke()` / `stream()` — executa o agente com histórico de mensagens
- `_count_tokens()` — contagem de tokens via tiktoken
- `as_tool()` — converte o modelo em `StructuredTool` do LangChain (para uso como agente filho)
- `_format_intermediate_steps()` — formata o raciocínio intermediário

Atributos obrigatórios nas subclasses: `name`, `description`, `llm`, `prompt`.

---

### `athena.py` — AthenaModel

**Planner estratégico completo.**

| Atributo | Valor |
|---|---|
| `name` | `"athena"` |
| `llm` | GPT-5.4 (temperature=0.2) |
| `verbose` | True |
| `return_intermediate_steps` | True |

Athena é o ponto de entrada principal. Ela entende a intenção do usuário, delega diagnósticos para o `DiagnosticFullModel` (como agente filho) e sintetiza os resultados em respostas estratégicas e acionáveis.

---

### `saori.py` — SaoriModel

**Planner ágil e econômico.**

| Atributo | Valor |
|---|---|
| `name` | `"saori"` |
| `llm` | GPT-5-mini (temperature=0.2) |
| `verbose` | True |
| `return_intermediate_steps` | True |

Saori é otimizada para tarefas simples e respostas rápidas. Delega diagnósticos para o `DiagnosticLiteModel` e prioriza concisão (resposta em 3 linhas em vez de relatórios longos).

---

### `diagnostic_full.py` — DiagnosticFullModel

**Agente de diagnóstico completo com execução paralela.**

| Atributo | Valor |
|---|---|
| `name` | `"diagnosis"` |
| `llm` | GPT-5.4 (temperature=0.1) |
| `verbose` | True |
| `return_intermediate_steps` | True |

Usado como agente filho de `AthenaModel`. Executa verificações em paralelo via `ThreadPoolExecutor`.

**Tools:**

| Tool | Descrição |
|---|---|
| `get_park_overview` | Visão geral do parque (métricas globais + PICs offline/standby) em paralelo |
| `get_pics` | Lista PICs filtrando por cliente, status, modelo e hardware |
| `run_complete_diagnosis` | Diagnóstico completo: executa `check_lora_network`, `check_wifi_network`, `check_battery` e `check_solar_panel` em paralelo |
| `make_grafana_link` | Gera link do dashboard Grafana com filtros dinâmicos de PICs |

---

### `diagnostic_lite.py` — DiagnosticLiteModel

**Agente de diagnóstico rápido.**

| Atributo | Valor |
|---|---|
| `name` | `"diagnosis"` |
| `llm` | GPT-5-mini (temperature=0.1) |

Usado como agente filho de `SaoriModel`. Expõe as mesmas tools do `DiagnosticFullModel`, mas com modelo mais leve, priorizando velocidade e custo.

---

## Hierarquia de Modelos

```
AthenaModel (gpt-5.4)
└── DiagnosticFullModel (gpt-5.4)   ← agente filho

SaoriModel (gpt-5-mini)
└── DiagnosticLiteModel (gpt-5-mini) ← agente filho
```

## Como Criar um Novo Model

1. Crie um arquivo em `models/`.
2. Importe `Model`.
3. Defina `name`, `description`, `llm` e `prompt`.
4. Opcionalmente, defina `tools`, `agents`, `verbose` e `return_intermediate_steps`.
5. Associe o modelo a um agente na pasta `agents/`.

### Template

```python
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from .model import Model


class MeuModelo(Model):
    name = "meu-modelo"
    description = "Modelo base para tarefas específicas"

    llm = ChatOpenAI(
        model_name="gpt-5.1",
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    tools = []
    agents = []

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Você é um assistente especializado."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
```
