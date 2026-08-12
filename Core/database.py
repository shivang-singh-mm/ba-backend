"""
Core Database — psycopg2 Connection Pool
-----------------------------------------
Manages a thread-safe PostgreSQL connection pool using psycopg2.
All query execution goes through `get_cursor()` or `get_conn()`.

Usage in crud.py:
    from Core.database import get_cursor

    def get_user(user_id):
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()
"""

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from Utils.logger import logger

# Global connection pool — initialised once in create_app()
_pool: ThreadedConnectionPool = None


def init_pool(database_url: str, min_conn: int = 2, max_conn: int = 10):
    """
    Initialise the psycopg2 threaded connection pool.
    Call this once during app startup.

    Args:
        database_url: Full PostgreSQL DSN (e.g. postgresql://user:pass@host/db).
        min_conn: Minimum number of idle connections to keep open.
        max_conn: Maximum number of simultaneous connections allowed.
    """
    global _pool
    _pool = ThreadedConnectionPool(minconn=min_conn, maxconn=max_conn, dsn=database_url)
    logger.info(f"PostgreSQL connection pool initialised (min={min_conn}, max={max_conn})")


def close_pool():
    """Close all connections in the pool. Call on app teardown."""
    global _pool
    if _pool:
        _pool.closeall()
        logger.info("PostgreSQL connection pool closed")


@contextmanager
def get_conn():
    """
    Context manager that checks out a raw psycopg2 connection from the pool.
    Auto-commits on success, rolls back on exception, returns connection to pool.

    Usage:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(...)
    """
    if _pool is None:
        raise RuntimeError("Database pool is not initialised. Call init_pool() first.")

    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


@contextmanager
def get_cursor(cursor_factory=RealDictCursor):
    """
    Context manager that yields a psycopg2 cursor with auto commit/rollback.
    Rows are returned as dicts by default (RealDictCursor).

    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()   # -> dict or None
            rows = cur.fetchall()  # -> list[dict]
    """
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
        finally:
            cur.close()


def fetchone(sql: str, params: tuple = ()):
    """Convenience: execute a query and return a single row as a dict (or None)."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetchall(sql: str, params: tuple = ()):
    """Convenience: execute a query and return all rows as a list of dicts."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params: tuple = ()):
    """Convenience: execute a write query (INSERT/UPDATE/DELETE). Returns rowcount."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


def execute_returning(sql: str, params: tuple = ()):
    """Execute an INSERT/UPDATE with RETURNING clause and return the first row."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
