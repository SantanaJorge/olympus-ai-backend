import importlib
from pathlib import Path

_models_dir = Path(__file__).parent

for _file in _models_dir.glob("*.py"):
    if _file.stem in ("__init__", "model"):
        continue

    try:
        importlib.import_module(f".{_file.stem}", package="models")
    except Exception as e:
        print(f"[models] erro ao importar {_file.stem}: {e}")
