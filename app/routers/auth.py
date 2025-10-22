from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
import secrets, string

# Local Import
from app.database.db import get_db
from app.schemas.auth_schemas import TokenResponse, UserCreate, UserLogin
from app.core.jwt_config import get_current_user, create_jwt
from app.core.config import API_VERSION
from app.database import UserDB
from app.core.api_key_and_rate_limiting import api_key_set

# Router Setup
auth_router = APIRouter(
	prefix=f"{API_VERSION}/auth", 
	tags=["auth"])

# Argon2 Password Hasher
ph = PasswordHasher()

@auth_router.post("/signup")
async def new_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(UserDB).where(UserDB.username == data.username))
	existing = result.scalars().first()

	if existing:
		raise HTTPException(status_code=400, detail="Username already exists")
		
	hashed_password = ph.hash(data.password)

	db_item = UserDB(
			username=data.username,
			password=hashed_password,
			email=data.email)

	try:
		db.add(db_item)
		await db.commit()
		await db.refresh(db_item)
		return {"message" : "Account Creation Successful. Head to /login to use account."}, 201
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail="Database error")

@auth_router.post("/login/cred", response_model=TokenResponse)
async def User_Login(data: UserLogin, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(UserDB).where(UserDB.username == data.username))
	existing = result.scalars().first()
	
	if not existing:
		raise HTTPException(status_code=400, detail="User not found.")
		
	try:
		ph.verify(existing.password, data.password)

		access_token, refresh_token = await create_jwt(existing.id, existing.role)

		# Generating API key
		characters = string.ascii_letters + string.digits  # a-z + A-Z + 0-9
		api_key = ''.join(secrets.choice(characters) for _ in range(8))
		
		# Setting Api key for limit
		api_key_set(api_key, existing.id, 200, 86400)

		return TokenResponse(
			access_token=access_token,
			refresh_token=refresh_token)
	
	except VerifyMismatchError:
		raise HTTPException(status_code=400, detail="Invalid Username or Password")
