"""
Dashboard CRUD Operations
--------------------------
Gathers aggregated dashboard data for Providers and Brands.
"""

from typing import Dict, Any, List
from Core.database import fetchone, fetchall
from Services.campaigns.crud import get_campaign_by_id


def get_provider_dashboard(user_id: int) -> Dict[str, Any]:
    """
    Fetch dashboard data for a Provider:
    1. Navbar context (user details, role, profile image)
    2. Greeting context (user name, occupation, city)
    3. Latest campaigns matching provider's experience / city / skills
    """
    # 1. Fetch user base details
    user = fetchone(
        "SELECT id, name, email, phone, role FROM users WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    if not user:
        return {}

    # 2. Fetch provider profile
    provider = fetchone(
        """
        SELECT pp.id AS provider_id, pp.current_occupation, pp.profile_image_url, 
               pp.city_id, c.name AS city_name, pp.is_verified, pp.is_active
        FROM provider_profiles pp
        LEFT JOIN cities c ON pp.city_id = c.id
        WHERE pp.user_id = %s
        """,
        (user_id,)
    )

    navbar_data = {
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "profile_image_url": provider.get("profile_image_url") if provider else None,
        "is_verified": provider.get("is_verified", False) if provider else False,
    }

    greeting_data = {
        "greeting": f"Hello, {user['name'].split()[0]}!",
        "full_name": user["name"],
        "occupation": provider.get("current_occupation", "Talent / Ambassador") if provider else "Talent",
        "city_name": provider.get("city_name") if provider else None,
    }

    # 3. Explore latest campaigns matching provider
    matching_campaigns: List[Dict[str, Any]] = []

    if provider and provider.get("provider_id"):
        pid = provider["provider_id"]
        pcity_id = provider.get("city_id")

        # Get provider skills & industries for smart relevance
        p_skills = fetchall("SELECT skill_id FROM provider_skills WHERE provider_id = %s", (pid,))
        p_skill_ids = [r["skill_id"] for r in p_skills]

        p_exps = fetchall("SELECT brand_name, role_name FROM provider_experiences WHERE provider_id = %s", (pid,))
        exp_roles = [e["role_name"].lower() for e in p_exps if e.get("role_name")]

        # Query active / open campaigns (status in 2, 3: pending/active)
        # Prioritize matching city or matching skill/type, ordered by latest created_at
        campaign_rows = fetchall(
            """
            SELECT DISTINCT c.id, c.title, c.description, c.city_id, ci.name AS city_name,
                   c.locality, c.date, c.start_time, c.end_time, c.total_hours,
                   c.status, c.created_at,
                   u.name AS creator_name,
                   bp.brand_name, bp.brand_logo_url
            FROM campaigns c
            LEFT JOIN cities ci ON c.city_id = ci.id
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN brand_profiles bp ON u.id = bp.user_id
            WHERE c.is_deleted = FALSE AND c.status IN (2, 3)
            ORDER BY c.created_at DESC
            LIMIT 20
            """
        )

        for cr in campaign_rows:
            cid = cr["id"]
            # Fetch campaign skills
            c_skills = fetchall(
                "SELECT s.id, s.name FROM campaign_skills cs JOIN skills s ON cs.skill_id = s.id WHERE cs.campaign_id = %s",
                (cid,)
            )
            c_skill_ids = [s["id"] for s in c_skills]

            # Calculate a quick compatibility score / badge for UI
            reasons = []
            if pcity_id and cr["city_id"] == pcity_id:
                reasons.append(f"In your city ({cr.get('city_name')})")

            shared_skills = set(p_skill_ids).intersection(set(c_skill_ids))
            if shared_skills:
                reasons.append(f"{len(shared_skills)} skills matched")

            # Check if any role matches
            c_title = (cr.get("title") or "").lower()
            if any(role in c_title for role in exp_roles):
                reasons.append("Matches past campaign experience")

            matching_campaigns.append({
                "id": cr["id"],
                "title": cr["title"],
                "description": cr["description"],
                "brand_name": cr.get("brand_name") or cr.get("creator_name") or "Featured Brand",
                "brand_logo_url": cr.get("brand_logo_url"),
                "city_id": cr.get("city_id"),
                "city_name": cr.get("city_name"),
                "locality": cr.get("locality"),
                "date": cr.get("date").isoformat() if cr.get("date") else None,
                "start_time": str(cr.get("start_time")) if cr.get("start_time") else None,
                "end_time": str(cr.get("end_time")) if cr.get("end_time") else None,
                "total_hours": float(cr.get("total_hours")) if cr.get("total_hours") else None,
                "status": cr.get("status"),
                "skills": c_skills,
                "match_reasons": reasons if reasons else ["Open for applications"],
                "is_city_match": bool(pcity_id and cr["city_id"] == pcity_id),
            })
    else:
        # Fallback if provider profile not created yet: return latest open campaigns
        campaign_rows = fetchall(
            """
            SELECT c.id, c.title, c.description, c.city_id, ci.name AS city_name,
                   c.locality, c.date, c.start_time, c.end_time, c.total_hours, c.created_at,
                   bp.brand_name, bp.brand_logo_url
            FROM campaigns c
            LEFT JOIN cities ci ON c.city_id = ci.id
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN brand_profiles bp ON u.id = bp.user_id
            WHERE c.is_deleted = FALSE AND c.status IN (2, 3)
            ORDER BY c.created_at DESC
            LIMIT 10
            """
        )
        for cr in campaign_rows:
            matching_campaigns.append({
                "id": cr["id"],
                "title": cr["title"],
                "description": cr["description"],
                "brand_name": cr.get("brand_name") or "Featured Brand",
                "brand_logo_url": cr.get("brand_logo_url"),
                "city_name": cr.get("city_name"),
                "locality": cr.get("locality"),
                "date": cr.get("date").isoformat() if cr.get("date") else None,
                "match_reasons": ["Open for applications"],
                "is_city_match": False,
            })

    return {
        "navbar": navbar_data,
        "greeting": greeting_data,
        "explore_campaigns": matching_campaigns,
    }


def get_brand_dashboard(user_id: int) -> Dict[str, Any]:
    """
    Brand dashboard payload:
    - navbar: brand name, logo, verified status
    - greeting: welcome message + city
    - my_campaigns: all campaigns with stats (total / active / draft)
    """
    user = fetchone(
        "SELECT id, name, email, phone, role FROM users WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    if not user:
        return {}

    brand = fetchone(
        """
        SELECT bp.id AS brand_id, bp.brand_name, bp.brand_logo_url,
               bp.brand_description, bp.brand_website,
               bp.is_verified, c.name AS city_name
        FROM brand_profiles bp
        LEFT JOIN cities c ON bp.city_id = c.id
        WHERE bp.user_id = %s
        """,
        (user_id,)
    )

    navbar_data = {
        "user_id": user["id"],
        "name": brand.get("brand_name") if brand else user["name"],
        "email": user["email"],
        "role": "brand",
        "brand_logo_url": brand.get("brand_logo_url") if brand else None,
        "is_verified": brand.get("is_verified", False) if brand else False,
    }

    greeting_data = {
        "greeting": f"Welcome back, {brand.get('brand_name') or user['name']}!",
        "brand_name": brand.get("brand_name") if brand else user["name"],
        "city_name": brand.get("city_name") if brand else None,
    }

    # Campaign status map: 1=draft, 2=pending, 3=active, 4=completed, 5=cancelled
    STATUS_LABELS = {1: "Draft", 2: "Pending", 3: "Active", 4: "Completed", 5: "Cancelled"}

    campaign_rows = fetchall(
        """
        SELECT c.id, c.title, c.description, c.status,
               c.date, c.start_time, c.end_time, c.total_hours,
               c.locality, ci.name AS city_name, c.created_at
        FROM campaigns c
        LEFT JOIN cities ci ON c.city_id = ci.id
        WHERE c.user_id = %s AND c.is_deleted = FALSE
        ORDER BY c.created_at DESC
        """,
        (user_id,)
    )

    campaigns_list = []
    total = 0
    active_count = 0
    draft_count = 0

    for cr in campaign_rows:
        total += 1
        s = cr.get("status", 1)
        if s == 3:
            active_count += 1
        elif s == 1:
            draft_count += 1

        # Fetch match count for this campaign
        match_count = fetchone(
            "SELECT COUNT(*) AS cnt FROM campaign_provider_matches WHERE campaign_id = %s AND is_eligible = TRUE",
            (cr["id"],)
        )

        campaigns_list.append({
            "id": cr["id"],
            "title": cr["title"],
            "description": cr.get("description"),
            "status": s,
            "status_label": STATUS_LABELS.get(s, "Unknown"),
            "city_name": cr.get("city_name"),
            "locality": cr.get("locality"),
            "date": cr.get("date").isoformat() if cr.get("date") else None,
            "start_time": str(cr.get("start_time")) if cr.get("start_time") else None,
            "end_time": str(cr.get("end_time")) if cr.get("end_time") else None,
            "total_hours": float(cr.get("total_hours")) if cr.get("total_hours") else None,
            "matched_providers": match_count["cnt"] if match_count else 0,
            "created_at": cr["created_at"].isoformat() if cr.get("created_at") else None,
        })

    return {
        "navbar": navbar_data,
        "greeting": greeting_data,
        "stats": {
            "total": total,
            "active": active_count,
            "draft": draft_count,
        },
        "my_campaigns": campaigns_list,
    }

