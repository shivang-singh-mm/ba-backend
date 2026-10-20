"""
Provider CRUD — Raw psycopg2 Queries
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import ProviderProfile, ProviderExperience
from .enum import PROVIDER_TYPE_ID, PROFICIENCY, PROFICIENCY_ID, DOCUMENT_TYPE, DOCUMENT_TYPE_ID


def get_all_providers() -> list[dict]:
    rows = fetchall("SELECT * FROM provider_profiles WHERE is_active = TRUE ORDER BY created_at DESC")
    results = []
    for r in rows:
        results.append(get_provider_by_id(r["id"]))
    return [res for res in results if res is not None]


def get_provider_by_id(provider_id: int) -> dict | None:
    row = fetchone("SELECT * FROM provider_profiles WHERE id = %s", (provider_id,))
    if not row:
        return None

    # Fetch relations
    industries = fetchall(
        "SELECT i.id, i.name FROM provider_industries pi JOIN industries i ON pi.industry_id = i.id WHERE pi.provider_id = %s",
        (provider_id,)
    )
    skills = fetchall(
        "SELECT s.id, s.name FROM provider_skills ps JOIN skills s ON ps.skill_id = s.id WHERE ps.provider_id = %s",
        (provider_id,)
    )
    
    lang_rows = fetchall(
        "SELECT l.id, l.name, pl.proficiency FROM provider_languages pl JOIN languages l ON pl.language_id = l.id WHERE pl.provider_id = %s",
        (provider_id,)
    )
    languages = []
    for lr in lang_rows:
        languages.append({
            "id": lr["id"],
            "name": lr["name"],
            "proficiency": PROFICIENCY.get(lr["proficiency"], "basic")
        })

    doc_rows = fetchall(
        "SELECT id, document_type, url, description FROM provider_documents WHERE provider_id = %s",
        (provider_id,)
    )
    documents = []
    for dr in doc_rows:
        documents.append({
            "id": dr["id"],
            "document_type": DOCUMENT_TYPE.get(dr["document_type"], "other"),
            "url": dr["url"],
            "description": dr["description"]
        })

    exp_rows = fetchall(
        "SELECT * FROM provider_experiences WHERE provider_id = %s ORDER BY created_at DESC",
        (provider_id,)
    )
    experiences = [ProviderExperience.from_row(er).to_dict() for er in exp_rows]

    return ProviderProfile.from_row(row, industries, skills, languages, documents, experiences).to_dict()


def get_provider_by_user_id(user_id: int) -> dict | None:
    row = fetchone("SELECT id FROM provider_profiles WHERE user_id = %s", (user_id,))
    if not row:
        return None
    return get_provider_by_id(row["id"])


def create_provider_profile(user_id: int, data: dict) -> dict:
    prov_type_str = data.get("provider_type", "individual")
    prov_type_id = PROVIDER_TYPE_ID.get(prov_type_str, 1)

    row = execute_returning(
        """
        INSERT INTO provider_profiles (user_id, provider_type, description, current_occupation, date_of_birth, gender, profile_image_url, city_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            user_id,
            prov_type_id,
            data.get("description"),
            data.get("current_occupation"),
            data.get("date_of_birth"),
            data.get("gender"),
            data.get("profile_image_url"),
            data.get("city_id")
        )
    )
    
    # Create relations if provided
    provider_id = row["id"]
    
    if "industry_ids" in data:
        for ind_id in data["industry_ids"]:
            execute("INSERT INTO provider_industries (provider_id, industry_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (provider_id, ind_id))
            
    if "skill_ids" in data:
        for sk_id in data["skill_ids"]:
            execute("INSERT INTO provider_skills (provider_id, skill_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (provider_id, sk_id))

    if "languages" in data:
        for lang in data["languages"]:
            l_id = lang.get("id")
            prof_str = lang.get("proficiency", "basic")
            prof_id = PROFICIENCY_ID.get(prof_str, 1)
            execute("INSERT INTO provider_languages (provider_id, language_id, proficiency) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (provider_id, l_id, prof_id))

    return get_provider_by_id(provider_id)


def update_provider_personal(provider_id: int, data: dict) -> dict | None:
    allowed = {k: v for k, v in data.items() if k in ("description", "current_occupation", "date_of_birth", "gender", "profile_image_url", "city_id")}
    if not allowed:
        return get_provider_by_id(provider_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [provider_id]

    execute(f"UPDATE provider_profiles SET {set_clause} WHERE id = %s", tuple(values))
    return get_provider_by_id(provider_id)


def update_provider_professional(provider_id: int, data: dict) -> dict | None:
    # Update provider type if passed
    if "provider_type" in data:
        prov_type_id = PROVIDER_TYPE_ID.get(data["provider_type"], 1)
        execute("UPDATE provider_profiles SET provider_type = %s WHERE id = %s", (prov_type_id, provider_id))

    # Update junction tables (replace all)
    if "industry_ids" in data:
        execute("DELETE FROM provider_industries WHERE provider_id = %s", (provider_id,))
        for ind_id in data["industry_ids"]:
            execute("INSERT INTO provider_industries (provider_id, industry_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (provider_id, ind_id))

    if "skill_ids" in data:
        execute("DELETE FROM provider_skills WHERE provider_id = %s", (provider_id,))
        for sk_id in data["skill_ids"]:
            execute("INSERT INTO provider_skills (provider_id, skill_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (provider_id, sk_id))

    if "languages" in data:
        execute("DELETE FROM provider_languages WHERE provider_id = %s", (provider_id,))
        for lang in data["languages"]:
            l_id = lang.get("id")
            prof_str = lang.get("proficiency", "basic")
            prof_id = PROFICIENCY_ID.get(prof_str, 1)
            execute("INSERT INTO provider_languages (provider_id, language_id, proficiency) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (provider_id, l_id, prof_id))

    return get_provider_by_id(provider_id)


# ── Provider Experiences CRUD ─────────────────────────────────────────────────

def get_provider_experiences(provider_id: int) -> list[dict]:
    """Retrieve all past campaign experiences for a provider."""
    rows = fetchall(
        "SELECT * FROM provider_experiences WHERE provider_id = %s ORDER BY created_at DESC",
        (provider_id,)
    )
    return [ProviderExperience.from_row(r).to_dict() for r in rows]


def add_provider_experience(provider_id: int, data: dict) -> dict:
    """Add a new past campaign experience record for a provider."""
    row = execute_returning(
        """
        INSERT INTO provider_experiences (provider_id, brand_name, role_name, duration, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (provider_id, data.get("brand_name"), data.get("role_name"), data.get("duration"), data.get("description"))
    )
    return ProviderExperience.from_row(row).to_dict()


def delete_provider_experience(provider_id: int, experience_id: int) -> bool:
    """Delete a specific experience record for a provider."""
    affected = execute(
        "DELETE FROM provider_experiences WHERE id = %s AND provider_id = %s",
        (experience_id, provider_id)
    )
    return affected > 0
