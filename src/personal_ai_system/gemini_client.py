"""Gemini API client for LLM interactions."""

from typing import Any

import google.generativeai as genai

from personal_ai_system.config import GeminiConfig


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, config: GeminiConfig):
        """Initialize the Gemini client.

        Args:
            config: Gemini configuration
        """
        self.config = config
        self.api_key = config.api_key
        self.model_name = config.model_name

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_text(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Gemini.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 to 1.0), uses config default if None
            max_tokens: Maximum tokens to generate, uses config default if None
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        generation_config = {
            "temperature": temperature,
            **({"max_output_tokens": max_tokens} if max_tokens else {}),
            **kwargs,
        }

        response = self.model.generate_content(prompt, generation_config=generation_config)
        return response.text

    def generate_structured_output(self, prompt: str, system_instruction: str | None = None) -> str:
        """Generate structured output (like JSON) from Gemini.

        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction for the model

        Returns:
            Generated structured response
        """
        if system_instruction:
            model_with_instruction = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction
            )
            response = model_with_instruction.generate_content(prompt)
        else:
            response = self.model.generate_content(prompt)

        return response.text
