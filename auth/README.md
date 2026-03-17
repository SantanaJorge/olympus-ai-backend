# Camada de Auth (Autenticacao)

Esta camada centraliza autenticacao por chave de API e persistencia das credenciais em SQLite.

## Funcionamento

Toda validacao de acesso HTTP passa por esta camada via `validate_api_key`, usada no `before_request` do servidor.
As chaves sao armazenadas com hash SHA-256 e so o valor bruto e exibido no momento da criacao.

### Principais Componentes

- `api_keys.py`: inicializacao do banco, criacao/listagem/remocao e validacao de chaves.
- `manage_keys.py`: CLI para operacoes administrativas (`create`, `list`, `delete`, `delete-all`).
- `auth.db`: banco SQLite de autenticacao (gerado localmente).
- `auth.db.bak`: backup opcional gerado por scripts de desinstalacao.

## Como Gerenciar Chaves

1. Crie uma chave para um cliente.
2. Liste as chaves para auditoria.
3. Revogue por ID quando necessario.

Exemplos:

```bash
# Criar
python auth/manage_keys.py create "Cliente X"

# Criar com validade
python auth/manage_keys.py create "Cliente X" "2026-12-31"

# Listar
python auth/manage_keys.py list

# Deletar por ID
python auth/manage_keys.py delete 3
```

### Template (Blank Example)

Copie e cole o codigo abaixo para criar uma validacao adicional de header/token:

```python
from typing import Optional

from auth.api_keys import validate_api_key


def validar_bearer(header_value: Optional[str]) -> bool:
    if not header_value:
        return False

    if not header_value.startswith("Bearer "):
        return False

    raw_key = header_value.split(" ", 1)[1].strip()
    return validate_api_key(raw_key)
```
