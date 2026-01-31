"""
OpenRouter API Client for MKTG Skills
Unified interface for multiple LLM providers via OpenRouter
"""

import json
import httpx
from typing import Optional, Literal
from dataclasses import dataclass

from config import config


@dataclass
class LLMResponse:
    """Structured response from LLM."""
    content: str
    model: str
    usage: dict
    cost: float = 0.0


class OpenRouterClient:
    """Client for OpenRouter API."""

    def __init__(self):
        self.config = config.openrouter
        self._validate()

    def _validate(self):
        if not self.config.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured. Add it to .env file.")

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.referer,
            "X-Title": self.config.title,
        }

    def complete(
        self,
        prompt: str,
        model: Literal["fast", "balanced", "deep", "cheap"] = "balanced",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Send completion request to OpenRouter.

        Args:
            prompt: User prompt
            model: Model tier (fast/balanced/deep/cheap)
            max_tokens: Max response tokens
            temperature: Creativity (0-1)
            system_prompt: Optional system message

        Returns:
            LLMResponse with content and metadata
        """
        model_id = self.config.models.get(model, model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens_default,
            "temperature": temperature,
        }

        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.post(
                f"{self.config.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", model_id),
            usage=data.get("usage", {}),
        )

    def complete_json(
        self,
        prompt: str,
        model: Literal["fast", "balanced", "deep", "cheap"] = "fast",
        **kwargs
    ) -> dict | list:
        """
        Get JSON response from LLM.
        Handles markdown code blocks and parsing.
        """
        response = self.complete(prompt, model=model, **kwargs)
        content = response.content.strip()

        # Handle markdown code blocks
        if "```" in content:
            # Extract content between first ``` and last ```
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
                # Remove language identifier (json, etc.)
                if content.startswith(("json", "JSON")):
                    content = content[4:].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try to find JSON in content
            for start_char, end_char in [("[", "]"), ("{", "}")]:
                start = content.find(start_char)
                end = content.rfind(end_char)
                if start != -1 and end != -1:
                    try:
                        return json.loads(content[start:end+1])
                    except json.JSONDecodeError:
                        continue
            raise ValueError(f"Failed to parse JSON from response: {content[:200]}") from e


# Singleton instance
client = OpenRouterClient()


# Convenience functions
def complete(prompt: str, **kwargs) -> str:
    """Quick completion, returns content string."""
    return client.complete(prompt, **kwargs).content


def complete_json(prompt: str, **kwargs) -> dict | list:
    """Quick JSON completion."""
    return client.complete_json(prompt, **kwargs)
