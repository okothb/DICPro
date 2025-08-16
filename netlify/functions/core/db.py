"""
Database connection and query handler for Neon DB.
Uses a connection pool for efficient database access in a serverless environment.
"""

import os
import psycopg2
from psycopg2 import pool
from typing import Optional, Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton connection pool
db_pool = None

def get_db_pool():
    """Initializes and returns a singleton database connection pool."""
    global db_pool
    if db_pool is None:
        try:
            # Your Neon DB connection string should be set as an environment variable in Netlify
            db_url = os.getenv("NEON_DATABASE_URL")
            if not db_url:
                raise ValueError("NEON_DATABASE_URL environment variable not set.")
            
            logger.info("Initializing database connection pool...")
            db_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=db_url
            )
            logger.info("Database connection pool initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            db_pool = None # Ensure it's None on failure
    return db_pool

def execute_query(query: str, params: tuple = None, fetch: str = None) -> Optional[Any]:
    """Executes a SQL query using a connection from the pool."""
    conn = None
    cursor = None
    pool = get_db_pool()
    if not pool:
        logger.error("Cannot execute query: Database pool is not available.")
        return None

    try:
        conn = pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch == 'one':
            return cursor.fetchone()
        elif fetch == 'all':
            return cursor.fetchall()
        else:
            conn.commit()
            return None
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            pool.putconn(conn)

def setup_database():
    """Ensures the necessary database table exists."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS document_hashes (
        id SERIAL PRIMARY KEY,
        original_hash VARCHAR(64) NOT NULL,
        protected_hash VARCHAR(64) NOT NULL UNIQUE,
        original_filename VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(create_table_query)
    logger.info("Database table 'document_hashes' is ready.")