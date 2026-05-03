from fastapi import APIRouter, HTTPException, Query
from app.database import get_connection, put_connection
from app.schemas.schemas import StatsResponse, ActivityItem, ActivityListResponse
from typing import List, Optional

router = APIRouter(prefix="/api/dashboard")

@router.get("/stats", response_model=StatsResponse)
def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM users")
        users_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM posts")
        posts_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM comments")
        comments_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM sessions")
        sessions_count = cur.fetchone()[0]

        return {
            "users": users_count,
            "posts": posts_count,
            "comments": comments_count,
            "sessions": sessions_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        put_connection(conn)

@router.get("/recent-activity", response_model=ActivityListResponse)
def recent_activity(
    last_created_at: Optional[str] = None,
    last_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100)
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if last_created_at and last_id:
            query = """
                SELECT id, user_id, action, created_at
                FROM activities
                WHERE (created_at, id) < (%s, %s)
                ORDER BY created_at DESC, id DESC
                LIMIT %s
            """
            cur.execute(query, (last_created_at, last_id, limit))
        else:
            query = """
                SELECT id, user_id, action, created_at
                FROM activities
                ORDER BY created_at DESC, id DESC
                LIMIT %s
            """
            cur.execute(query, (limit,))

        rows = cur.fetchall()

        activities = [
            {
                "id": row[0],
                "user_id": row[1],
                "action": row[2],
                "created_at": row[3].isoformat()
            }
            for row in rows
        ]

        return {"activities": activities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        put_connection(conn)
