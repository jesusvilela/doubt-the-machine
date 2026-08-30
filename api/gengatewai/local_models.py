from __future__ import annotations

import ipaddress
import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

LOCAL_MODELS_MODE_ENV = "GENGATEWAI_LOCAL_MODELS"
LOCAL_MODEL_TIMEOUT_ENV = "GENGATEWAI_LOCAL_MODEL_TIMEOUT_SECONDS"
LOCAL_LMSTUDIO_BASE_URLS_ENV = "GENGATEWAI_LOCAL_LMSTUDIO_BASE_URLS"
LOCAL_OLLAMA_BASE_URLS_ENV = "GENGATEWAI_LOCAL_OLLAMA_BASE_URLS"
LAN_OLLAMA_BASE_URLS_ENV = "GENGATEWAI_LAN_OLLAMA_BASE_URLS"
LAN_OLLAMA_CIDRS_ENV = "GENGATEWAI_LAN_OLLAMA_CIDRS"
LAN_OLLAMA_SCAN_LIMIT_ENV = "GENGATEWAI_LAN_OLLAMA_SCAN_LIMIT"

LOCAL_MODEL_ID_PREFIX = "local/"
LMSTUDIO_PROVIDER = "lmstudio"
OLLAMA_PROVIDER = "ollama"
LMSTUDIO_DEFAULT_BASE_URLS = ("http://127.0.0.1:1234/v1", "http://localhost:1234/v1")
OLLAMA_DEFAULT_BASE_URLS = ("http://127.0.0.1:11434", "http://localhost:11434")
DEFAULT_TIMEOUT_SECONDS = 0.35
DEFAULT_LAN_SCAN_LIMIT = 64

LOCAL_RUNNER_SYSTEM_MESSAGE = (
    "You are local model capacity recruited by GenGatewAI for Doubt the Machine. "
    "Use DOUBT → MEASURE → TEST → REVERT → REPEAT. Separate claim, evidence, test, "
    "and rollback. Do not present model output as a truth verdict."
)


class LocalModelUnavailableError(RuntimeError):
    """Raised when a configured local model cannot be reached or used."""


def local_models_mode() -> str:
    raw = os.getenv(LOCAL_MODELS_MODE_ENV, "off").strip().lower()
    if raw in {"1", "true", "yes", "on", "auto", "localhost"}:
        return "localhost"
    if raw in {"lan", "local+lan", "localhost+lan"}:
        return "lan"
    return "off"


def _timeout() -> float:
    raw = os.getenv(LOCAL_MODEL_TIMEOUT_ENV, "").strip()
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return min(max(value, 0.05), 5.0)


def _split_urls(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip().rstrip("/") for part in value.split(",") if part.strip())


def _json_get(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise LocalModelUnavailableError(str(exc)) from exc


def _json_post(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise LocalModelUnavailableError(str(exc)) from exc


def _private_lan_cidrs() -> tuple[ipaddress.IPv4Network, ...]:
    configured = os.getenv(LAN_OLLAMA_CIDRS_ENV)
    if configured:
        networks: list[ipaddress.IPv4Network] = []
        for raw in configured.split(","):
            raw = raw.strip()
            if not raw:
                continue
            try:
                network = ipaddress.ip_network(raw, strict=False)
            except ValueError:
                continue
            if isinstance(network, ipaddress.IPv4Network) and network.is_private:
                networks.append(network)
        return tuple(networks)

    networks = set()
    try:
        addresses = socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET)
    except OSError:
        return ()
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if isinstance(ip, ipaddress.IPv4Address) and ip.is_private and not ip.is_loopback:
            networks.add(ipaddress.ip_network(f"{ip}/24", strict=False))
    return tuple(sorted(networks, key=str))


def _lan_ollama_base_urls() -> tuple[str, ...]:
    explicit = _split_urls(os.getenv(LAN_OLLAMA_BASE_URLS_ENV))
    if explicit:
        return explicit

    try:
        limit = int(os.getenv(LAN_OLLAMA_SCAN_LIMIT_ENV, str(DEFAULT_LAN_SCAN_LIMIT)))
    except ValueError:
        limit = DEFAULT_LAN_SCAN_LIMIT
    limit = min(max(limit, 0), 512)
    if limit == 0:
        return ()

    urls: list[str] = []
    for network in _private_lan_cidrs():
        for host in network.hosts():
            urls.append(f"http://{host}:11434")
            if len(urls) >= limit:
                return tuple(urls)
    return tuple(urls)


def lmstudio_base_urls(mode: str | None = None) -> tuple[str, ...]:
    mode = mode or local_models_mode()
    if mode == "off":
        return ()
    configured = _split_urls(os.getenv(LOCAL_LMSTUDIO_BASE_URLS_ENV))
    return configured or LMSTUDIO_DEFAULT_BASE_URLS


def ollama_base_urls(mode: str | None = None) -> tuple[str, ...]:
    mode = mode or local_models_mode()
    if mode == "off":
        return ()
    configured = _split_urls(os.getenv(LOCAL_OLLAMA_BASE_URLS_ENV))
    urls = list(configured or OLLAMA_DEFAULT_BASE_URLS)
    if mode == "lan":
        urls.extend(_lan_ollama_base_urls())
    return tuple(dict.fromkeys(urls))


def _local_model_id(provider: str, model_id: str) -> str:
    return f"{LOCAL_MODEL_ID_PREFIX}{provider}/{model_id}"


def _model_entry(provider: str, model_id: str, base_url: str) -> dict[str, Any]:
    return {
        "id": _local_model_id(provider, model_id),
        "object": "model",
        "created": 0,
        "owned_by": provider,
        "provider": provider,
        "local": True,
        "source_base_url": base_url,
    }


def _discover_lmstudio(timeout: float) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for base_url in lmstudio_base_urls():
        try:
            body = _json_get(f"{base_url.rstrip('/')}/models", timeout)
        except LocalModelUnavailableError:
            continue
        for item in body.get("data", []):
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("id", "")).strip()
            if model_id:
                models.append(_model_entry(LMSTUDIO_PROVIDER, model_id, base_url.rstrip("/")))
    return models


