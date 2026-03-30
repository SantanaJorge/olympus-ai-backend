from typing import Any, Dict, Iterator, List

from llm.adapters import BaseAdapter, register_adapter


@register_adapter("openai")
class OpenAIAdapter(BaseAdapter):
    """Adapter para a API da OpenAI (e endpoints compatíveis)."""

    def __init__(self, model_name: str, api_key: str, base_url: str = None) -> None:
        from openai import OpenAI

        self._model = model_name
        self._client = OpenAI(
            api_key=api_key,
            **({"base_url": base_url} if base_url else {}),
        )

    def chat(self, messages: List[Dict[str, Any]], **params: Any) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            **params,
        )
        return response.choices[0].message.content or ""

    def chat_stream(self, messages: List[Dict[str, Any]], **params: Any) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
            **params,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
