# Camada de RAG

Esta camada implementa recuperacao de contexto com base vetorial (Weaviate), memoria e pesquisa web.

## Funcionamento

A classe base `RAG` oferece busca semantica, escrita com chunking, exposicao como tool e suporte a filtros.
A classe `WebRAG` estende o comportamento para pesquisa externa (Tavily) com persistencia dos resultados.

### Principais Componentes

- `rag.py`: classes base `RAG`, `WebRAG`, enums `Backend` e `TypeAccess`.
- `memory.py`: colecao de memoria de longo prazo (`TypeAccess.ALL`).
- `library.py`: colecao de conhecimento tecnico (`TypeAccess.READ`).
- `research.py`: pesquisa web + armazenamento na colecao (`TypeAccess.ALL`).

## Como Criar uma Nova Colecao RAG

1. Crie um arquivo em `rag/`.
2. Herde de `RAG` (ou `WebRAG`).
3. Defina `collection_name`, `embedding`, `type_access` e metadados.
4. Instancie no model/agente como tool via `as_tool()`.

### Template (Blank Example)

Copie e cole o codigo abaixo para criar uma colecao de leitura:

```python
import os

from langchain_openai import OpenAIEmbeddings

from .rag import Backend, RAG, TypeAccess


class MinhaBaseConhecimento(RAG):
    description = "Base semantica para consultas tecnicas"

    backend = Backend.WEAVIATE
    collection_name = "ZEUSAI_CustomKnowledge"
    text_key = "content"
    type_access = TypeAccess.READ
    max_query_results = 5

    metadata_fields = ["source", "category", "created_at"]

    embedding = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    skip_init_checks = True
    port = 8080
```
