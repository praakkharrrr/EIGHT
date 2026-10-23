import time
import json
import re
from typing import Optional, Dict, Any, Tuple, List
from src.config import Config

class GemmaClient:
    """
    Client for interacting with Google GenAI / Gemini API.
    Provides real API execution with model discovery, auto-retry on 500 errors,
    error containment, and realistic mock mode.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        force_mock: bool = False
    ):
        self.api_key = Config.get_api_key(api_key)
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.force_mock = force_mock
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes the Google GenAI Client if credentials are available."""
        if self.api_key and not self.force_mock:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def is_mock_mode(self) -> bool:
        """Returns True if client is operating in mock mode."""
        return self.force_mock or self._client is None

    def list_available_models(self) -> List[str]:
        """Queries the Gemini API for all available models on this API key, prioritizing Gemma 4."""
        if self.is_mock_mode:
            return list(Config.SUPPORTED_MODELS)

        try:
            discovered = []
            for m in self._client.models.list():
                name = getattr(m, "name", "")
                if name.startswith("models/"):
                    name = name[len("models/"):]
                
                actions = getattr(m, "supported_generation_methods", []) or []
                if not actions or "generateContent" in actions:
                    discovered.append(name)

            if discovered:
                priority = [
                    "gemma-4-26b-a4b-it",
                    "gemma-4-31b-it",
                    "gemini-2.5-flash",
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "gemma-2-27b-it",
                ]
                sorted_models = []
                for p in priority:
                    if p in discovered and p not in sorted_models:
                        sorted_models.append(p)
                for d in discovered:
                    if d not in sorted_models:
                        sorted_models.append(d)
                return sorted_models
        except Exception:
            pass

        return list(Config.SUPPORTED_MODELS)

    def test_connectivity(self) -> Tuple[bool, str]:
        """
        Runs a minimal ping request to verify model connectivity.
        Handles Google server 500 INTERNAL errors gracefully with retry.
        """
        if self.is_mock_mode:
            return False, "Simulation mode active. Turn off 'Use Offline Simulator' to test live API."

        # Try up to 2 times for transient 500 errors
        last_error = ""
        for attempt in range(2):
            try:
                start_time = time.time()
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents="Reply with one word: PONG",
                )
                elapsed = time.time() - start_time
                reply_text = getattr(response, "text", "").strip()
                return True, f"Connected to {self.model_name} successfully ({elapsed:.2f}s). Reply: '{reply_text[:20]}'"
            except Exception as e:
                last_error = str(e)
                if "500" in last_error or "INTERNAL" in last_error:
                    time.sleep(1.0)
                    continue
                break

        # If failed after retry
        if "500" in last_error or "INTERNAL" in last_error:
            return False, f"⚠️ Google server error (500 INTERNAL) on '{self.model_name}'. Google's preview endpoint is temporarily overloaded. Please switch to 'gemini-2.5-flash' in the dropdown for instant live responses, or use the Simulator."
        elif "404" in last_error or "NOT_FOUND" in last_error:
            return False, f"⚠️ Model '{self.model_name}' was not found. Please select an active model like 'gemini-2.5-flash' or 'gemma-4-26b-a4b-it' from the dropdown."
        elif "400" in last_error or "API_KEY_INVALID" in last_error:
            return False, "❌ Invalid API Key. Please verify your Gemini API key in Google AI Studio."
        elif "RESOURCE_EXHAUSTED" in last_error or "429" in last_error:
            return False, "⏳ Rate limit exceeded on this key. Please wait a minute or use the Simulator."

        return False, f"Connection failed for {self.model_name}: {last_error[:120]}"

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generates content from the model or mock provider with retry on transient server errors.
        """
        temp = temperature if temperature is not None else Config.TEMPERATURE
        max_tokens = max_output_tokens or Config.MAX_OUTPUT_TOKENS

        if self.is_mock_mode:
            # Super fast simulation (0.05s) so evaluations complete in seconds
            time.sleep(0.05)
            mock_text = self._generate_mock_response(prompt, system_instruction)
            return {
                "text": mock_text,
                "latency_seconds": 0.05,
                "tokens_used": len(mock_text.split()) * 2,
                "error": None,
                "is_mock": True
            }

        start_time = time.time()
        last_exception = None

        # Retry up to 2 times on 500 INTERNAL or rate limit
        for attempt in range(2):
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    temperature=temp,
                    max_output_tokens=max_tokens,
                    system_instruction=system_instruction
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                latency = time.time() - start_time
                text = getattr(response, "text", "") or ""
                
                tokens = 0
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    tokens = getattr(response.usage_metadata, "total_token_count", 0) or 0
                if tokens == 0:
                    tokens = len(text.split()) * 2

                return {
                    "text": text,
                    "latency_seconds": round(latency, 3),
                    "tokens_used": tokens,
                    "error": None,
                    "is_mock": False
                }
            except Exception as e:
                last_exception = e
                err_str = str(e)
                if ("500" in err_str or "INTERNAL" in err_str or "429" in err_str) and attempt == 0:
                    time.sleep(1.2)
                    continue
                break

        latency = time.time() - start_time
        err_msg = str(last_exception)
        if "500" in err_msg or "INTERNAL" in err_msg:
            err_msg = f"Google Server 500 INTERNAL on '{self.model_name}'. Switch to 'gemini-2.5-flash' for instant responses."
        elif "404" in err_msg:
            err_msg = f"Model '{self.model_name}' not found (404). Please switch to 'gemini-2.5-flash'."

        return {
            "text": "",
            "latency_seconds": round(latency, 3),
            "tokens_used": 0,
            "error": err_msg,
            "is_mock": False
        }

    def _generate_mock_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Simulated response fallback."""
        sys_str = system_instruction or ""
        
        if "evaluator" in sys_str.lower() or ("compare" in prompt.lower() and "agent a" in prompt.lower()):
            return json.dumps({
                "selected_agent": "Agent B",
                "rationale": "Agent B explicitly accounts for edge cases and order preservation, whereas Agent A uses a naive approach.",
                "identified_disagreements": [
                    "Handling of duplicates and insertion order",
                    "Treatment of empty and single-element inputs"
                ],
                "confidence_score": 0.92,
                "potential_failure_modes": [
                    "Agent A loses item sequence in list operations."
                ]
            }, indent=2)

        if "TASK-01" in prompt:
            if "baseline" in sys_str.lower():
                return "```python\ndef stable_dedup(items):\n    # Naive set conversion\n    return list(set(items))\n```\n\nExplanation: Converted the items to a set to remove duplicates."
            elif "agent b" in sys_str.lower() or "adversarial" in sys_str.lower():
                return "```python\ndef stable_dedup(items):\n    seen = set()\n    result = []\n    for x in items:\n        if x not in seen:\n            seen.add(x)\n            result.append(x)\n    return result\n```\n\nExplanation: Uses set for O(1) lookup while preserving insertion order."
            else:
                return "```python\ndef stable_dedup(items):\n    return list(dict.fromkeys(items))\n```\n\nExplanation: In modern Python, dict keys preserve insertion order."

        return "```python\ndef solution(*args, **kwargs):\n    return []\n```\n\nExplanation: Default candidate solution."
