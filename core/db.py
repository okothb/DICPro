"""
Database connection and query handler for Neon DB for the FastAPI server.
Uses a connection pool for efficient database access.
"""

import os
import logging
from typing import Optional, Any

try:
    import psycopg2
    from psycopg2 import pool
except Exception:  # pragma: no cover
    psycopg2 = None
    pool = None


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_db_pool: Optional["pool.SimpleConnectionPool"] = None


def get_db_pool() -> Optional["pool.SimpleConnectionPool"]:
    """Initializes and returns a singleton database connection pool.

    Returns None if psycopg2 is unavailable or env vars are missing.
    """
    global _db_pool

    if _db_pool is not None:
        return _db_pool

    if psycopg2 is None or pool is None:
        logger.warning("psycopg2 is not installed; DB features disabled")
        return None

    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        logger.warning("NEON_DATABASE_URL not set; DB features disabled")
        return None

    try:
        logger.info("Initializing Neon DB connection pool…")
        _db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=int(os.getenv("DB_MAX_CONN", "5")),
            dsn=db_url,
        )
        logger.info("Neon DB connection pool initialized")
    except Exception as exc:  # pragma: no cover
        logger.error(f"Failed to initialize DB pool: {exc}")
        _db_pool = None

    return _db_pool


def execute_query(query: str, params: tuple = None, fetch: Optional[str] = None) -> Optional[Any]:
    """Execute a SQL query using a connection from the pool.

    - fetch=None: commit and return None
    - fetch='one': return cursor.fetchone()
    - fetch='all': return cursor.fetchall()
    Returns None if pool is unavailable.
    """
    dbp = get_db_pool()
    if not dbp:
        return None

    conn = None
    cur = None
    try:
        conn = dbp.getconn()
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch == 'one':
            return cur.fetchone()
        if fetch == 'all':
            return cur.fetchall()
        conn.commit()
        return None
    except Exception as exc:  # pragma: no cover
        if conn:
            conn.rollback()
        logger.error(f"DB query failed: {exc}")
        return None
    finally:
        if cur:
            cur.close()
        if conn and dbp:
            dbp.putconn(conn)


def setup_database() -> None:
    """Create the hashes table if it does not exist."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS document_hashes (
        id SERIAL PRIMARY KEY,
        original_hash VARCHAR(64) NOT NULL,
        protected_hash VARCHAR(64) NOT NULL UNIQUE,
        original_filename VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(create_sql)
    logger.info("Ensured table 'document_hashes' exists")


