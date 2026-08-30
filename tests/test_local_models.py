from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from api.gengatewai import local_models
from api.gengatewai.app import app

client = TestClient(app)


def test_local_model_discovery_is_off_by_default(monkeypatch) -> None:
    monkeypatch.delenv(local_models.LOCAL_MODELS_MODE_ENV, raising=False)

    discovery = local_models.discover_local_models()

    assert discovery == {"enabled": False, "mode": "off", "models": [], "warnings": []}


def test_local_model_discovery_finds_lmstudio_and_ollama(monkeypatch) -> None:
    monkeypatch.setenv(local_models.LOCAL_MODELS_MODE_ENV, "localhost")

    def fake_json_get(url: str, timeout: float) -> dict[str, Any]:
        if url == "http://127.0.0.1:1234/v1/models":
            return {"data": [{"id": "qwen3-local"}]}
        if url == "http://127.0.0.1:11434/api/tags":
            return {"models": [{"model": "gemma4:local", "size": 1234}]}
        raise local_models.LocalModelUnavailableError(url)

    monkeypatch.setattr(local_models, "_json_get", fake_json_get)

    discovery = local_models.discover_local_models()

    assert discovery["enabled"] is True
    assert discovery["mode"] == "localhost"
    assert {model["id"] for model in discovery["models"]} == {
        "local/lmstudio/qwen3-local",
        "local/ollama/gemma4:local",
    }


def test_local_model_api_does_not_expose_base_urls(monkeypatch) -> None:
    monkeypatch.setenv(local_models.LOCAL_MODELS_MODE_ENV, "localhost")
    monkeypatch.setattr(
        local_models,
        "_json_get",
        lambda url, timeout: {"data": [{"id": "qwen3-local"}]} if url.endswith("/v1/models") else {"models": []},
    )

    response = client.get("/v1/local-models")

    assert response.status_code == 200
    body = response.json()
    assert body["models"] == [
        {
            "id": "local/lmstudio/qwen3-local",
            "object": "model",
            "created": 0,
            "owned_by": "lmstudio",
            "provider": "lmstudio",
            "local": True,
        }
    ]
    assert "source_base_url" not in str(body)


def test_local_ollama_chat_completion_is_wrapped_by_doubt_runner(monkeypatch) -> None:
    monkeypatch.setenv(local_models.LOCAL_MODELS_MODE_ENV, "localhost")

    def fake_json_get(url: str, timeout: float) -> dict[str, Any]:
        if url == "http://127.0.0.1:1234/v1/models":
            return {"data": []}
        if url == "http://127.0.0.1:11434/api/tags":
            return {"models": [{"model": "gemma4:local"}]}
        raise local_models.LocalModelUnavailableError(url)

    def fake_json_post(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        assert url == "http://127.0.0.1:11434/v1/chat/completions"
        assert payload["model"] == "gemma4:local"
        assert payload["stream"] is False
        assert payload["messages"][0]["role"] == "system"
        assert "DOUBT → MEASURE → TEST → REVERT → REPEAT" in payload["messages"][0]["content"]
        return {
            "id": "local-response-1",
            "created": 1788048001,
            "choices": [{"message": {"content": "local model answer"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 11, "total_tokens": 18},
        }

    monkeypatch.setattr(local_models, "_json_get", fake_json_get)
    monkeypatch.setattr(local_models, "_json_post", fake_json_post)

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "local/ollama/gemma4:local",
            "messages": [{"role": "user", "content": "CLAIM: local answer is enough"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "local-response-1"
    assert body["model"] == "local/ollama/gemma4:local"
    content = body["choices"][0]["message"]["content"]
    assert "local model answer" in content
    assert "GenGatewAI runner note" in content
    assert "does not decide whether the claim is true" in content
    assert body["usage"] == {"prompt_tokens": 7, "completion_tokens": 11, "total_tokens": 18}


def test_lan_ollama_discovery_is_opt_in_and_bounded(monkeypatch) -> None:
    monkeypatch.setenv(local_models.LOCAL_MODELS_MODE_ENV, "lan")
    monkeypatch.setenv(local_models.LAN_OLLAMA_BASE_URLS_ENV, "http://192.168.1.50:11434")
    monkeypatch.setattr(
        local_models,
        "_json_get",
        lambda url, timeout: (_ for _ in ()).throw(local_models.LocalModelUnavailableError(url)),
    )

    assert "http://192.168.1.50:11434" in local_models.ollama_base_urls()
    assert "http://127.0.0.1:11434" in local_models.ollama_base_urls()
    assert local_models.discover_local_models()["warnings"] == [
        "LAN Ollama autodetection is enabled; keep this local or behind a trusted network boundary."
    ]
