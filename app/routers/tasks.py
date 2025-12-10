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
from app.database import Transactions, Wallets, Tasks
from app.utils import add_to_db

# Router Setup
tasks_router = APIRouter(
	prefix=f"{API_VERSION}/tasks",
	dependencies=[Depends(get_current_user)],
	tags=["tasks"])

@tasks_router.post("/new", response_model=APIResponse)
async def new_scheduled_transaction(
	data: NewTrx, current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db), response: Response):

	result = await db.execute(
		select(exists().where(
			and_(
				Wallets.id == data.wallet_id,
				Wallets.user_id == current_user["user_id"]
			)
		))
	)
	existing = result.scalar()

	if not existing:
		raise HTTPException(status_code=404, 
			detail="Wallet not found or access denied.")

	
	trx_at_filtered = datetime.strptime(data.trx_at, "%d:%m:%Y").date()
	
	check_desc = len(data.description)
	if check_desc > 200:
		raise HTTPException(status_code=400, 
			detail="Description not found.")

	new_record = Tasks(
		amount = data.amount,
		trx_type = data.trx_type,
		intended_time = trx_at_filtered,
		wallet_id = data.wallet_id,
		catg_id = data.catg_id,
		user_id = current_user["user_id"],
		description = data.description
	)

	return await add_to_db(new_record, response, db)
