"""
Matching CRUD — Raw psycopg2 Queries
--------------------------------------
All database reads and writes for campaign-provider matching.
"""

from typing import Optional, List, Dict, Any
from Core.database import fetchone, fetchall, execute_returning, execute
from .models import CampaignProviderMatch
from .enum import MATCH_STATUS_ID, MATCH_STATUS


def get_all_provider_candidates() -> List[Dict[str, Any]]:
    """
    Fetch all active, non-deleted provider candidates with:
    - User details (name, email, phone)
    - City details
    - Skills (list of ids and names)
    - Languages (list of ids, names, proficiency integer)
    - Industries (list of ids, names)
    - Past user_experiences (brand_name, role_name, duration, description)
    """
    # 1. Fetch base provider profiles joined with users and cities
    provider_rows = fetchall(
        """
        SELECT 
            p.id AS provider_id,
            p.user_id,
            p.provider_type,
            p.description AS provider_bio,
            p.current_occupation,
            p.date_of_birth,
            p.gender,
            p.city_id,
            c.name AS city_name,
            p.is_verified,
            p.is_active,
            u.name AS user_name,
            u.email AS user_email,
            u.phone AS user_phone
        FROM provider_profiles p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN cities c ON p.city_id = c.id
        WHERE p.is_active = TRUE AND u.is_deleted = FALSE AND u.is_active = TRUE
        """
    )

    if not provider_rows:
        return []

    provider_ids = [r["provider_id"] for r in provider_rows]
    user_ids = [r["user_id"] for r in provider_rows]

    # 2. Fetch all skills for these providers
    skill_rows = fetchall(
        """
        SELECT ps.provider_id, s.id AS skill_id, s.name AS skill_name
        FROM provider_skills ps
        JOIN skills s ON ps.skill_id = s.id
        WHERE ps.provider_id = ANY(%s)
        """,
        (provider_ids,)
    )
    skills_map: Dict[int, List[Dict[str, Any]]] = {}
    for sr in skill_rows:
        skills_map.setdefault(sr["provider_id"], []).append({
            "id": sr["skill_id"],
            "name": sr["skill_name"],
        })

    # 3. Fetch all languages for these providers
    lang_rows = fetchall(
        """
        SELECT pl.provider_id, l.id AS language_id, l.name AS language_name, pl.proficiency
        FROM provider_languages pl
        JOIN languages l ON pl.language_id = l.id
        WHERE pl.provider_id = ANY(%s)
        """,
        (provider_ids,)
    )
    langs_map: Dict[int, List[Dict[str, Any]]] = {}
    for lr in lang_rows:
        langs_map.setdefault(lr["provider_id"], []).append({
            "id": lr["language_id"],
            "name": lr["language_name"],
            "proficiency": lr["proficiency"],
        })

    # 4. Fetch all industries for these providers
    ind_rows = fetchall(
        """
        SELECT pi.provider_id, i.id AS industry_id, i.name AS industry_name
        FROM provider_industries pi
        JOIN industries i ON pi.industry_id = i.id
        WHERE pi.provider_id = ANY(%s)
        """,
        (provider_ids,)
    )
    inds_map: Dict[int, List[Dict[str, Any]]] = {}
    for ir in ind_rows:
        inds_map.setdefault(ir["provider_id"], []).append({
            "id": ir["industry_id"],
            "name": ir["industry_name"],
        })

    # 5. Fetch past campaign user_experiences
    exp_rows = fetchall(
        """
        SELECT id, user_id, brand_name, role_name, duration, description
        FROM user_experiences
        WHERE user_id = ANY(%s)
        ORDER BY created_at DESC
        """,
        (user_ids,)
    )
    exp_map: Dict[int, List[Dict[str, Any]]] = {}
    for er in exp_rows:
        exp_map.setdefault(er["user_id"], []).append({
            "id": er["id"],
            "brand_name": er["brand_name"],
            "role_name": er["role_name"],
            "duration": er["duration"],
            "description": er["description"],
        })

    # 6. Assemble candidate dictionaries
    candidates = []
    for pr in provider_rows:
        pid = pr["provider_id"]
        uid = pr["user_id"]
        candidate = dict(pr)
        candidate["skills"] = skills_map.get(pid, [])
        candidate["languages"] = langs_map.get(pid, [])
        candidate["industries"] = inds_map.get(pid, [])
        candidate["experiences"] = exp_map.get(uid, [])
        candidates.append(candidate)

    return candidates


