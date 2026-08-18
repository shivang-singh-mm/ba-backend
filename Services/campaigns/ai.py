"""
Campaigns AI Module
--------------------
Handles all AI interactions for campaign creation via OpenRouter.

Flow:
  1. User sends a free-text description of what they want.
  2. AI checks if enough info exists to populate the campaign.
  3. If not, AI replies with follow-up questions.
  4. Once sufficient, AI calls the `populate_campaign` tool with all fields.
  5. Caller (routes.py) detects the tool call and writes to DB via crud.py.
"""

import json
import os

import requests

from Utils.logger import logger

# ── OpenRouter config (read from Flask app config in routes, passed in here) ──

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Tool definition for OpenRouter tool calling ───────────────────────────────

_POPULATE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "populate_campaign",
        "description": (
            "Call this when you have gathered enough information from the user "
            "to fully populate the campaign. Provide every field you know; "
            "leave optional fields as null if the user did not specify them."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                # Campaign table fields
                "description": {
                    "type": "string",
                    "description": "A rich description of the campaign.",
                },
                "total_hours": {
                    "type": "number",
                    "description": "Total expected hours for the campaign execution.",
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in HH:MM format (24-hour).",
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in HH:MM format (24-hour).",
                },
                "date": {
                    "type": "string",
                    "description": "Campaign date in YYYY-MM-DD format.",
                },
                "target": {
                    "type": "string",
                    "description": "Target audience description (e.g. 'Young adults 18-30').",
                },
                "locality": {
                    "type": "string",
                    "description": "Location or area of the campaign (e.g. 'Koramangala, Bangalore').",
                },
                # Campaign props fields
                "stalls": {
                    "type": "integer",
                    "description": "Number of stalls required.",
                },
                "tables": {
                    "type": "integer",
                    "description": "Number of tables required.",
                },
                "chairs": {
                    "type": "integer",
                    "description": "Number of chairs required.",
                },
                "led": {
                    "type": "integer",
                    "description": "Number of LED screens/panels required.",
                },
                "banners": {
                    "type": "integer",
                    "description": "Number of banners required.",
                },
            },
            "required": ["description"],
        },
    },
}

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a campaign planning assistant for BrandActivation, an offline brand activation platform.

Your job is to help users fill in the details of a brand activation campaign.

A campaign has the following fields:
- description: What the campaign is about
- date: When it happens (YYYY-MM-DD)
- start_time / end_time: Working hours (HH:MM 24-hour)
- total_hours: Total duration in hours
- target: Who the campaign is targeting
- locality: Where the campaign is happening

Campaign equipment (props):
- stalls, tables, chairs, led (screens), banners — all integers

Rules:
1. Ask the user for any missing REQUIRED information (description, date, locality).
2. For optional fields (time, hours, target, props), if the user hasn't mentioned them, estimate sensible defaults based on context — do NOT ask about every single field.
3. Once you have description, date, and locality (at minimum), call the `populate_campaign` tool immediately.
4. Keep replies brief and conversational. Do not explain your reasoning — just ask what you need.
5. Never make up information the user has not provided or implied.\
"""


# ── Public function ───────────────────────────────────────────────────────────

def chat(
    messages: list[dict],
    api_key: str,
    model: str,
    site_url: str,
    site_name: str,
) -> dict:
    """
    Send the conversation to OpenRouter and return the raw API response dict.

    Returns a dict with keys:
      - "reply"     (str | None)  — assistant text reply (if no tool call)
      - "tool_call" (dict | None) — parsed tool arguments if populate_campaign was called
      - "messages"  (list[dict])  — updated conversation history including the new assistant turn
    """
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": _SYSTEM_PROMPT}] + messages,
        "tools": [_POPULATE_TOOL],
        "tool_choice": "auto",
    }

    headers = {
        "Authorization":  f"Bearer {api_key}",
        "HTTP-Referer":   site_url,
        "X-Title":        site_name,
        "Content-Type":   "application/json",
    }

    try:
        resp = requests.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"OpenRouter request failed: {exc}")
        raise RuntimeError("AI service is unavailable. Please try again.") from exc

    data = resp.json()

    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})

    tool_calls = message.get("tool_calls") or []
    reply: str | None = message.get("content") or None
    tool_args: dict | None = None

    # Parse the populate_campaign tool call if present
    if tool_calls:
        for tc in tool_calls:
            fn = tc.get("function", {})
            if fn.get("name") == "populate_campaign":
                try:
                    tool_args = json.loads(fn.get("arguments", "{}"))
                except (json.JSONDecodeError, ValueError):
                    tool_args = {}
                break

    # Append assistant turn to history
    updated_messages = messages + [{"role": "assistant", "content": reply or ""}]

    return {
        "reply":     reply,
        "tool_call": tool_args,
        "messages":  updated_messages,
    }
