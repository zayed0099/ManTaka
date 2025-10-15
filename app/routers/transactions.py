# transactions.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.future import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List
# Local Import
from app.database.db import get_db
from app.schemas import (
	NewTrx, APIResponse, UpdateTrx)
from app.core.jwt_config import get_current_user
from app.core.config import API_VERSION
from app.database import Transactions, Wallets

# Router Setup
trx_router = APIRouter(
	prefix=f"{API_VERSION}/transactions",
	dependencies=[Depends(get_current_user)],
	tags=["transactions"])

@trx_router.post("/new")
async def new_transactions(
	data: NewTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(
		select(exists().where(Wallets.id == NewTrx.wallet_id))
	)
	existing = result.scalar()

	if not existing:
		raise HTTPException(status_code=404, 
			detail="No wallet found for the wallet id.")

	new_record = Transactions(
		amount = data.amount,
		trx_type = data.trx_type,
		trx_at = data.trx_at,
		wallet_id = data.wallet_id,
		catg_id = data.catg_id,
		user_id = current_user["user_id"]
	)

	try:
		db.add(new_record)
		await db.commit()
		await db.refresh(new_record)
		return APIResponse(
			status="success",
			message="Record successfully added.")
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@trx_router.patch("/update/{id}")
async def update_transaction(
	id: int,
	data: UpdateTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(select(Transactions).where(
		Transactions.user_id == current_user["user_id"],
		Transactions.id == id))
	existing = result.scalars().first()

	if not existing:
		raise HTTPException(status_code=404, 
			detail="No transaction found for the provided Trx id.")

	if data.amount is not None:
		existing.amount = data.amount

	if data.trx_type is not None:
		existing.trx_type = data.trx_type

	if data.trx_at is not None:
		existing.trx_at = data.trx_at

	if data.wallet_id is not None:
		existing.wallet_id = data.wallet_id

	if data.catg_id is not None:
		existing.catg_id = data.catg_id

	try:
		db.add(new_record)
		await db.commit()
		await db.refresh(new_record)
		return APIResponse(
			status="success",
			message="Record successfully deleted.")
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@trx_router.delete("/update/{id}")
async def delete_transaction(
	id: int,
	data: UpdateTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(select(Transactions).where(
		Transactions.user_id == current_user["user_id"],
		Transactions.id == id))
	existing = result.scalars().first()

	if not existing:
		raise HTTPException(status_code=404, 
			detail="No transaction found for the provided Trx id.")

	try:
		await db.delete(existing)
		await db.commit()
		return APIResponse(
			status="success",
			message="Record successfully updated.")
	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@trx_router.get("/all")
async def all_transactions(
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(select(Transactions).where(
		Transactions.user_id == current_user["user_id"],
		Transactions.id == id))
	all_trx = result.scalars().all()

	return APIResponse(
		status="success",
		data=all_trx)

@trx_router.