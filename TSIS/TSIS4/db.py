# db.py — PostgreSQL persistence layer (psycopg2)
# All DB errors are caught and logged so the game runs even without a DB.

import psycopg2
import psycopg2.extras
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _connect():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        connect_timeout=3,
    )


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""

def init_db() -> bool:
    """Create tables if they don't exist. Returns True on success."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()
        return True
    except Exception as exc:
        print(f"[DB] init_db failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Player helpers
# ---------------------------------------------------------------------------

def get_or_create_player(username: str) -> int | None:
    """Return player id, creating a row if necessary."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username "
                    "RETURNING id",
                    (username,),
                )
                row = cur.fetchone()
            conn.commit()
        return row[0] if row else None
    except Exception as exc:
        print(f"[DB] get_or_create_player failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def save_session(player_id: int, score: int, level_reached: int) -> bool:
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached),
                )
            conn.commit()
        return True
    except Exception as exc:
        print(f"[DB] save_session failed: {exc}")
        return False


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever (0 if none)."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(MAX(score), 0) FROM game_sessions "
                    "WHERE player_id = %s",
                    (player_id,),
                )
                row = cur.fetchone()
        return row[0] if row else 0
    except Exception as exc:
        print(f"[DB] get_personal_best failed: {exc}")
        return 0


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top-N rows sorted by score desc."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT p.username,
                           best.score,
                           best.level_reached,
                           best.played_date
                    FROM (
                        SELECT DISTINCT ON (player_id)
                               player_id,
                               score,
                               level_reached,
                               played_at::date AS played_date
                        FROM game_sessions
                        ORDER BY player_id, score DESC
                    ) best
                    JOIN players p ON p.id = best.player_id
                    ORDER BY best.score DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as exc:
        print(f"[DB] get_leaderboard failed: {exc}")
        return []