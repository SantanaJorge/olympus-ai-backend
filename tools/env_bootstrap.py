"""Normalize environment variables often injected from Secret Manager (strip whitespace)."""

import os
from typing import Literal

# Cloud Run maps secrets to these env vars; trailing newlines break OpenAI and other clients.
_SECRET_ENV_NAMES = (
    "OPENAI_API_KEY",
    "TAVILY_API_KEY",
    "MCP_DIAGNOSIS_AUTH_TOKEN",
    "AUTH_API_KEY",
    "RAGIE_API_KEY",
)

Environment = Literal["local", "accept", "production"]


def get_environment() -> Environment:
    """Retorna o ambiente atual: 'local', 'accept' ou 'production'.

    - local:      sem var ENVIRONMENT (roda via .env / terminal)
    - accept:     Cloud Run em zeus-accept  (ENVIRONMENT=accept)
    - production: Cloud Run em zeus-prod    (ENVIRONMENT=production)
    """
    value = os.environ.get("ENVIRONMENT", "").strip().lower()
    if value == "production":
        return "production"
    if value == "accept":
        return "accept"
    return "local"


def strip_secret_env_vars() -> None:
    for name in _SECRET_ENV_NAMES:
        value = os.environ.get(name)
        if value is not None:
            os.environ[name] = value.strip()
