from typing import Any, Dict, Iterator, List

from llm.adapters import BaseAdapter, register_adapter


# Google oferece um endpoint compatível com a API da OpenAI, o que
# permite reutilizar o mesmo cliente sem SDK proprietário adicional.
_GOOGLE_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


@register_adapter("google")
class GoogleAdapter(BaseAdapter):
    """
    Adapter para a API do Google (Gemini) via endpoint compatível com OpenAI.

    Usa o SDK da OpenAI apontando para o endpoint do Google, evitando
    dependência do SDK proprietário google-generativeai.
    """

    def __init__(self, model_name: str, api_key: str) -> None:
        from openai import OpenAI

        self._model = model_name
        self._client = OpenAI(
            api_key=api_key,
            base_url=_GOOGLE_OPENAI_BASE_URL,
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
