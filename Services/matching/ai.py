"""
Matching AI Module
-------------------
Pluggable AI layer for semantic experience matching between campaign requirements
and provider past brand experiences / roles / skills.

Configurable via environment variables (e.g. MATCHING_AI_PROVIDER, MATCHING_AI_MODEL).
Supports OpenAI (GPT-3.5-turbo default) and OpenRouter with graceful heuristic fallbacks.
"""

import json
import requests
from typing import List, Dict, Any, Tuple
from Utils.logger import logger

_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def score_provider_experience_batch(
    campaign_summary: Dict[str, Any],
    candidate_summaries: List[Dict[str, Any]],
    ai_config: Dict[str, Any],
) -> Dict[int, Dict[str, Any]]:
    """
    Score a batch of candidates on their semantic experience fit against campaign requirements.
    
    Returns a dict keyed by provider_id:
      {
        provider_id: {
            "score": float (0-100),
            "reasoning": str
        }
      }
    """
    if not candidate_summaries:
        return {}

    provider = (ai_config.get("provider") or "openai").lower()
    model = ai_config.get("model") or "gpt-3.5-turbo"
    openai_key = ai_config.get("openai_api_key", "")
    openrouter_key = ai_config.get("openrouter_api_key", "")

    # Fallback to heuristic scoring if no API key is provided
    if (provider == "openai" and not openai_key) or (provider == "openrouter" and not openrouter_key):
        logger.info(f"AI matching API key not configured for provider '{provider}'. Using rule-based experience heuristic.")
        return _fallback_experience_scores(campaign_summary, candidate_summaries)

    try:
        if provider == "openai":
            return _call_openai_batch(campaign_summary, candidate_summaries, model, openai_key)
        elif provider == "openrouter":
            return _call_openrouter_batch(
                campaign_summary,
                candidate_summaries,
                model,
                openrouter_key,
                ai_config.get("site_url", ""),
                ai_config.get("site_name", "BrandActivation")
            )
        else:
            logger.warning(f"Unsupported AI provider '{provider}'. Falling back to heuristic scoring.")
            return _fallback_experience_scores(campaign_summary, candidate_summaries)
    except Exception as exc:
        logger.error(f"AI semantic matching failed: {exc}. Falling back to heuristic scoring.")
        return _fallback_experience_scores(campaign_summary, candidate_summaries)


def _build_prompt(campaign_summary: Dict[str, Any], candidate_summaries: List[Dict[str, Any]]) -> str:
    """Build a concise, structured prompt for batch semantic evaluation."""
    campaign_text = f"""CAMPAIGN REQUIREMENTS:
- Title: {campaign_summary.get('title')}
- Description: {campaign_summary.get('description') or 'N/A'}
- Industries: {', '.join(campaign_summary.get('industries', [])) or 'General'}
- Campaign Types: {', '.join(campaign_summary.get('types', [])) or 'General Promotion'}
- Required / Context Target: {campaign_summary.get('target') or 'N/A'}
- Locality / Venue: {campaign_summary.get('locality') or 'N/A'}"""

    candidates_text_list = []
    for c in candidate_summaries:
        exps = []
        for e in c.get("experiences", []):
            exps.append(f"{e.get('role_name')} at {e.get('brand_name')} ({e.get('duration') or 'N/A'}): {e.get('description') or ''}")
        exp_str = "; ".join(exps) if exps else "No formal past activation experience listed."

        c_text = f"""Candidate #{c.get('provider_id')}:
- Type: {c.get('provider_type')} | Occupation: {c.get('occupation') or 'N/A'}
- Skills: {', '.join(c.get('skills', [])) or 'None'}
- Industries: {', '.join(c.get('industries', [])) or 'None'}
- Past Experiences: {exp_str}"""
        candidates_text_list.append(c_text)

    prompt = f"""You are an expert recruitment and offline brand activation campaign evaluator.
Evaluate how well each candidate's past work experience, brand background, roles, and skills match the campaign's needs.

{campaign_text}

CANDIDATES TO EVALUATE:
{chr(10).join(candidates_text_list)}

OUTPUT INSTRUCTIONS:
Return a valid, raw JSON array of objects with the exact format:
[
  {{
    "provider_id": <int>,
    "score": <float between 0.0 and 100.0 representing semantic fit of experience>,
    "reasoning": "<1 concise sentence explaining the score based on their past roles and skills>"
  }}
]

Important:
- High score (80-100): Direct past experience in similar brand activations, roles (e.g. sampling, emcee, promoter), or same industry.
- Moderate score (50-79): Transferable event or promotion skills, adjacent experience.
- Lower score (10-49): Limited relevant experience or generic profile.
- Return ONLY the JSON array without markdown code fences or backticks."""
    return prompt


def _call_openai_batch(
    campaign_summary: Dict[str, Any],
    candidate_summaries: List[Dict[str, Any]],
    model: str,
    api_key: str,
) -> Dict[int, Dict[str, Any]]:
    prompt = _build_prompt(campaign_summary, candidate_summaries)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise evaluation AI that outputs JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(_OPENAI_URL, json=payload, headers=headers, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return _parse_ai_json(content, candidate_summaries)


def _call_openrouter_batch(
    campaign_summary: Dict[str, Any],
    candidate_summaries: List[Dict[str, Any]],
    model: str,
    api_key: str,
    site_url: str,
    site_name: str,
) -> Dict[int, Dict[str, Any]]:
    prompt = _build_prompt(campaign_summary, candidate_summaries)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise evaluation AI that outputs JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
        "Content-Type": "application/json",
    }

    resp = requests.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return _parse_ai_json(content, candidate_summaries)


def _parse_ai_json(raw_content: str, candidate_summaries: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Clean and parse JSON from model response."""
    text = raw_content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
        results = {}
        if isinstance(parsed, list):
            for item in parsed:
                pid = item.get("provider_id")
                if pid:
                    score = float(item.get("score", 50.0))
                    score = max(0.0, min(100.0, score))
                    results[pid] = {
                        "score": score,
                        "reasoning": item.get("reasoning", "Relevant experience evaluated by AI."),
                    }
        return results
    except Exception as exc:
        logger.error(f"Failed to parse AI response JSON: {exc}. Raw content was: {text[:200]}")
        return _fallback_experience_scores({}, candidate_summaries)


def _fallback_experience_scores(
    campaign_summary: Dict[str, Any],
    candidate_summaries: List[Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    Deterministic rule-based experience fit calculation used as fallback when AI is unavailable.
    """
    results = {}
    for c in candidate_summaries:
        pid = c.get("provider_id")
        exps = c.get("experiences", [])
        skills = c.get("skills", [])
        
        # Base score based on count and depth of experiences
        exp_count = len(exps)
        skill_count = len(skills)
        
        score = 40.0 + min(30.0, exp_count * 15.0) + min(20.0, skill_count * 4.0)
        if c.get("provider_type") in ("freelancer", "agency"):
            score += 10.0
        
        score = min(95.0, score)
        
        reason = f"{exp_count} past experience record(s) and {skill_count} relevant skill(s) on profile."
        results[pid] = {
            "score": score,
            "reasoning": reason,
        }
    return results
