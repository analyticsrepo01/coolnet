"""Async-friendly BigQuery client for CoolNest."""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from functools import partial

from google.cloud import bigquery
from config import PROJECT_ID, BQ_DATASET

_bq = None

def _get_client():
    global _bq
    if _bq is None:
        _bq = bigquery.Client(project=PROJECT_ID)
    return _bq


def _run_sync(fn, *args, **kwargs):
    """Run a sync BQ call in the default executor."""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, partial(fn, *args, **kwargs))


# ── Session ops ─────────────────────────────────────────────────────────────

async def log_session_start(session_id: str, user_id: str, agent_id: str):
    def _insert():
        table = f"{PROJECT_ID}.{BQ_DATASET}.sessions"
        rows = [{
            "session_id": session_id,
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ended_at": None,
            "agents_used": [agent_id],
            "outcome": "active",
            "satisfaction": None,
        }]
        _get_client().insert_rows_json(table, rows)
    await _run_sync(_insert)


async def log_session_end(session_id: str, outcome: str = "resolved"):
    def _update():
        sql = f"""
            UPDATE `{PROJECT_ID}.{BQ_DATASET}.sessions`
            SET ended_at = @ts, outcome = @outcome
            WHERE session_id = @sid
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("ts", "STRING", datetime.now(timezone.utc).isoformat()),
            bigquery.ScalarQueryParameter("outcome", "STRING", outcome),
            bigquery.ScalarQueryParameter("sid", "STRING", session_id),
        ])
        _get_client().query(sql, job_config=job_config).result()
    try:
        await _run_sync(_update)
    except Exception:
        pass  # non-critical


# ── Conversation ops ─────────────────────────────────────────────────────────

async def log_message(session_id: str, user_id: str, speaker: str, agent_id: str, text: str, msg_type: str = "audio_transcript"):
    def _insert():
        table = f"{PROJECT_ID}.{BQ_DATASET}.conversations"
        rows = [{
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speaker": speaker,
            "agent_id": agent_id,
            "message": text,
            "message_type": msg_type,
        }]
        _get_client().insert_rows_json(table, rows)
    try:
        await _run_sync(_insert)
    except Exception:
        pass


# ── Handoff ops ─────────────────────────────────────────────────────────────

async def log_handoff(session_id: str, from_agent: str, to_agent: str, reason: str):
    def _insert():
        table = f"{PROJECT_ID}.{BQ_DATASET}.agent_handoffs"
        rows = [{
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
        _get_client().insert_rows_json(table, rows)
    try:
        await _run_sync(_insert)
    except Exception:
        pass


# ── User ops ─────────────────────────────────────────────────────────────────

async def get_user_profile(user_id: str) -> dict | None:
    def _query():
        sql = f"SELECT * FROM `{PROJECT_ID}.{BQ_DATASET}.users` WHERE user_id = @uid LIMIT 1"
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("uid", "STRING", user_id),
        ])
        rows = list(_get_client().query(sql, job_config=job_config).result())
        return dict(rows[0]) if rows else None
    try:
        return await _run_sync(_query)
    except Exception:
        return None


async def get_user_orders(user_id: str) -> list:
    def _query():
        sql = f"""
            SELECT o.order_id, o.sku, p.name as product_name, o.price_paid,
                   o.order_date, o.status
            FROM `{PROJECT_ID}.{BQ_DATASET}.orders` o
            JOIN `{PROJECT_ID}.{BQ_DATASET}.products` p ON o.sku = p.sku
            WHERE o.user_id = @uid
            ORDER BY o.order_date DESC
            LIMIT 5
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("uid", "STRING", user_id),
        ])
        return [dict(r) for r in _get_client().query(sql, job_config=job_config).result()]
    try:
        return await _run_sync(_query)
    except Exception:
        return []


async def get_user_context(user_id: str) -> dict:
    """Fetch recent session summary for context injection into system prompt."""
    def _query():
        sql = f"""
            SELECT message, speaker, agent_id, timestamp
            FROM `{PROJECT_ID}.{BQ_DATASET}.conversations`
            WHERE user_id = @uid
            ORDER BY timestamp DESC
            LIMIT 20
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("uid", "STRING", user_id),
        ])
        return [dict(r) for r in _get_client().query(sql, job_config=job_config).result()]
    try:
        rows = await _run_sync(_query)
        if rows:
            lines = [f"{r['speaker']} ({r['agent_id']}): {r['message']}" for r in reversed(rows)]
            return {"session_summary": "Recent history:\n" + "\n".join(lines)}
        return {}
    except Exception:
        return {}


async def upsert_user(user_id: str, name: str, email: str, loyalty_tier: str):
    """Insert or update a user record."""
    def _run():
        sql = f"""
            MERGE `{PROJECT_ID}.{BQ_DATASET}.users` T
            USING (SELECT @uid AS user_id) S ON T.user_id = S.user_id
            WHEN MATCHED THEN UPDATE SET updated_at = @ts
            WHEN NOT MATCHED THEN INSERT (user_id, name, email, loyalty_tier, total_spend, created_at, updated_at)
              VALUES (@uid, @name, @email, @tier, 0.0, @ts, @ts)
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("uid", "STRING", user_id),
            bigquery.ScalarQueryParameter("name", "STRING", name),
            bigquery.ScalarQueryParameter("email", "STRING", email),
            bigquery.ScalarQueryParameter("tier", "STRING", loyalty_tier),
            bigquery.ScalarQueryParameter("ts", "STRING", datetime.now(timezone.utc).isoformat()),
        ])
        _get_client().query(sql, job_config=job_config).result()
    try:
        await _run_sync(_run)
    except Exception:
        pass
