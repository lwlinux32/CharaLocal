import json
import httpx
from typing import List, Dict, Any, AsyncIterator
from .base import AIProvider

class OpenAICompatibleProvider(AIProvider):
    """
    Client for any OpenAI-compatible API endpoint:
    - OpenAI (https://api.openai.com/v1)
    - Google Gemini OpenAI endpoint (https://generativelanguage.googleapis.com/v1beta/openai/)
    - Local Ollama (http://localhost:11434/v1)
    - Local LM Studio (http://localhost:1234/v1)
    - Groq, Together, OpenRouter, vLLM, etc.
    """

    def _normalize_endpoint(self, base_url: str) -> str:
        url = base_url.strip()
        if not url:
            url = "https://api.openai.com/v1"
        url = url.rstrip("/")
        # If user entered bare host:port for Ollama or LM Studio without /v1, add /v1
        if url in ("http://localhost:11434", "http://127.0.0.1:11434", "http://localhost:1234", "http://127.0.0.1:1234"):
            url = f"{url}/v1"
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"
        return url

    def _normalize_models_endpoint(self, base_url: str) -> str:
        url = base_url.strip().rstrip("/")
        if url.endswith("/chat/completions"):
            url = url[:-17].rstrip("/")
        if url in ("http://localhost:11434", "http://127.0.0.1:11434", "http://localhost:1234", "http://127.0.0.1:1234"):
            url = f"{url}/v1"
        if not url.endswith("/models"):
            url = f"{url}/models"
        return url

    async def list_models(self, config: Dict[str, Any]) -> List[str]:
        base_url = config.get("base_url", "https://api.openai.com/v1")
        api_key = config.get("api_key", "")
        headers = self._get_headers(api_key)

        models = []
        # Try standard /v1/models endpoint
        models_url = self._normalize_models_endpoint(base_url)
        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                res = await client.get(models_url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    raw_list = data.get("data", [])
                    for item in raw_list:
                        if isinstance(item, dict) and "id" in item:
                            models.append(item["id"])
                        elif isinstance(item, str):
                            models.append(item)
                    if models:
                        return models
            except Exception:
                pass

            # Try Ollama native /api/tags if port 11434 or local
            if "11434" in base_url or "ollama" in base_url.lower():
                try:
                    root_url = base_url.split("/v1")[0].rstrip("/")
                    res = await client.get(f"{root_url}/api/tags")
                    if res.status_code == 200:
                        data = res.json()
                        for m in data.get("models", []):
                            if "name" in m:
                                models.append(m["name"])
                        if models:
                            return models
                except Exception:
                    pass

        return models

    def _get_headers(self, api_key: str) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if api_key and api_key.strip():
            headers["Authorization"] = f"Bearer {api_key.strip()}"
        return headers

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> str:
        base_url = config.get("base_url", "https://api.openai.com/v1")
        api_key = config.get("api_key", "")
        model = config.get("model", "gpt-4o-mini")
        temperature = float(config.get("temperature", 0.85))
        max_tokens = int(config.get("max_tokens", 1024))

        endpoint = self._normalize_endpoint(base_url)
        headers = self._get_headers(api_key)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
            except httpx.HTTPStatusError as e:
                err_text = e.response.text
                raise RuntimeError(f"API Error ({e.response.status_code}): {err_text}")
            except Exception as e:
                raise RuntimeError(f"Connection failed to {endpoint}: {str(e)}")

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any]
    ) -> AsyncIterator[str]:
        base_url = config.get("base_url", "https://api.openai.com/v1")
        api_key = config.get("api_key", "")
        model = config.get("model", "gpt-4o-mini")
        temperature = float(config.get("temperature", 0.85))
        max_tokens = int(config.get("max_tokens", 1024))

        endpoint = self._normalize_endpoint(base_url)
        headers = self._get_headers(api_key)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                async with client.stream("POST", endpoint, json=payload, headers=headers) as response:
                    if response.status_code != 200:
                        err_body = await response.aread()
                        raise RuntimeError(f"API Error ({response.status_code}): {err_body.decode('utf-8', errors='ignore')}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                choices = chunk.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                if "API Error" in str(e):
                    raise
                raise RuntimeError(f"Streaming failed: {str(e)}")

    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        import os
        base_url = config.get("base_url", "https://api.openai.com/v1")
        api_key = config.get("api_key", "")
        model = config.get("model", "gpt-4o-mini")

        endpoint = self._normalize_endpoint(base_url)
        headers = self._get_headers(api_key)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }

        # Check if running in cloud container vs local machine
        app_url = os.environ.get("APP_URL", "")
        is_cloud_preview = bool(os.environ.get("K_SERVICE") or "run.app" in app_url)
        is_local_target = "localhost" in base_url or "127.0.0.1" in base_url or "0.0.0.0" in base_url

        # Also try to discover available models to help the user
        available_models = []
        try:
            available_models = await self.list_models(config)
        except Exception:
            pass

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": f"Successfully connected to {model} at {base_url}!",
                        "models": available_models
                    }
                elif response.status_code == 404:
                    models_str = f" Found installed models: {', '.join(available_models[:5])}" if available_models else ""
                    return {
                        "success": False,
                        "message": f"Model '{model}' not found on endpoint (404).{models_str}. Please verify the model name or run 'ollama pull {model}'.",
                        "models": available_models
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": f"Authentication required (401 Unauthorized). Please check your API key for {base_url}.",
                        "models": available_models
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Endpoint returned status {response.status_code}: {response.text[:200]}",
                        "models": available_models
                    }
            except Exception as e:
                err_str = str(e)
                diag_tips = []

                if is_local_target and is_cloud_preview:
                    return {
                        "success": False,
                        "message": (
                            "⚠️ Cloud Sandbox Notice: You are testing a 'localhost' URL from the Cloud Web Preview! "
                            "In the cloud, 'localhost' refers to the remote server container, not your home computer.\n\n"
                            "To connect your local Ollama/LM Studio model:\n"
                            "1. Run this app directly on your computer: Download the code and run 'python run.py'. Then localhost:11434 will connect straight to your machine!\n"
                            "2. Or expose your local model using a free tunnel: Run 'ngrok http 11434' and paste the public https://... URL into Base URL.\n"
                            "3. Or select Google Gemini or OpenAI in Settings while using this cloud preview."
                        ),
                        "is_cloud_notice": True,
                        "models": []
                    }

                if "Connection refused" in err_str or "ConnectError" in err_str:
                    if "11434" in base_url or "ollama" in base_url.lower():
                        return {
                            "success": False,
                            "message": (
                                "Connection refused to Ollama (port 11434).\n"
                                "1. Make sure Ollama is running: 'ollama serve' or 'ollama run <model>'.\n"
                                "2. Allow CORS: set OLLAMA_ORIGINS=\"*\" before running ollama serve.\n"
                                "3. Base URL should be: http://localhost:11434/v1"
                            ),
                            "models": []
                        }
                    elif "1234" in base_url or "lmstudio" in base_url.lower():
                        return {
                            "success": False,
                            "message": (
                                "Connection refused to LM Studio (port 1234).\n"
                                "1. Open LM Studio and go to the 'Local Server' (double arrow) tab.\n"
                                "2. Click the green 'Start Server' button.\n"
                                "3. Ensure 'Enable CORS' is checked in server settings.\n"
                                "4. Base URL should be: http://localhost:1234/v1"
                            ),
                            "models": []
                        }

                return {
                    "success": False,
                    "message": f"Could not reach endpoint {endpoint}: {err_str}",
                    "models": []
                }
