import httpx

from app.config import get_settings
from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        payload = {
    "model": self.model,
    "stream": False,
    "options": {
        "temperature": 0.2,
        "num_predict": 256,
    },
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        return data["message"]["content"]

    async def stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ):

        payload = {
    "model": self.model,
    "stream": True,
    "options": {
        "temperature": 0.2,
        "num_predict": 96,
        "num_ctx": 4096,
    },
    
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    yield line
