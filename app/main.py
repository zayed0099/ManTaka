import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import (
	auth, transactions, admin, social_auth)
from db import init_db
from app.core.config import SECRET_KEY

app = FastAPI()

# Create tables at startup
@app.on_event("startup")
async def on_startup():
	await init_db()

# Middleware 
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Register routers
app.include_router(auth.auth_router)
app.include_router(transactions.trx_router)
app.include_router(admin.admin_router)
app.include_router(social_auth.social_auth_router)

if __name__ == "__main__":
	uvicorn.run(
		"main:app", 
		host="0.0.0.0", 
		port=8000, 
		log_level="info",
		reload=True
	)