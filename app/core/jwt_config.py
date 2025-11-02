import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
from app.core.config import JWT_ALGORITHM, JWT_SECRET
from app.database.models import UserDB
from .api_key_and_rate_limiting import api_limit_manage
from app.core.config import JWT_SECRET, JWT_ALGORITHM

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
	
	# checking if user has an active api_key
	# if not, then user won't be able to access api even if he has a valid jwt
	user_id = payload["user_id"]
	api_limit_manage(user_id)

	if not payload:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return payload


""" this decorator is same as get_current_user, 
	but it just checks user role, mainly for admin authentication.
	admin_required will be used instead of get_current_user in admin panel code.
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
			detail="Only admins can access this route.",
			headers={"WWW-Authenticate": "Bearer"},
		)

async def create_jwt(user_id, role):
	access_token = jwt.encode(
		payload={
			"role": role, 
			"user_id" : user_id,
			"type" : "access",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
		}, 
		key=JWT_SECRET, 
		algorithm=JWT_ALGORITHM
	)
		
	refresh_token = jwt.encode(
		payload={
			"role": role, 
			"user_id" : user_id,
			"type" : "refresh",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(minutes=120)).timestamp())
		}, 
		key=JWT_SECRET, 
		algorithm=JWT_ALGORITHM
	)

	return access_token, refresh_token