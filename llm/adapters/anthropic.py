from typing import Any, Dict, Iterator, List, Tuple

from llm.adapters import BaseAdapter, register_adapter


# Parâmetros suportados pela API da Anthropic
# (frequency_penalty, presence_penalty, logprobs, n, user não existem lá)
_SUPPORTED_PARAMS = frozenset({
    "temperature",
    "top_p",
    "top_k",
    "max_tokens",
    "stop_sequences",
})


@register_adapter("anthropic")
class AnthropicAdapter(BaseAdapter):
    """
    Adapter para a API da Anthropic (Claude).

    Diferenças chave em relação à OpenAI:
    - System message é um parâmetro separado (system=), não fica em messages[].
    - max_tokens é obrigatório (usamos DEFAULT_MAX_TOKENS se não informado).
    - Parâmetros como frequency_penalty, presence_penalty não são suportados.
    - Streaming via context manager: with client.messages.stream() as s.
    """

    DEFAULT_MAX_TOKENS = 8096

    def __init__(self, model_name: str, api_key: str) -> None:
        import anthropic

        self._model = model_name
        self._client = anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def _split_messages(
        messages: List[Dict[str, Any]],
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Extrai a system message da lista, retornando (system, resto)."""
        system = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                system = content if isinstance(content, str) else str(content)
            else:
                user_messages.append(msg)
        return system, user_messages

    @staticmethod
    def _filter_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove parâmetros não suportados pela API da Anthropic."""
        return {k: v for k, v in params.items() if k in _SUPPORTED_PARAMS}

    def _build_kwargs(
        self,
        messages: List[Dict[str, Any]],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        system, user_messages = self._split_messages(messages)
        filtered = self._filter_params(params)
        filtered.setdefault("max_tokens", self.DEFAULT_MAX_TOKENS)

        kwargs: Dict[str, Any] = {
            "model": self._model,
            "messages": user_messages,
            **filtered,
        }
        if system:
            kwargs["system"] = system
        return kwargs

    def chat(self, messages: List[Dict[str, Any]], **params: Any) -> str:
        kwargs = self._build_kwargs(messages, params)
        response = self._client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""

    def chat_stream(self, messages: List[Dict[str, Any]], **params: Any) -> Iterator[str]:
        kwargs = self._build_kwargs(messages, params)
        with self._client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text
