"""
Adapters de provider para o PassthroughProxy.

Cada adapter isola a interface específica de um provider (OpenAI, Anthropic, Google),
expondo uma API unificada: chat() e chat_stream().

Para adicionar um novo provider:
    1. Crie um arquivo neste diretório com uma classe que herda de BaseAdapter.
    2. Decore-a com @register_adapter("nome_do_provider").
    3. Declare o provider nas classes BaseLLM correspondentes em llm/.
"""

import importlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Type


# ---------------------------------------------------------------------------
# Contrato base
# ---------------------------------------------------------------------------

class BaseAdapter(ABC):
    """Interface unificada para acesso direto a providers de LLM."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **params: Any) -> str:
        """Envia uma requisição não-streaming e retorna o texto da resposta."""
        ...

    @abstractmethod
    def chat_stream(
        self, messages: List[Dict[str, Any]], **params: Any
    ) -> Iterator[str]:
        """Envia uma requisição streaming e retorna um iterator de chunks de texto."""
        ...


# ---------------------------------------------------------------------------
# Registry + decorator de registro
# ---------------------------------------------------------------------------

ADAPTER_REGISTRY: Dict[str, Type[BaseAdapter]] = {}


def register_adapter(provider: str):
    """Decorator que registra uma classe de adapter pelo nome do provider."""
    def decorator(cls: Type[BaseAdapter]) -> Type[BaseAdapter]:
        ADAPTER_REGISTRY[provider] = cls
        return cls
    return decorator


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_adapter(model_name: str, provider: str, api_key: str) -> BaseAdapter:
    """
    Instancia o adapter correto para um dado provider.

    Args:
        model_name: Nome do modelo (ex: "gpt-5.4", "claude-3-7-sonnet-20250219")
        provider:   Nome do provider (ex: "openai", "anthropic", "google")
        api_key:    Chave de API já resolvida via os.getenv()
    """
    adapter_cls = ADAPTER_REGISTRY.get(provider)
    if adapter_cls is None:
        raise ValueError(
            f"Nenhum adapter registrado para provider '{provider}'. "
            f"Disponíveis: {list(ADAPTER_REGISTRY.keys())}"
        )
    return adapter_cls(model_name=model_name, api_key=api_key)


# ---------------------------------------------------------------------------
# Auto-discovery: importa todos os adapters para disparar @register_adapter
# ---------------------------------------------------------------------------

_adapters_dir = Path(__file__).parent

for _file in _adapters_dir.glob("*.py"):
    if _file.stem == "__init__":
        continue
    try:
        importlib.import_module(f".{_file.stem}", package="llm.adapters")
    except Exception as _e:
        print(f"[llm.adapters] erro ao importar {_file.stem}: {_e}")


__all__ = ["BaseAdapter", "ADAPTER_REGISTRY", "register_adapter", "build_adapter"]
