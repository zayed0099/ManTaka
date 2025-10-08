from fastapi import FastAPI
from routers import auth, habits
from db import init_db

app = FastAPI()

# Create tables at startup
@app.on_event("startup")
async def on_startup():
    await init_db()

# Register routers
app.include_router(auth.auth_router)