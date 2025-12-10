# tasks/monthly_payments_checker.py
from sqlalchemy import delete
from datetime import datetime
from app.database.db import get_db, SessionLocal
from app.database import Tasks, Transactions
from app.core.logging import admin_logger

async def make_monthly_payments(): 
	async with SessionLocal() as db:
		date_now = datetime.utcnow() 
		now = date_now.date()
		
		stmt = select(Tasks)
		result = await db.execute(stmt)
		tasks = result.scalars().all()

		count = []

		for task in tasks:
			if task.intended_time == now:
				new_record = Tasks(
					amount = task.amount,
					trx_type = task.trx_type,
					trx_at = task.intended_time,
					wallet_id = task.wallet_id,
					catg_id = task.catg_id,
					user_id = task.user_id,
					description = task.description
				)

				try:
					db.add(new_record)
					task.is_completed = True
					count.append(task.id)
				
				except SQLAlchemyError as e:
					await db.rollback()
					admin_logger.info("An database error occured while completing scheduled tasks.")
					raise HTTPException(
						status_code=500, 
						detail="An Database error occured.")
		
		await db.commit()

		check_completed = len(count)
		admin_logger.info(f"{check_completed} tasks completed at {date_now}.")

async def clean_completed_tasks():
	async with SessionLocal() as db:
		try:
			stmt = delete(Tasks).where(Tasks.is_completed == True)
			await db.execute(stmt)

		except SQLAlchemyError as e:
			await db.rollback()
			admin_logger.info("An database error occured while completing scheduled tasks.")
			raise HTTPException(
				status_code=500, 
				detail="An Database error occured.")
		
		await db.commit()
		date_now = datetime.utcnow() 
		admin_logger.info(f"Completed tasks deleted from db at {date_now}.")
