# transactions.py
from fastapi import (
	APIRouter, HTTPException, status, Depends, Response, Query)
from sqlalchemy import select, desc, exists, func
from sqlalchemy.sql import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, date
from typing import List

# Local Import
from app.database.db import get_db
from app.schemas import (
	NewTrx, APIResponse, UpdateTrx, PaginatedResponse)
from app.core.jwt_config import get_current_user
from app.core.config import API_VERSION
from app.database import Transactions, Wallets
from app.utils import add_to_db, update_to_db

# Router Setup
trx_router = APIRouter(
	prefix=f"{API_VERSION}/transactions",
	dependencies=[Depends(get_current_user)],
	tags=["transactions"])

"""
	What this file contains:-
	[1] Transactions CRUD
		+ Money transfer from one account to another account
	[2] Transaction summary route
"""
@trx_router.post("/new", response_model=APIResponse)
async def new_transactions(
	data: NewTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db), response: Response):

	query_to_validate_sender = await db.execute(
		select(Wallets)
		.where(
			and_(
				Wallets.id == data.wallet_id,
				Wallets.user_id == current_user["user_id"],
				Wallets.amount >= data.amount
		))
	)
	validate_sender = query_to_validate_sender.scalar_one_or_none()

	if not validate_sender:
		raise HTTPException(status_code=404, 
			detail="Wallet not found or not enough balance to complete transaction.")

	if data.trx_type == "transfer":
		query = await db.execute(
			select(Wallets)
			.where(
				and_(
					Wallets.id == data.recipient_wallet_id,
					Wallets.user_id == current_user["user_id"]
				))
		)
		recipient_check = query.scalar_one_or_none()

		if not recipient_check:
			raise HTTPException(status_code=404, 
				detail="The receiver wallet not found.")

	try:
		trx_at_filtered = datetime.strptime(data.trx_at, "%d:%m:%Y").date()

		if data.trx_type == "transfer" and data.recipient_wallet_id is not None:
			expense_record = Transactions(
				amount = data.amount,
				trx_type = "transfer",
				trx_at = trx_at_filtered,
				wallet_id = data.wallet_id,
				catg_id = data.catg_id, # will add a catg for transfer
				user_id = current_user["user_id"]
			)

			income_record = Transactions(
				amount = data.amount,
				trx_type = "transfer",
				trx_at = trx_at_filtered,
				wallet_id = data.recipient_wallet_id,
				catg_id = data.catg_id,
				user_id = current_user["user_id"]
			)

			try:
			    validate_sender.amount = validate_sender.amount - data.amount
			    recipient_check.amount = recipient_check.amount + data.amount
			    db.add(expense_record)
			    db.add(income_record)
			    await db.commit()
			    response.status_code = 201
				return APIResponse(message="Transfer successfull.")
			
			except SQLAlchemyError as e:
			    await db.rollback()
			    raise HTTPException(status_code=500, detail="Transfer failed")

		elif data.trx_type in ["expense", "income"]:
			check_desc = len(data.description)
			if check_desc > 200:
				raise HTTPException(status_code=400, 
					detail="Description too long.")

			new_record = Transactions(
				amount = data.amount,
				trx_type = data.trx_type,
				trx_at = trx_at_filtered,
				wallet_id = data.wallet_id,
				catg_id = data.catg_id,
				user_id = current_user["user_id"],
				description = data.description
			)
			
			return await add_to_db(new_record, response, db)

	except ValueError:
		response.status_code = 400
		return APIResponse(
			status="fail", message="Invalid DateTime format.")

@trx_router.patch("/{id}", response_model=APIResponse)
async def update_transaction(
	id: int, response: Response,
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

	return await update_to_db(existing, response, db)

@trx_router.delete("/{id}", response_model=APIResponse)
async def delete_transaction(
	id: int, response: Response,
	data: UpdateTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(
		select(Transactions).where(
			Transactions.user_id == current_user["user_id"],
			Transactions.id == id)
	)
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

@trx_router.get("/view", response_model=PaginatedResponse)
async def all_transactions(
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	page: int = Query(1, ge=1),
	page_size: int = Query(10, ge=1, le=100),
	response: Response):
	
	# counting total row for the user
	total_result = await db.execute(
		select(func.count())
		.select_from(Transactions)
		.where(Transactions.user_id == current_user["user_id"])
	)
	total = total_result.scalar_one()

	offset = (page - 1) * page_size
	total_pages =  (total + page_size - 1) // page_size

	result = await db.execute(
		select(Transactions)
		.where(Transactions.user_id == current_user["user_id"])
		.order_by(desc(Transactions.amount))
		.offset(offset)
		.limit(page_size)
	)
	transactions = result.scalars().all()

	if not transactions:
		raise HTTPException(
			status_code=404, 
			detail="The user requested data wasn't found in the database.")

	response.status_code = 200
	return PaginatedResponse(
		status="success",
		data=transactions,
		total_pages=total_pages, 
		page=page, page_size=page_size)


# Summary of Transactions
@trx_router.get("/summary/income", response_model=APIResponse)
async def transaction_summary(
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	response: Response):
	
	current_date = date.today()
	if current_date.day not in range(1, 6):
		start_date = date(current_date.year, current_date.month, 1)
	else:
		start_date = current_date

	if current_date.month == 2:
		end_date = start_date + timedelta(days=28)
	else:
		end_date = start_date + timedelta(days=30)
	
	query = await db.execute(
		select(
			Transactions.trx_type,
			func.sum(Transactions.amount).label("Total_Spent"))
		.where(
			and_(
				Transactions.user_id == current_user["user_id"],
				Transactions.trx_at.between(start_date, end_date),
				Transactions.trx_type.in_(['income', 'expense'])
			)
		)
		.group_by(Transactions.trx_type)
	)
	results = query.mappings().all()

	if not results:
		raise HTTPException(
			status_code=404, 
			detail="The users requested data wasn't found in the database.")

	totals = {row['trx_type']: row['Total_Spent'] for row in results}
	
	if totals["income"] < totals["expense"]:
		summary = {
			"comment" : "Your income is less than your expense.",
			"data" : totals
		}
	else:
		summary = {
			"comment" : "You're doing great. Keep growing.",
			"data" : totals
		}

	return APIResponse(
		status="success",
		data=summary)