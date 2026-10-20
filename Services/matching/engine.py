"""
Matching Engine
----------------
Core hybrid matching pipeline for campaign-to-provider evaluation:
1. Hard filtering (deterministic eligibility).
2. Structured score calculation (location, language, industry, skills).
3. AI semantic experience scoring (evaluating provider_experiences and roles).
4. Configurable weighted score aggregation and ranking.
"""

from typing import Dict, Any, List, Tuple
from .models import MatchScoreBreakdown
from .ai import score_provider_experience_batch
from .enum import MATCH_STATUS


def run_matching_pipeline(
    campaign: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    weights: Dict[str, float],
    ai_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Orchestrate the full matching and ranking pipeline.
    """
    if not candidates:
        return []

    rules = campaign.get("matching_rules") or {}
    
    # Matching rules interpretation: 1=hard, 2=soft, 3=ignore
    loc_rule = rules.get("location_rule", "soft")
    lang_rule = rules.get("language_rule", "soft")
    ind_rule = rules.get("industry_rule", "soft")
    exp_rule = rules.get("experience_rule", "soft")
    out_rule = rules.get("output_rule", "soft")

    # ── Phase 1: Hard Filtering ────────────────────────────────────────────────
    eligible_candidates = []
    for cand in candidates:
        is_eligible, reasons = _check_hard_rules(campaign, cand, loc_rule, lang_rule, ind_rule, exp_rule)
        if is_eligible:
            eligible_candidates.append(cand)

    if not eligible_candidates:
        return []

    # ── Phase 2: Structured Scoring ───────────────────────────────────────────
    structured_scores: Dict[int, Dict[str, float]] = {}
    for cand in eligible_candidates:
        pid = cand["provider_id"]
        loc_score = _score_location(campaign, cand)
        lang_score = _score_languages(campaign, cand)
        ind_score = _score_industries(campaign, cand)
        skills_score = _score_skills(campaign, cand)

        structured_scores[pid] = {
            "location_score": loc_score,
            "language_score": lang_score,
            "industry_score": ind_score,
            "skills_score": skills_score,
        }

    # ── Phase 3: AI Semantic Experience Scoring ────────────────────────────────
    # Prepare concise representations
    campaign_summary = {
        "title": campaign.get("title"),
        "description": campaign.get("description"),
        "industries": [i.get("name") for i in campaign.get("industries", []) if i.get("name")],
        "types": [t.get("name") for t in campaign.get("types", []) if t.get("name")],
        "target": campaign.get("target"),
        "locality": campaign.get("locality"),
    }

    candidate_summaries = []
    for cand in eligible_candidates:
        candidate_summaries.append({
            "provider_id": cand["provider_id"],
            "provider_type": cand.get("provider_type"),
            "occupation": cand.get("current_occupation"),
            "skills": [s.get("name") for s in cand.get("skills", []) if s.get("name")],
            "industries": [i.get("name") for i in cand.get("industries", []) if i.get("name")],
            "experiences": cand.get("experiences", []),
        })

    ai_results = score_provider_experience_batch(campaign_summary, candidate_summaries, ai_config)

    # ── Phase 4: Weighted Score Aggregation ────────────────────────────────────
    evaluated_results = []
    
    w_loc = weights.get("location", 0.20) if loc_rule != "ignore" else 0.0
    w_lang = weights.get("language", 0.20) if lang_rule != "ignore" else 0.0
    w_ind = weights.get("industry", 0.15) if ind_rule != "ignore" else 0.0
    w_skill = weights.get("skills", 0.20)
    w_ai = weights.get("ai_experience", 0.25) if exp_rule != "ignore" else 0.0

    total_weight = w_loc + w_lang + w_ind + w_skill + w_ai
    if total_weight == 0:
        total_weight = 1.0

    for cand in eligible_candidates:
        pid = cand["provider_id"]
        s_scores = structured_scores[pid]
        ai_eval = ai_results.get(pid, {"score": 50.0, "reasoning": "Standard experience evaluation."})

        raw_total = (
            (s_scores["location_score"] * w_loc) +
            (s_scores["language_score"] * w_lang) +
            (s_scores["industry_score"] * w_ind) +
            (s_scores["skills_score"] * w_skill) +
            (ai_eval["score"] * w_ai)
        )
        final_score = round(raw_total / total_weight, 2)

        evaluated_results.append({
            "campaign_id": campaign["id"],
            "provider_id": pid,
            "total_score": final_score,
            "location_score": round(s_scores["location_score"], 2),
            "language_score": round(s_scores["language_score"], 2),
            "industry_score": round(s_scores["industry_score"], 2),
            "skills_score": round(s_scores["skills_score"], 2),
            "ai_experience_score": round(ai_eval["score"], 2),
            "ai_reasoning": ai_eval.get("reasoning"),
            "is_eligible": True,
            "match_status": "matched",
            "provider": {
                "provider_id": pid,
                "user_id": cand.get("user_id"),
                "name": cand.get("user_name"),
                "email": cand.get("user_email"),
                "phone": cand.get("user_phone"),
                "city_id": cand.get("city_id"),
                "city_name": cand.get("city_name"),
                "occupation": cand.get("current_occupation"),
                "bio": cand.get("provider_bio"),
                "is_verified": cand.get("is_verified", False),
                "skills": cand.get("skills", []),
                "languages": cand.get("languages", []),
                "industries": cand.get("industries", []),
                "experiences_count": len(cand.get("experiences", [])),
            }
        })

    # ── Phase 5: Ranking ───────────────────────────────────────────────────────
    evaluated_results.sort(key=lambda x: x["total_score"], reverse=True)
    return evaluated_results


def _check_hard_rules(
    campaign: Dict[str, Any],
    candidate: Dict[str, Any],
    loc_rule: str,
    lang_rule: str,
    ind_rule: str,
    exp_rule: str,
) -> Tuple[bool, List[str]]:
    """
    Evaluate deterministic hard rules. If candidate fails ANY active hard rule, they are disqualified.
    """
    reasons = []

    # 1. Location Hard Rule
    if loc_rule == "hard":
        camp_city_id = campaign.get("city_id")
        cand_city_id = candidate.get("city_id")
        if camp_city_id and cand_city_id and camp_city_id != cand_city_id:
            reasons.append(f"Location mismatch: Campaign city ({camp_city_id}) != Provider city ({cand_city_id})")

    # 2. Language Hard Rule
    if lang_rule == "hard":
        camp_langs = campaign.get("languages", [])
        cand_lang_ids = {l.get("id") or l.get("language_id") for l in candidate.get("languages", [])}
        for cl in camp_langs:
            cl_id = cl.get("id") or cl.get("language_id")
            if cl.get("is_required", True) and cl_id not in cand_lang_ids:
                reasons.append(f"Missing required language: {cl.get('name') or cl_id}")

    # 3. Industry Hard Rule
    if ind_rule == "hard":
        camp_inds = {i.get("id") or i.get("industry_id") for i in campaign.get("industries", [])}
        cand_inds = {i.get("id") or i.get("industry_id") for i in candidate.get("industries", [])}
        if camp_inds and not (camp_inds & cand_inds):
            reasons.append("No matching industry experience found")

    # 4. Experience / Skills Hard Rule
    if exp_rule == "hard":
        cand_exps = candidate.get("experiences", [])
        cand_skills = candidate.get("skills", [])
        if not cand_exps and not cand_skills:
            reasons.append("Provider has no listed past experiences or skills")

    is_eligible = len(reasons) == 0
    return is_eligible, reasons


def _score_location(campaign: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate location compatibility (0.0 to 100.0)."""
    camp_city_id = campaign.get("city_id")
    cand_city_id = candidate.get("city_id")

    if not camp_city_id:
        return 80.0  # Flexible campaign location

    if camp_city_id == cand_city_id:
        return 100.0
    return 30.0  # Different city base


def _score_languages(campaign: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate language coverage and proficiency score (0.0 to 100.0)."""
    camp_langs = campaign.get("languages", [])
    if not camp_langs:
        return 100.0

    cand_langs_map = {
        (l.get("id") or l.get("language_id")): (l.get("proficiency") or 2)
        for l in candidate.get("languages", [])
    }

    scores = []
    for cl in camp_langs:
        cl_id = cl.get("id") or cl.get("language_id")
        req_prof = cl.get("proficiency", 2)
        
        if cl_id in cand_langs_map:
            cand_prof = cand_langs_map[cl_id]
            # Convert str proficiency to int if needed
            if isinstance(cand_prof, str):
                prof_lut = {"basic": 1, "conversational": 2, "fluent": 3, "native": 4}
                cand_prof = prof_lut.get(cand_prof, 2)
            if isinstance(req_prof, str):
                prof_lut = {"basic": 1, "conversational": 2, "fluent": 3, "native": 4}
                req_prof = prof_lut.get(req_prof, 2)

            if cand_prof >= req_prof:
                scores.append(100.0)
            else:
                scores.append(70.0)
        else:
            scores.append(0.0 if cl.get("is_required", True) else 40.0)

    return sum(scores) / len(scores) if scores else 100.0


def _score_industries(campaign: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate industry overlap score (0.0 to 100.0)."""
    camp_inds = campaign.get("industries", [])
    if not camp_inds:
        return 80.0

    camp_ind_ids = {i.get("id") or i.get("industry_id") for i in camp_inds}
    cand_ind_ids = {i.get("id") or i.get("industry_id") for i in candidate.get("industries", [])}

    intersection = camp_ind_ids & cand_ind_ids
    if intersection:
        return min(100.0, 70.0 + len(intersection) * 15.0)
    return 30.0


def _score_skills(campaign: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate core skills coverage score (0.0 to 100.0)."""
    cand_skills = candidate.get("skills", [])
    if not cand_skills:
        return 40.0

    skill_count = len(cand_skills)
    score = 50.0 + min(50.0, skill_count * 10.0)
    return min(100.0, score)
