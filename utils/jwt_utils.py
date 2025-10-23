from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 读取JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_TOKEN_EXPIRE_HOURS"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    :param data: 载荷数据（包含 user_id 和 email）
    :param expires_delta: 过期时间
    :return: 编码后的 JWT 令牌
    """
    to_encode = data.copy()
    # 设置过期时间
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    # 创建JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证 JWT 访问令牌
    :param token: 访问令牌
    :return: 解码后的 JWT 数据
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise JWTError("令牌已过期")
    except JWTError:
        raise JWTError("无效的令牌")

    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email:
        raise JWTError("令牌数据不完整")
    return {"user_id": int(user_id), "email": email}


