"""
Módulo de agentes com auto-discovery.

Ao importar este módulo, todos os arquivos .py neste diretório são
automaticamente importados, o que dispara o auto-registro declarativo
de rotas e agentes de chat.
"""

import importlib
from pathlib import Path

# Diretório atual
agents_dir = Path(__file__).parent

# Auto-importar todos os módulos de agentes
for file in agents_dir.glob("*.py"):
    if file.stem in ("__init__", "agent"):
        continue

    try:
        importlib.import_module(f".{file.stem}", package="agents")
    except Exception as e:
        print(f"[agents] erro ao importar {file.stem}: {e}")
