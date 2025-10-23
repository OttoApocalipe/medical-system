from fastapi import APIRouter, HTTPException, Depends
from api_server.schemas.session import (
    SessionsListRequest, CreateSessionRequest,
    SessionsListResponse, CreateSessionResponse
)
from utils.mysql_pool import mysql_user_pool
from api_server.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# 获取用户的所有 sessions
@router.post("/list", response_model=SessionsListResponse)
async def get_sessions(
        request: SessionsListRequest,
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    conn = mysql_user_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                session_uuid AS session_id,
                title,
                created_at,
                updated_at
            FROM sessions
            WHERE user_id = %s
            ORDER BY updated_at DESC
        """, (user_id,))
        sessions = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

    return {
        "meta": {"status": "success"},
        "data": sessions
    }


# 创建 session
@router.post("/new", response_model=CreateSessionResponse)
async def create_session(
        request: CreateSessionRequest,
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    title = request.title or "新对话"
    session_uuid = str(uuid.uuid4())
    conn = mysql_user_pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO sessions (user_id, session_uuid, title)
            VALUES (%s, %s, %s)
        """, (user_id, session_uuid, title))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {e}")
    finally:
        cursor.close()
        conn.close()

    return {
        "meta": {"status": "success"},
        "data": {"session_id": session_uuid, "title": title}
    }

