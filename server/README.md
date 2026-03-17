# Camada de Server

Esta camada expoe a API HTTP, aplica autenticacao e entrega respostas no contrato OpenAI-compatible.

## Funcionamento

A classe `Server` (singleton) inicializa o Flask, registra rotas padrao e recebe o registro declarativo dos agentes.
Ela resolve o modelo solicitado, executa chat normal ou stream SSE e monta payload com `usage` e `thought`.

### Principais Componentes

- `server.py`: singleton Flask, autenticacao Bearer, endpoints `/models`, `/chat/completions`, `/health` e stream SSE.
- `exceptions.py`: excecoes de dominio com mapeamento de status HTTP.

## Endpoints Expostos

- `GET /health`
- `GET /models`
- `GET /v1/models`
- `POST /chat/completions`
- `POST /v1/chat/completions`

## Como Estender o Server

1. Mantenha o contrato OpenAI nas rotas de chat.
2. Trate erros com payload padronizado.
3. Valide autenticacao em `before_request`.
4. Se adicionar rota publica, inclua excecao explicita no gate de auth.

### Template (Blank Example)

Copie e cole o codigo abaixo para adicionar uma rota publica simples no servidor:

```python
from flask import jsonify


# Dentro de Server._setup_default_routes
@self.app.route("/version", methods=["GET"])
def version_info():
    return jsonify(
        {
            "service": "zeus-ai-agents",
            "version": "1.0.0",
        }
    )
```
