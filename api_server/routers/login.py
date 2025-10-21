from fastapi import APIRouter, HTTPException, status
from service.login import processor as login_processor
from api_server.schemas.login import SendCodeRequest, AuthRequest  # <- 引用

router = APIRouter(prefix="/api/login", tags=["login"])


@router.post("/send-code", status_code=status.HTTP_201_CREATED)
async def send_code(req: SendCodeRequest):
    try:
        code = await login_processor.send_code(req.email)
        return {"message": "验证码已发送", "email": req.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=503, detail="邮件服务暂不可用")


@router.post("/authenticate", status_code=status.HTTP_200_OK)
async def authenticate(req: AuthRequest):
    result = await login_processor.authenticate(req.email, req.code)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])