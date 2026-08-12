# BrandActivation Backend — Engineering Rules

> **This file must be read and followed before making any change to this codebase.**
> It applies to every file inside `ba-backend/` without exception.

---

## 1. Code Philosophy

- **KISS first.** Clean, simple, and stupid — yet precise. If a solution feels clever, it probably needs to be simplified.
- **Don't change what isn't broken.** Touch only what is strictly required by the task. No opportunistic refactors, no "while I'm here" edits.
- **One thing per function.** Functions do exactly one job. If you need an `and` in the description, split it.
- **Explicit over implicit.** No magic. If behaviour is non-obvious, a short comment explains why — not what.

---

## 2. Folder & Module Structure

Every service under `Services/<module>/` follows this exact layout:

```
Services/<module>/
├── routes.py      ← HTTP layer only (Flask Blueprint)
├── crud.py        ← All PostgreSQL operations (psycopg2 raw SQL)
├── ai.py          ← All AI/ML logic and external model calls
├── models.py      ← Python dataclasses mirroring the DB table
├── schema.sql     ← PostgreSQL DDL (CREATE TABLE, indexes, triggers)
├── enum.py        ← Integer-keyed enum dicts for every enum column in this module
└── __init__.py
```

---

## 3. Strict Layer Responsibilities

### `routes.py`
- Defines the Flask Blueprint and all route handlers.
- Reads `request.get_json()` and extracts fields directly — no validation layer.
- Performs only simple presence checks (`if not data.get("email"): ...`).
- Calls `crud.py` for every database operation.
- Calls `ai.py` for every AI operation.
- **Routes never import from each other's `crud.py` or `ai.py` directly** (except `user.crud` in auth routes, which is documented).
- Returns responses via `Core.response` helpers only (`success_response`, `error_response`).

### `crud.py`
- Contains **only** psycopg2 SQL functions.
- Returns plain Python types: `dict | None`, `list[dict]`, `bool`, `int`.
- Never imports from `ai.py` — ever.
- Never calls Flask helpers, `current_app`, or `request`.
- Internal helpers (not called by routes) are **always prefixed with `_`**.

### `ai.py`
- Contains **only** AI/ML logic: prompt construction, model API calls, result parsing.
- Never imports from `crud.py` — ever.
- Receives all data it needs as function arguments from `routes.py`.
- Returns structured Python dicts or primitives.

### `models.py`
- Python `@dataclass` definitions that mirror the PostgreSQL table structure.
- Provides `from_row(dict) -> Self` and `to_dict() -> dict` methods.
- No business logic, no imports from `crud.py` or `ai.py`.

### `schema.sql`
- Pure PostgreSQL DDL only: `CREATE TABLE IF NOT EXISTS`, indexes, triggers.
- No DML (`INSERT`, `UPDATE`, `DELETE`) ever lives here.
- Applied via `scripts/init_db.py` in dependency order.

---

## 4. Function Naming Conventions

| Prefix / Pattern | Meaning |
|---|---|
| `_function_name` | Private / internal helper — not called directly by routes |
| `get_*` | Read-only DB fetch, returns data or `None` |
| `create_*` | INSERT, returns the new row as dict |
| `update_*` | UPDATE, returns updated row or `None` |
| `delete_*` / `soft_delete_*` | DELETE or soft-delete, returns `bool` |
| `initiate_*` | Starts a multi-step flow (e.g. OTP send) |
| `verify_*` | Validates an external input (e.g. OTP verify) |

---

## 5. Database Rules

- **psycopg2 only.** No SQLAlchemy, no ORM, no query builders — ever.
- **Always parameterized queries.** String-formatting SQL (`f"WHERE id = {id}"`) is forbidden.  
  Use `%s` placeholders and pass a `tuple` as the second argument.
- Use `Core.database` helpers (`fetchone`, `fetchall`, `execute`, `execute_returning`) for all queries.
- All schema changes go in the module's `schema.sql`. Re-run `scripts/init_db.py` after changes.
- Soft-delete (`is_deleted = TRUE`) over hard `DELETE` wherever records have relationships.

---

## 6. Return Conventions

### `crud.py` functions
Always return a simple value — never raise HTTP errors:
```python
# Good
def get_user(user_id: int) -> dict | None: ...

# Good — business logic error signalling
def initiate_login(data: dict) -> tuple[dict | None, str | None]: ...
#   returns (result, error_string) — caller checks for error

# Bad — never do this in crud
abort(404)
```

