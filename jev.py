"""Minimal client for TypeSafe's Jev via OpenRouter's Decisions API."""

import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)  # .env wins over variables already in the shell

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"


def noul(instructions: str, criteria: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Yes/no question. Answer is a probability in [0, 1]."""
    q: Dict[str, Any] = {"type": "noul", "instructions": instructions}
    if criteria:
        q["criteria"] = criteria
    return q


def choice(instructions: str, options: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """Pick one of `options` (name -> optional description)."""
    return {"type": "choice", "instructions": instructions, "criteria": options}


def score(instructions: str, scale: List[str]) -> Dict[str, Any]:
    """Place the state on an ordered scale, low to high."""
    return {"type": "score", "instructions": instructions, "criteria": scale}


class Jev:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: float = 30.0):
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set (see .env.example)")
        self.model = model or os.environ.get("JEV_MODEL")
        if not self.model:
            raise RuntimeError("JEV_MODEL is not set (see .env.example)")
        self._http = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}", "X-Title": "typesafe-jev"},
        )

    def decide(self, state: Dict[str, Any], questions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Send a state + typed questions; returns the raw JSON response."""
        resp = self._http.post(
            ENDPOINT, json={"model": self.model, "state": state, "questions": questions}
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Jev":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
