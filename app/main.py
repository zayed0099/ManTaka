from fastapi import FastAPI
from routers import auth, transactions, admin
from db import init_db

app = FastAPI()

# Create tables at startup
@app.on_event("startup")
async def on_startup():
    await init_db()

# Register routers
app.include_router(auth.auth_router)
app.include_router(transactions.trx_router)
app.include_router(admin.admin_router)