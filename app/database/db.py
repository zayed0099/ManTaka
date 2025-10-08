from sqlalchemy.ext.asyncio import (
	create_async_engine,
	async_sessionmaker,
	AsyncSession)
from sqlalchemy.orm import declarative_base
from app.core.config import DATABASE_NAME

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(basedir, DATABASE_NAME)}"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(
	engine,
	expire_on_commit=False,
	class_=AsyncSession,
)
Base = declarative_base()

async def init_db():
	import models
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

# Dependency for DB session
async def get_db():
	async with SessionLocal() as session:
		yield session