def _discover_ollama(timeout: float) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for base_url in ollama_base_urls():
        base_url = base_url.rstrip("/")
        try:
            body = _json_get(f"{base_url}/api/tags", timeout)
        except LocalModelUnavailableError:
            continue
        for item in body.get("models", []):
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("model") or item.get("name") or "").strip()
            if model_id:
                entry = _model_entry(OLLAMA_PROVIDER, model_id, base_url)
                if "size" in item:
                    entry["size"] = item["size"]
                models.append(entry)
    return models


def discover_local_models() -> dict[str, Any]:
    mode = local_models_mode()
    if mode == "off":
        return {"enabled": False, "mode": "off", "models": [], "warnings": []}

    timeout = _timeout()
    discovered = _discover_lmstudio(timeout) + _discover_ollama(timeout)
    models_by_id = {model["id"]: model for model in discovered}
    warnings = []
    if mode == "lan":
        warnings.append("LAN Ollama autodetection is enabled; keep this local or behind a trusted network boundary.")
    return {"enabled": True, "mode": mode, "models": list(models_by_id.values()), "warnings": warnings}


def public_local_model(model: dict[str, Any]) -> dict[str, Any]:
    return {
        key: model[key]
        for key in ("id", "object", "created", "owned_by", "provider", "local", "size")
        if key in model
    }


def public_local_model_discovery() -> dict[str, Any]:
    discovery = discover_local_models()
    return {
        "enabled": discovery["enabled"],
        "mode": discovery["mode"],
        "models": [public_local_model(model) for model in discovery["models"]],
        "warnings": discovery["warnings"],
    }


def resolve_local_model(model_id: str) -> dict[str, Any] | None:
    if not model_id.startswith(LOCAL_MODEL_ID_PREFIX):
        return None
    for model in discover_local_models()["models"]:
        if model["id"] == model_id:
            return model
    return None


def _provider_model_id(local_model_id: str, provider: str) -> str:
    return local_model_id.removeprefix(f"{LOCAL_MODEL_ID_PREFIX}{provider}/")


def _chat_url(model: dict[str, Any]) -> str:
    base_url = str(model["source_base_url"]).rstrip("/")
    if model["provider"] == LMSTUDIO_PROVIDER:
        return f"{base_url}/chat/completions"
    if model["provider"] == OLLAMA_PROVIDER:
        return f"{base_url}/v1/chat/completions"
    raise LocalModelUnavailableError(f"unsupported local provider: {model['provider']}")


def local_chat_payload(request_payload: dict[str, Any], local_model: dict[str, Any]) -> dict[str, Any]:
    provider = str(local_model["provider"])
    payload = {
        key: value
        for key, value in request_payload.items()
        if key
        in {
            "messages",
            "temperature",
            "top_p",
            "max_tokens",
            "max_completion_tokens",
            "user",
        }
        and value is not None
    }
    payload["model"] = _provider_model_id(str(local_model["id"]), provider)
    payload["stream"] = False
    messages = payload.get("messages", [])
    if isinstance(messages, list):
        payload["messages"] = [{"role": "system", "content": LOCAL_RUNNER_SYSTEM_MESSAGE}, *messages]
    return payload


def call_local_chat_completion(request_payload: dict[str, Any], local_model: dict[str, Any]) -> dict[str, Any]:
    return _json_post(_chat_url(local_model), local_chat_payload(request_payload, local_model), _timeout())
