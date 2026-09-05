from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate a complete response."""
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ):
        """Stream response tokens/chunks."""
        raise NotImplementedError
