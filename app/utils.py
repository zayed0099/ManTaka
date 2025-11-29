from fastapi import HTTPException, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db, SessionLocal
from app.core.logging import admin_logger
from app.schemas import APIResponse

async def add_to_db(entry, response: Response, db: AsyncSession):
	try:
		db.add(entry)
		await db.commit()
		await db.refresh(entry)
		
		response.status_code = 201
		return APIResponse(message="Record successfully added.")

	except SQLAlchemyError as e:
		await db.rollback()
		admin_logger.error(f"Database error: {str(e)}")
		
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

async def update_to_db(entry, response: Response, db: AsyncSession):
	try:
		await db.commit()
		await db.refresh(entry)
		
		response.status_code = 200
		return APIResponse(message="Record successfully updated.")

	except SQLAlchemyError as e:
		await db.rollback()
		admin_logger.error(f"Database error: {str(e)}")
		
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")