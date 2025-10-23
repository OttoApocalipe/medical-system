from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from utils.jwt_utils import verify_token

# 定义令牌提取规则：从Authorization头中提取 [Bearer + 令牌]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/authenticate")    # 前端获取令牌的接口


# 定义授权依赖：验证令牌并返回当前用户(user_id为int，email为str)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    # 验证失败的统一响应
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="令牌无效或已过期，请重新登陆",
        headers={"WWW-Authenticate": "Bearer"},     # OAuth2协议要求, 提示前端用此Bearer模式
    )

    try:
        # 调用jwt_utils验证令牌, 返回解码后的数据{"user_id": int, "email": str}
        user_info = verify_token(token)
        return user_info
    except JWTError as e:
        raise credentials_exception from e

