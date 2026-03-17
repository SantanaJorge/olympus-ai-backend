# Camada de Tools (Utilitários)

Esta pasta contém funções utilitárias e ferramentas auxiliares que são usadas transversalmente por várias camadas do sistema.

## Funcionamento

Diferente das outras camadas, `tools` não impõe uma estrutura rígida de classes. Geralmente contém scripts com funções puras (stateless) para tarefas específicas, como processamento de strings, cálculos matemáticos ou transformações de estruturas de dados.

### Exemplo Comum

*   **Agrupamento de Dados:** Funções para transformar listas planas (DataFrames) em estruturas hierárquicas (JSON aninhado).

## Como Adicionar uma Nova Tool

1.  Crie um novo arquivo em `tools/` com um nome descritivo (ex: `date_utils.py`).
2.  Defina suas funções utilitárias.
3.  Adicione *Type Hints* para clareza.

### Template (Blank Example)

Copie e cole o código abaixo para criar um novo utilitário:

```python
from typing import Any, List, Dict

def minha_funcao_utilitaria(dados: List[Any]) -> Dict[str, Any]:
    """
    Descreva o que a função faz.
    
    Args:
        dados: Lista de dados de entrada.
        
    Returns:
        Dicionário processado.
    """
    resultado = {}
    
    # Implemente a lógica aqui
    if not dados:
        return resultado
        
    for item in dados:
        # processamento...
        pass
        
    return resultado
```
