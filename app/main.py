import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import transactions, admin, visuals, tasks
from routers.auth import credentials_auth, social_auth

from app.database.db import init_db
from app.core.config import SECRET_KEY
from app.core.scheduler import start_scheduler

app = FastAPI()

# Create tables at startup + APScheduler Startup
@app.on_event("startup")
async def on_startup():
	await init_db()
	admin_logger.info("Server started.")
	start_scheduler(app)


# Middleware 
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Register routers
app.include_router(transactions.trx_router)
app.include_router(admin.admin_router)
app.include_router(social_auth.social_auth_router)
app.include_router(credentials_auth.auth_router)
app.include_router(visuals.visual_router)
app.include_router(tasks.tasks_router)

# App Shutdown settings
@app.on_event("shutdown")
def shutdown_event():
	admin_logger.info("Server being shutdown.")

if __name__ == "__main__":
	uvicorn.run(
		"main:app", 
		host="0.0.0.0", 
		port=8000, 
		log_level="info",
		reload=True
	)