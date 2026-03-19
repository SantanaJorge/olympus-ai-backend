import datetime as dt
import json
import os
import socket
from typing import Any, Dict, List, Optional
from urllib import error, request

import pandas as pd

from tools.toon import encode_toon

_DEFAULT_BASE_URL = (
    "https://mcp-diagnosis-server-ukneqvhpoa-uc.a.run.app"
)
_DEFAULT_AUTH_TOKEN = "sk_gP0eOKRyx1hscEzKRQ8D3vf7Bf249ooSbs18DqL2lTw"
_DEFAULT_TIMEOUT_SECONDS = 300


def _read_timeout_seconds() -> Optional[float]:
    raw_timeout = os.getenv("MCP_DIAGNOSIS_TIMEOUT_SECONDS", "").strip()
    if not raw_timeout:
        return _DEFAULT_TIMEOUT_SECONDS

    timeout_lower = raw_timeout.lower()
    if timeout_lower in {"0", "none", "off", "false", "no", "inf", "infinite"}:
        return None

    try:
        parsed = float(raw_timeout)
        if parsed <= 0:
            return None
        return parsed
    except ValueError:
        return _DEFAULT_TIMEOUT_SECONDS


class MCPDiagnosisService:
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("MCP_DIAGNOSIS_BASE_URL", _DEFAULT_BASE_URL)
        ).rstrip("/")

        self.auth_token = (
            auth_token
            or os.getenv("MCP_DIAGNOSIS_AUTH_TOKEN", _DEFAULT_AUTH_TOKEN)
        ).strip()

        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else _read_timeout_seconds()

    @staticmethod
    def _normalize_reference_date(reference_date: Any) -> Optional[str]:
        if reference_date is None:
            return None

        if isinstance(reference_date, str):
            value = reference_date.strip()
            if not value:
                return None

            try:
                parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=dt.timezone.utc)
                return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            except ValueError:
                return value

        if isinstance(reference_date, dt.date) and not isinstance(reference_date, dt.datetime):
            reference_date = dt.datetime.combine(reference_date, dt.time.min)

        if isinstance(reference_date, dt.datetime):
            parsed_dt = reference_date
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=dt.timezone.utc)
            return parsed_dt.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        return str(reference_date)

    @staticmethod
    def _clean_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}

        for key, value in payload.items():
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            if isinstance(value, tuple):
                value = list(value)
            elif isinstance(value, set):
                value = list(value)

            if isinstance(value, (list, dict)) and len(value) == 0:
                continue

            cleaned[key] = value

        return cleaned

    def _build_headers(self) -> Dict[str, str]:
        auth_value = self.auth_token
        if not auth_value.lower().startswith("bearer "):
            auth_value = f"Bearer {auth_value}"

        return {
            "Authorization": auth_value,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def _format_response(response: Dict[str, Any], as_toon: bool):
        if as_toon:
            return encode_toon(pd.DataFrame([response]), name="mcp_response")
        return response

    def _post(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_payload = self._clean_payload(payload)
        if not cleaned_payload:
            raise ValueError("Pelo menos um parametro deve ser informado no body da requisicao.")

        body = json.dumps(cleaned_payload).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}/mcp/tools/{tool_name}",
            data=body,
            headers=self._build_headers(),
            method="POST",
        )

        try:
            if self.timeout_seconds is None:
                with request.urlopen(req) as response:
                    raw_response = response.read().decode("utf-8")
            else:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    raw_response = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Erro HTTP {exc.code} ao chamar {tool_name}: {error_body or exc.reason}"
            ) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise RuntimeError(
                "Timeout de leitura ao chamar "
                f"{tool_name}. Ajuste MCP_DIAGNOSIS_TIMEOUT_SECONDS "
                "(ex: 300) ou use 0 para remover limite."
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"Falha de conexao ao chamar {tool_name}: {exc.reason}"
            ) from exc

        try:
            parsed = json.loads(raw_response) if raw_response else {}
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Resposta invalida (nao JSON) ao chamar {tool_name}."
            ) from exc

        if not isinstance(parsed, dict):
            raise RuntimeError(
                f"Resposta inesperada ao chamar {tool_name}: tipo {type(parsed).__name__}."
            )

        if parsed.get("success") is False:
            err_msg = parsed.get("error") or parsed.get("message") or "Erro desconhecido"
            raise RuntimeError(f"Erro retornado por {tool_name}: {err_msg}")

        return parsed

    def get_park_info(
        self,
        reference_date: Any = None,
        window_days: Optional[int] = None,
        status_list: Optional[List[str]] = None,
        model_list: Optional[List[str]] = None,
        as_toon: bool = True,
    ):
        payload = {
            "reference_date": self._normalize_reference_date(reference_date),
            "window_days": window_days,
            "status_list": status_list,
            "model_list": model_list,
        }
        response = self._post("get_park_info", payload)
        return self._format_response(response, as_toon)

    def get_pics(
        self,
        client_id_list: Optional[List[int]] = None,
        pic_id_list: Optional[List[int]] = None,
        hardware_id_list: Optional[List[int]] = None,
        status_list: Optional[List[str]] = None,
        model_list: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        reference_date: Any = None,
        visible: Optional[bool] = None,
        as_toon: bool = True,
    ):
        payload = {
            "client_id_list": client_id_list,
            "pic_id_list": pic_id_list,
            "hardware_id_list": hardware_id_list,
            "status_list": status_list,
            "model_list": model_list,
            "columns": columns,
            "limit": limit,
            "reference_date": self._normalize_reference_date(reference_date),
            "visible": visible,
        }
        response = self._post("get_pics", payload)
        return self._format_response(response, as_toon)

    def check_lora_network(
        self,
        pic_id_list: Optional[List[int]] = None,
        client_id_list: Optional[List[int]] = None,
        hardware_id_list: Optional[List[int]] = None,
        reference_date: Any = None,
        as_toon: bool = True,
    ):
        payload = {
            "pic_id_list": pic_id_list,
            "client_id_list": client_id_list,
            "hardware_id_list": hardware_id_list,
            "reference_date": self._normalize_reference_date(reference_date),
        }
        response = self._post("check_lora_network", payload)
        return self._format_response(response, as_toon)

    def check_wifi_network(
        self,
        pic_id_list: Optional[List[int]] = None,
        client_id_list: Optional[List[int]] = None,
        hardware_id_list: Optional[List[int]] = None,
        reference_date: Any = None,
        as_toon: bool = True,
    ):
        payload = {
            "pic_id_list": pic_id_list,
            "client_id_list": client_id_list,
            "hardware_id_list": hardware_id_list,
            "reference_date": self._normalize_reference_date(reference_date),
        }
        response = self._post("check_wifi_network", payload)
        return self._format_response(response, as_toon)

    def check_battery(
        self,
        pic_id_list: Optional[List[int]] = None,
        client_id_list: Optional[List[int]] = None,
        hardware_id_list: Optional[List[int]] = None,
        reference_date: Any = None,
        as_toon: bool = True,
    ):
        payload = {
            "pic_id_list": pic_id_list,
            "client_id_list": client_id_list,
            "hardware_id_list": hardware_id_list,
            "reference_date": self._normalize_reference_date(reference_date),
        }
        response = self._post("check_battery", payload)
        return self._format_response(response, as_toon)

    def check_solar_panel(
        self,
        pic_id_list: Optional[List[int]] = None,
        client_id_list: Optional[List[int]] = None,
        hardware_id_list: Optional[List[int]] = None,
        reference_date: Any = None,
        as_toon: bool = True,
    ):
        payload = {
            "pic_id_list": pic_id_list,
            "client_id_list": client_id_list,
            "hardware_id_list": hardware_id_list,
            "reference_date": self._normalize_reference_date(reference_date),
        }
        response = self._post("check_solar_panel", payload)
        return self._format_response(response, as_toon)

    # Compatibilidade com chamadas legadas usadas no DiagnosticAgent anterior.
    def check_lora_network_status(self, **kwargs):
        return self.check_lora_network(**kwargs)

    def check_wifi_network_status(self, **kwargs):
        return self.check_wifi_network(**kwargs)

    def check_battery_status(self, **kwargs):
        return self.check_battery(**kwargs)

    def check_solar_panel_status(self, **kwargs):
        return self.check_solar_panel(**kwargs)