def save_match_results(campaign_id: int, match_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Persist or upsert matching scores into campaign_provider_matches table.
    """
    saved = []
    for m in match_results:
        provider_id = m["provider_id"]
        status_str = m.get("match_status", "matched")
        status_id = MATCH_STATUS_ID.get(status_str, 1)

        row = execute_returning(
            """
            INSERT INTO campaign_provider_matches (
                campaign_id, provider_id, total_score,
                location_score, language_score, industry_score,
                skills_score, ai_experience_score, ai_reasoning,
                is_eligible, match_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (campaign_id, provider_id)
            DO UPDATE SET
                total_score = EXCLUDED.total_score,
                location_score = EXCLUDED.location_score,
                language_score = EXCLUDED.language_score,
                industry_score = EXCLUDED.industry_score,
                skills_score = EXCLUDED.skills_score,
                ai_experience_score = EXCLUDED.ai_experience_score,
                ai_reasoning = EXCLUDED.ai_reasoning,
                is_eligible = EXCLUDED.is_eligible,
                match_status = EXCLUDED.match_status,
                updated_at = NOW()
            RETURNING *
            """,
            (
                campaign_id,
                provider_id,
                m["total_score"],
                m.get("location_score", 0.0),
                m.get("language_score", 0.0),
                m.get("industry_score", 0.0),
                m.get("skills_score", 0.0),
                m.get("ai_experience_score", 0.0),
                m.get("ai_reasoning"),
                m.get("is_eligible", True),
                status_id,
            )
        )
        saved.append(CampaignProviderMatch.from_row(row, provider=m.get("provider")).to_dict())

    return saved


def get_saved_matches_for_campaign(campaign_id: int, min_score: float = 0.0) -> List[Dict[str, Any]]:
    """
    Retrieve persisted match records for a campaign ordered by highest total score.
    """
    rows = fetchall(
        """
        SELECT 
            m.*,
            p.user_id,
            p.provider_type,
            p.description AS provider_bio,
            p.current_occupation,
            p.city_id,
            c.name AS city_name,
            p.is_verified,
            u.name AS user_name,
            u.email AS user_email,
            u.phone AS user_phone
        FROM campaign_provider_matches m
        JOIN provider_profiles p ON m.provider_id = p.id
        JOIN users u ON p.user_id = u.id
        LEFT JOIN cities c ON p.city_id = c.id
        WHERE m.campaign_id = %s AND m.is_eligible = TRUE AND m.total_score >= %s
        ORDER BY m.total_score DESC, m.created_at DESC
        """,
        (campaign_id, min_score)
    )

    results = []
    for r in rows:
        provider_data = {
            "provider_id": r["provider_id"],
            "user_id": r["user_id"],
            "name": r["user_name"],
            "email": r["user_email"],
            "phone": r["user_phone"],
            "city_id": r["city_id"],
            "city_name": r["city_name"],
            "occupation": r["current_occupation"],
            "bio": r["provider_bio"],
            "is_verified": r["is_verified"],
        }
        match_obj = CampaignProviderMatch.from_row(dict(r), provider=provider_data)
        results.append(match_obj.to_dict())

    return results


def get_all_matched_providers(
    user_id: Optional[int] = None,
    provider_id: Optional[int] = None,
    min_score: float = 0.0,
    match_status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List matched providers across campaigns.
    Optionally filter by campaign creator's user_id, provider_id, min_score, and match_status.
    """
    conditions = ["m.is_eligible = TRUE", "m.total_score >= %s"]
    params: List[Any] = [min_score]

    if user_id is not None:
        conditions.append("c.user_id = %s")
        params.append(user_id)

    if provider_id is not None:
        conditions.append("m.provider_id = %s")
        params.append(provider_id)

    if match_status is not None:
        status_id = MATCH_STATUS_ID.get(match_status.lower(), 1)
        conditions.append("m.match_status = %s")
        params.append(status_id)

    where_clause = " AND ".join(conditions)

    rows = fetchall(
        f"""
        SELECT 
            m.*,
            c.title AS campaign_title,
            c.user_id AS campaign_owner_id,
            p.user_id,
            p.provider_type,
            p.description AS provider_bio,
            p.current_occupation,
            p.city_id,
            ci.name AS city_name,
            p.is_verified,
            u.name AS user_name,
            u.email AS user_email,
            u.phone AS user_phone
        FROM campaign_provider_matches m
        JOIN campaigns c ON m.campaign_id = c.id
        JOIN provider_profiles p ON m.provider_id = p.id
        JOIN users u ON p.user_id = u.id
        LEFT JOIN cities ci ON p.city_id = ci.id
        WHERE {where_clause}
        ORDER BY m.total_score DESC, m.created_at DESC
        """,
        tuple(params)
    )

    results = []
    for r in rows:
        provider_data = {
            "provider_id": r["provider_id"],
            "user_id": r["user_id"],
            "name": r["user_name"],
            "email": r["user_email"],
            "phone": r["user_phone"],
            "city_id": r["city_id"],
            "city_name": r["city_name"],
            "occupation": r["current_occupation"],
            "bio": r["provider_bio"],
            "is_verified": r["is_verified"],
            "campaign_title": r["campaign_title"],
        }
        match_obj = CampaignProviderMatch.from_row(dict(r), provider=provider_data)
        results.append(match_obj.to_dict())

    return results


def get_match_by_id(match_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single match record by ID."""
    row = fetchone(
        """
        SELECT 
            m.*,
            c.title AS campaign_title,
            c.user_id AS campaign_owner_id,
            p.user_id,
            p.provider_type,
            p.description AS provider_bio,
            p.current_occupation,
            p.city_id,
            ci.name AS city_name,
            p.is_verified,
            u.name AS user_name,
            u.email AS user_email,
            u.phone AS user_phone
        FROM campaign_provider_matches m
        JOIN campaigns c ON m.campaign_id = c.id
        JOIN provider_profiles p ON m.provider_id = p.id
        JOIN users u ON p.user_id = u.id
        LEFT JOIN cities ci ON p.city_id = ci.id
        WHERE m.id = %s
        """,
        (match_id,)
    )
    if not row:
        return None

    provider_data = {
        "provider_id": row["provider_id"],
        "user_id": row["user_id"],
        "name": row["user_name"],
        "email": row["user_email"],
        "phone": row["user_phone"],
        "city_id": row["city_id"],
        "city_name": row["city_name"],
        "occupation": row["current_occupation"],
        "bio": row["provider_bio"],
        "is_verified": row["is_verified"],
        "campaign_title": row["campaign_title"],
        "campaign_owner_id": row["campaign_owner_id"],
    }
    return CampaignProviderMatch.from_row(dict(row), provider=provider_data).to_dict()


def update_match_status(match_id: int, status_str: str) -> Optional[Dict[str, Any]]:
    """Update match status (e.g. matched, shortlisted, contacted, accepted, rejected)."""
    status_id = MATCH_STATUS_ID.get(status_str.lower(), 1)
    row = execute_returning(
        """
        UPDATE campaign_provider_matches
        SET match_status = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id
        """,
        (status_id, match_id)
    )
    if not row:
        return None
    return get_match_by_id(match_id)

