from typing import Any, Dict, List, Optional
import logging
from .base_agent import BaseAgent
import os

logger = logging.getLogger(__name__)


class LLMIntegrationAgent(BaseAgent):
    """Agent for integrating with LLM providers (OpenAI, Claude)"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        super().__init__(
            name="LLMIntegrationAgent",
            description=f"Integrates with {provider} for AI-powered tasks",
        )
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.conversation_history = []
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        try:
            if self.provider == "openai":
                try:
                    import openai
                    if self.api_key:
                        openai.api_key = self.api_key
                    self.client = openai
                    logger.info("OpenAI client initialized")
                except ImportError:
                    logger.warning("openai package not installed")

            elif self.provider == "anthropic" or self.provider == "claude":
                try:
                    import anthropic
                    if self.api_key:
                        self.client = anthropic.Anthropic(api_key=self.api_key)
                    logger.info("Anthropic client initialized")
                except ImportError:
                    logger.warning("anthropic package not installed")

        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {str(e)}")

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute an LLM-powered task"""
        logger.info(f"Executing LLM task: {task}")

        try:
            prompt = kwargs.get("prompt", task)
            result = self._generate_response(prompt, **kwargs)

            self.conversation_history.append({
                "prompt": prompt,
                "response": result,
            })

            return {
                "status": "success",
                "task": task,
                "response": result,
                "provider": self.provider,
                "history_length": len(self.conversation_history),
            }

        except Exception as e:
            logger.error(f"LLM task failed: {str(e)}")
            return {"status": "failed", "task": task, "error": str(e)}

    def _generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        if not self.client:
            return "LLM client not initialized. Please install required packages and set API key."

        model = kwargs.get("model")
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)

        try:
            if self.provider == "openai":
                model = model or "gpt-3.5-turbo"
                response = self.client.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content

            elif self.provider in ["anthropic", "claude"]:
                model = model or "claude-3-sonnet-20240229"
                message = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"

    def chat(self, message: str, **kwargs) -> str:
        """Simple chat interface"""
        result = self.execute("chat", prompt=message, **kwargs)
        return result.get("response", "No response")

    def summarize(self, text: str, **kwargs) -> str:
        """Summarize text"""
        prompt = f"Please summarize the following text:\n\n{text}"
        result = self.execute("summarize", prompt=prompt, **kwargs)
        return result.get("response", "No response")

    def analyze_sentiment(self, text: str, **kwargs) -> str:
        """Analyze sentiment of text"""
        prompt = f"Analyze the sentiment of the following text and provide a brief analysis:\n\n{text}"
        result = self.execute("analyze_sentiment", prompt=prompt, **kwargs)
        return result.get("response", "No response")

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
