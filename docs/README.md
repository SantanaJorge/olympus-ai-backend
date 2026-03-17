# Camada de Docs

Esta pasta guarda artefatos de documentacao e apoio a testes manuais da API.

## Funcionamento

Os arquivos desta camada servem como referencia para integracao externa (clientes HTTP, Postman e exemplos de payload).
A colecao atual permite testar endpoints de diagnostico, health-check e filtros de consulta.

### Principais Componentes

- `postman.json`: colecao Postman com requisicoes de exemplo para validar o backend.

## Como Adicionar um Novo Artefato de Documentacao

1. Crie o arquivo em `docs/` com nome descritivo.
2. Explique objetivo, pre-condicoes e exemplos de request/response.
3. Quando for colecao de API, inclua variaveis de ambiente e headers obrigatorios.

### Template (Blank Example)

Copie e cole o modelo abaixo para criar um novo documento de endpoint:

```md
# Endpoint: nome_do_endpoint

## Objetivo
Descreva o que este endpoint resolve.

## Requisicao
- Metodo: POST
- URL: /v1/exemplo
- Headers:
  - Authorization: Bearer <API_KEY>
  - Content-Type: application/json

## Body de Exemplo
~~~json
{
  "campo": "valor"
}
~~~

## Resposta de Exemplo
~~~json
{
  "success": true,
  "result": {}
}
~~~
```
