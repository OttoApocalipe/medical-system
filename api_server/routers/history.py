from fastapi import APIRouter, HTTPException, Depends, status
from api_server.schemas.history import HistoryRequest, HistoryResponse
from api_server.dependencies import get_current_user
from service.history import processor as history_processor


router = APIRouter(prefix="/api", tags=["history"])


@router.post("/history", response_model=HistoryResponse)
async def get_history(
        request: HistoryRequest,
        current_user: dict = Depends(get_current_user)
):
    # 从鉴权依赖中获取user_id
    user_id = current_user["user_id"]
    # 验证会话是否属于当前用户
    service_result =await history_processor.get_history(user_id, request.session_id)

    # 根据service结果响应
    if not service_result["success"]:
        # 区分403（权限问题）和500（服务器问题）
        if "会话不属于当前用户" in service_result["message"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=service_result["message"])
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=service_result["message"])

    # 响应成功
    return {
        "meta": {
            "status": service_result["status"],
            "message": service_result["message"]
        },
        "data": service_result["data"]
    }
