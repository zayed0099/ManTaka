# admin.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
# Local Import
from app.database.db import get_db
from app.database import Transactions, Categories
from app.schemas import AddCatg
from app.core.jwt_config import admin_required
from app.core.config import API_VERSION
from app.core.logging import admin_logger

admin_router = APIRouter(
	prefix=f"{API_VERSION}/admin",
	dependencies=[Depends(admin_required)],
	tags=["admin"])

# To add category in Category d and update/delete them when needed
@admin_router.post("/category/add")
async def add_category(
	data: AddCatg, current_user: dict = Depends(admin_required),
	db: AsyncSession = Depends(get_db)):
	
	catg_normal = data.category.strip().lower()

	result = await db.execute(
		select(exists().where(Categories.id == catg_normal))
	)
	existing = result.scalar()

	if existing:
		return APIResponse(
			status="unsuccessful",
			message="The category already exists.")

	new_catg = Categories(
		category=data.category,
		category_normal=catg_normal,
	)

	try:
		db.add(new_catg)
		await db.commit()
		await db.refresh(new_catg)
		
		admin_logger.info(f"{data.category} has been added to the category db.")
		return APIResponse(
			status="success",
			message="Category successfully added.")
	
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")
	

@admin_router.patch("/category/{id}")
async def update_category(
	data: AddCatg, current_user: dict = Depends(admin_required),
	db: AsyncSession = Depends(get_db)), id: int:

	result = await db.execute(
		select(exists().where(
			and_(
				Categories.id == id,
				Categories.is_archieved == False
			)
		))
	)
	existing = result.scalars().first()

	if not existing:
		return APIResponse(
			status="unsuccessful",
			message="The category doesn't exist or is archieved.")

	try:
		existing.category = data.category
		existing.category_normal = data.category.strip().lower()
		await db.commit()
		
		admin_logger.info(f"{data.category} has been changed to {existing.category}.")
		return APIResponse(
			status="success",
			message="Category successfully updated.")
	
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@admin_router.put("/category/{id}")
async def archieve_category(
	current_user: dict = Depends(admin_required),
	db: AsyncSession = Depends(get_db)), id: int:

	result = await db.execute(
		select(exists().where(
			and_(
				Categories.id == id,
				Categories.is_archieved == False
			)
		))
	)
	existing = result.scalars().first()

	if not existing:
		return APIResponse(
			status="unsuccessful",
			message="The category doesn't exist.")

	try:
		existing.is_active = False
		await db.commit()
		
		admin_logger.info(f"{existing.category} has been archieved.")
		return APIResponse(
			status="success",
			message="Category successfully archieved.")
	
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@admin_router.delete("/category/{id}")
async def delete_category(
	current_user: dict = Depends(admin_required),
	db: AsyncSession = Depends(get_db)), id: int:

	result = await db.execute(
		select(exists().where(
			and_(
				Categories.id == id,
				Categories.is_archieved == True
			)
		))
	)
	existing = result.scalars().first()

	if not existing:
		return APIResponse(
			status="unsuccessful",
			message="The category doesn't exist or is not archieved.")

	now = datetime.utcnow()
	
	if now - existing.updated_at < timedelta(days=30):
		raise HTTPException(
			status_code=400, 
			detail="The category should be archioeved for minimum 30 days.")

	try:
		await db.delete(existing)
		await db.commit()
		
		admin_logger.info(
			f"{existing.category} has been permanently deleted from the category db.")
		return APIResponse(
			status="success",
			message="Category permanently deleted.")
	
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")