### `routes.py` handlers
Always use `Core.response` helpers:
```python
return success_response(data=user, message="Fetched.")
return error_response("User not found", 404)
```

---

## 7. Error Handling

- Let unhandled exceptions propagate to `Core.error_handlers` — don't swallow them with bare `except`.
- Catch only specific, expected exceptions (e.g. `psycopg2.errors.UniqueViolation`).
- Log unexpected errors with `Utils.logger.logger.error(...)` before re-raising.
- Never `print()` — always use the logger.

---

## 8. Imports & Circular Dependencies

- Import order: stdlib → third-party → `Core` → `Utils` → sibling module.
- No circular imports. `crud.py` and `ai.py` must never import from each other.
- Avoid wildcard imports (`from module import *`).

---

## 9. Environment & Configuration

- Every configurable value lives in `.env` and is read via `Config/settings.py`.
- **No hardcoded secrets, URLs, or magic numbers** anywhere in source files.
- Use `current_app.config.get("KEY")` inside Flask context; `os.environ.get("KEY")` outside it.

---

## 10. Type Hints

- All function signatures must have type hints for parameters and return types.
- Use `dict | None`, `list[dict]`, `str | None`, `tuple[dict | None, str | None]`.
- `from __future__ import annotations` is not required — Python 3.10+ union syntax (`X | Y`) is sufficient.

---

## 11. Docstrings

- Every public function (not prefixed with `_`) gets a one-line docstring.
- Internal helpers (`_`) get a docstring only if the logic is non-obvious.
- Docstrings describe **what** the function does and what it **returns** — not how.

---

## 12. What Is Absolutely Forbidden

| Action | Reason |
|---|---|
| Adding `validation.py` to any module | Validation layer was intentionally removed |
| Adding Marshmallow schemas | Removed; not part of the stack |
| Using SQLAlchemy / Flask-Migrate | Replaced by raw psycopg2 |
| `crud.py` importing `ai.py` | Hard architectural boundary |
| `ai.py` importing `crud.py` | Hard architectural boundary |
| Hardcoded credentials or URLs | Security / portability |
| `print()` statements | Use `Utils.logger` |
| Non-parameterized SQL | SQL injection risk |
| Storing enum values as raw strings in DB | Use integer codes defined in `enum.py` |
| Defining enums outside `enum.py` | All enum dicts live in the module's `enum.py` only |

---

## 13. Enum Convention

Every enumerated value (role, status, type, purpose, etc.) follows this pattern:

### Where it lives
- Each service module that owns an enum column has an `enum.py` file.
- `enum.py` is the **single source of truth** for both Python code and the database schema.

### Format — integer-keyed dict

```python
# Services/user/enum.py

# Integer → string label (used for display / serialisation)
ROLE = {
    1: "user",
    2: "admin",
    3: "manager",
    4: "brand",
    5: "agency",
}

# Reverse: string label → integer (used when writing to the DB)
ROLE_ID = {v: k for k, v in ROLE.items()}
```

### Rules
- Dict name is `UPPER_SNAKE_CASE` matching the column name: `ROLE`, `STATUS`, `PURPOSE`.
- The reverse lookup dict is always named `<DICT_NAME>_ID`: `ROLE_ID`, `STATUS_ID`.
- Integers start at `1` — never use `0` as a meaningful value.
- Values are lowercase strings: `"user"`, `"admin"`, not `"User"` or `"ADMIN"`.
- The PostgreSQL column stores the **integer**, never the string.
- The comment in `schema.sql` documents the mapping inline.

### schema.sql usage

```sql
-- Role: 1=user, 2=admin, 3=manager, 4=brand, 5=agency
role  SMALLINT  NOT NULL DEFAULT 1
```

### crud.py usage

```python
from .enum import ROLE, ROLE_ID

# Writing — convert string to int before inserting
role_id = ROLE_ID.get(data["role"], 1)          # default to 1 (user)
execute("INSERT INTO users (role) VALUES (%s)", (role_id,))

# Reading — convert int to string after fetching
row["role"] = ROLE.get(row["role"], "user")
```

### What belongs in enum.py

Only pure Python dict literals — no imports, no logic, no functions.
