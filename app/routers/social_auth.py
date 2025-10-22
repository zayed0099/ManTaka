import secrets, string
from fastapi import FastAPI, Request, Depends, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.jwt_config import create_jwt
from app.core.config import (
	GOOGLE_CLIENT_ID, 
	GOOGLE_CLIENT_SECRET, 
	GOOGLE_REDIRECT_URI)
from app.database import UserDB
from app.database.db import get_db
from app.schemas.auth_schemas import TokenResponse

oauth = OAuth()

oauth.register(
	name="google",
	client_id=GOOGLE_CLIENT_ID,
	client_secret=GOOGLE_CLIENT_SECRET,
	access_token_url="https://oauth2.googleapis.com/token",
	access_token_params=None,
	authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
	authorize_params=None,
	api_base_url="https://www.googleapis.com/oauth2/v2/",
	client_kwargs={'scope': 'openid email profile'}
)

social_auth_router = APIRouter(
	prefix="/auth",
	tags=["auth"])

@social_auth_router.get("/login")
async def google_login(request: Request):
	redirect_url = GOOGLE_REDIRECT_URI
	return await oauth.google.authorize_redirect(request, redirect_url)

@social_auth_router.get("/callback", response_model=TokenResponse)
async def auth_callback(
	request: Request,
	db: AsyncSession = Depends(get_db)):

	token = await oauth.google.authorize_access_token(request)
	user_info = await oauth.google.parse_id_token(request, token)

	email = user_info.get("email")

	result = await db.execute(select(UserDB).where(UserDB.email == email))
	existing = result.scalars().first()

	# Random username generation
	# User can change the username later from his profile
	characters = string.ascii_letters + string.digits  # a-z + A-Z + 0-9
	username = ''.join(secrets.choice(characters) for _ in range(6))

	if existing:
		raise HTTPException(status_code=400, detail="User already exists.")

	new_user_entry = UserDB(
		username=username,
		email=email,
		is_oauth_login=True
	)

	try:
		db.add(new_user_entry)
		await db.commit()
		await db.refresh(new_user_entry)
		
		access_token, refresh_token = await create_jwt(
			new_user_entry.id, new_user_entry.role)
		
		return TokenResponse(
			access_token=access_token,
			refresh_token=refresh_token) 
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail="Database error")