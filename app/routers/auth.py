from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
	
# Local Import
from app.database.db import get_db
from app.schemas.auth_schemas import TokenResponse, UserCreate, UserLogin
from app.core.jwt_config import get_current_user
from app.core.config import (
	JWT_SECRET, 
	JWT_ALGORITHM, 
	API_VERSION)
from app.database import UserDB

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

@auth_router.post("/login", response_model=TokenResponse)
async def User_Login(data: UserLogin, db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(UserDB).where(UserDB.username == data.username))
	existing = result.scalars().first()
	
	if not existing:
		raise HTTPException(status_code=400, detail="User not found.")
		
	try:
		ph.verify(existing.password, data.password)

		access_payload = {
			"role": existing.role, 
			"user_id" : existing.id,
			"type" : "access",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
		}

		refresh_payload = {
			"role": existing.role, 
			"user_id" : existing.id,
			"type" : "refresh",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(days=3)).timestamp())
		}

		access_token = jwt.encode(
			payload=access_payload, 
			key=JWT_SECRET, 
			algorithm=JWT_ALGORITHM)
		
		refresh_token = jwt.encode(
			payload=refresh_payload, 
			key=JWT_SECRET, 
			algorithm=JWT_ALGORITHM)

		return TokenResponse(
			access_token=access_token,
			refresh_token=refresh_token)
	
	except VerifyMismatchError:
		raise HTTPException(status_code=400, detail="Invalid Username or Password")
