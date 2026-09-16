"""
Location CRUD — Raw psycopg2 Queries
---------------------------------------
All queries run against the countries, states, and cities tables.
"""

from Core.database import fetchall, execute_returning
from .models import Country, State, City


# ── Country ───────────────────────────────────────────────────────────────────

def create_country(data: dict) -> dict:
    """Insert a new country row and return the created record."""
    row = execute_returning(
        """
        INSERT INTO countries (name, country_code, phone_code)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (data["name"], data["country_code"], data["phone_code"])
    )
    return Country.from_row(row).to_dict()


def update_country(country_id: int, data: dict) -> dict | None:
    """Update allowed fields on a country row."""
    allowed = {k: v for k, v in data.items() if k in ("name", "country_code", "phone_code")}
    if not allowed:
        return _get_country_by_id(country_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [country_id]

    row = execute_returning(
        f"UPDATE countries SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return Country.from_row(row).to_dict() if row else None


def get_countries(filters: dict) -> list[dict]:
    """Fetch countries, no filters supported (returns all)."""
    rows = fetchall("SELECT * FROM countries ORDER BY name ASC")
    return [Country.from_row(r).to_dict() for r in rows]


def _get_country_by_id(country_id: int) -> dict | None:
    """Fetch a single country by primary key."""
    from Core.database import fetchone
    row = fetchone("SELECT * FROM countries WHERE id = %s", (country_id,))
    return Country.from_row(row).to_dict() if row else None


# ── State ─────────────────────────────────────────────────────────────────────

def create_state(data: dict) -> dict:
    """Insert a new state row and return the created record."""
    row = execute_returning(
        """
        INSERT INTO states (name, country_id)
        VALUES (%s, %s)
        RETURNING *
        """,
        (data["name"], data["country_id"])
    )
    return State.from_row(row).to_dict()


def update_state(state_id: int, data: dict) -> dict | None:
    """Update allowed fields on a state row."""
    allowed = {k: v for k, v in data.items() if k in ("name", "country_id")}
    if not allowed:
        return _get_state_by_id(state_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [state_id]

    row = execute_returning(
        f"UPDATE states SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return State.from_row(row).to_dict() if row else None


def get_states(filters: dict) -> list[dict]:
    """Fetch states with optional country_id filter."""
    sql = "SELECT * FROM states"
    params: list = []

    if filters.get("country_id"):
        sql += " WHERE country_id = %s"
        params.append(int(filters["country_id"]))

    sql += " ORDER BY name ASC"
    rows = fetchall(sql, tuple(params))
    return [State.from_row(r).to_dict() for r in rows]


def _get_state_by_id(state_id: int) -> dict | None:
    """Fetch a single state by primary key."""
    from Core.database import fetchone
    row = fetchone("SELECT * FROM states WHERE id = %s", (state_id,))
    return State.from_row(row).to_dict() if row else None


# ── City ──────────────────────────────────────────────────────────────────────

def create_city(data: dict) -> dict:
    """Insert a new city row and return the created record."""
    row = execute_returning(
        """
        INSERT INTO cities (name, state_id)
        VALUES (%s, %s)
        RETURNING *
        """,
        (data["name"], data["state_id"])
    )
    return City.from_row(row).to_dict()


def update_city(city_id: int, data: dict) -> dict | None:
    """Update allowed fields on a city row."""
    allowed = {k: v for k, v in data.items() if k in ("name", "state_id")}
    if not allowed:
        return _get_city_by_id(city_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [city_id]

    row = execute_returning(
        f"UPDATE cities SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return City.from_row(row).to_dict() if row else None


def get_cities(filters: dict) -> list[dict]:
    """Fetch cities with optional state_id or country_id filter."""
    sql = "SELECT * FROM cities"
    conditions: list[str] = []
    params: list = []

    if filters.get("state_id"):
        conditions.append("state_id = %s")
        params.append(int(filters["state_id"]))

    if filters.get("country_id"):
        conditions.append(
            "state_id IN (SELECT id FROM states WHERE country_id = %s)"
        )
        params.append(int(filters["country_id"]))

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY name ASC"
    rows = fetchall(sql, tuple(params))
    return [City.from_row(r).to_dict() for r in rows]


def _get_city_by_id(city_id: int) -> dict | None:
    """Fetch a single city by primary key."""
    from Core.database import fetchone
    row = fetchone("SELECT * FROM cities WHERE id = %s", (city_id,))
    return City.from_row(row).to_dict() if row else None
