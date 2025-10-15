import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
from app.core.config import JWT_ALGORITHM, JWT_SECRET
from app.database.models import UserDB

security = HTTPBearer()

def decode_jwt(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(security)):
    token = cred.credentials
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

    """
    this decorator is same as get_current_user 
    but it just checks user role, mainly for admin authentication.
    admin_required will be used instead of get_current_user
    in admin panel code 
    """
async def admin_required(cred: HTTPAuthorizationCredentials = Depends(security)):
    token = cred.credentials
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = await db.execute(
        select(exists().where(
            and_(
                UserDB.id == payload["user_id"],
                UserDB.role == "admin"
            )
        ))
    )
    record_exists = query.scalar()

    if record_exists:
        return payload

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin only route. Only admins can access.",
            headers={"WWW-Authenticate": "Bearer"},
        )

