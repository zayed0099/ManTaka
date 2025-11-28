from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.database.db import get_db, SessionLocal
from app.core.logging import admin_logger

async def add_to_db(entry):
	async with SessionLocal() as db:
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

async def update_to_db(entry):
	async with SessionLocal() as db:
		try:
			merged = db.merge(entry)
			await db.commit()
			await db.refresh(merged)
			
			response.status_code = 200
			return APIResponse(message="Record successfully updated.")

		except SQLAlchemyError as e:
			await db.rollback()
			admin_logger.error(f"Database error: {str(e)}")
			
			raise HTTPException(
				status_code=500, 
				detail="An Database error occured.")