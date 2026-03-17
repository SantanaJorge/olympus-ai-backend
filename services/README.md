# Camada de Services

Esta camada concentra integracoes externas e operacoes de negocio reutilizaveis pelos modelos.

## Funcionamento

A implementacao atual utiliza `MCPDiagnosisService`, que encapsula chamadas HTTP para um backend de diagnostico.
O servico normaliza payloads, aplica autenticacao Bearer, trata timeout/erros e pode serializar resposta em TOON.

### Principais Componentes

- `mcp_diagnosis.py`: cliente HTTP com metodos de diagnostico (`get_pics`, `check_wifi_network`, `check_battery`, etc).
- `__init__.py`: exporta `MCPDiagnosisService` para uso pela camada de models.

## Como Adicionar um Novo Metodo de Integracao

1. Defina o metodo no service com assinatura explicita.
2. Monte o payload limpo com `_clean_payload`.
3. Chame `_post("nome_da_tool", payload)`.
4. Retorne formatado via `_format_response(response, as_toon)`.

### Template (Blank Example)

Copie e cole o codigo abaixo para adicionar uma nova chamada externa:

```python
from typing import Any, List, Optional


class MCPDiagnosisService:
    # ... codigo existente

    def check_temperature(
        self,
        pic_id_list: Optional[List[int]] = None,
        reference_date: Any = None,
        as_toon: bool = True,
    ):
        payload = {
            "pic_id_list": pic_id_list,
            "reference_date": self._normalize_reference_date(reference_date),
        }
        response = self._post("check_temperature", payload)
        return self._format_response(response, as_toon)
```
