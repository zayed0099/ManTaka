# tasks/manage_notifications.py
from sqlalchemy import delete
from datetime import datetime, date
from app.database.db import get_db, SessionLocal
from app.database import Transactions, UserNotifications
from app.core.logging import admin_logger

async def add_to_notif_db(user_id, message):
	new_entry = UserNotifications(
		notification=message, user_id=user_id, is_seen=False)

	try:
		db.add(new_entry)
		await db.commit()
	except SQLAlchemyError as e:
		await db.rollback()
		admin_logger.info("A database error occured while adding new data.")

async def monthly_summary_notifier():
	async with SessionLocal() as db:
		today = date.today()
		mnth = today.month - 1
		start_date = date(today.year, mnth, 1)
		end_date = date(today.year, mnth, 30)

		query = await db.execute(
			select(
				Transactions.user_id,
				func.sum(Transactions.amount)
					.filter(Transactions.trx_type == "income")
					.label("income"),
				func.sum(Transactions.amount)
					.filter(Transactions.trx_type == "expense")
					.label("expense"),
			)
			.where(
				and_(
					Transactions.trx_at.between(start_date, end_date),
					Transactions.trx_type.in_(['income', 'expense'])
				)
			)
			.group_by(Transactions.user_id)
		)
		results = query.mappings().all()

		notif_counter = 0

		notif_dict = {
			"income_bigger" : "You're managing your expenses perfetcly. Keep it up. You are earning more than you're spending. Don't forget to save and invest properly.",
			"expense_bigger" : "Ouch! You're in deepe water. You're in debt right now. Please try to redce expense..",
			"little_difference" : "You're doing well. But you should track your expenses more strictly as your income and expenses are nearly the same. You don't have enough to save and invest." 
		}

		if results:
			for r in results:
				income = r["income"]
				expense = r["expense"]

				if income is None or expense is None:
					continue

				notif_text = None

				if income > expense:
					if abs(income - expense) >= 5000:
						notif_text = notif_dict["income_bigger"]

					elif abs(income - expense) <= 1000:
						notif_text = notif_dict["little_difference"]
		
				elif income < expense:	
						notif_text = notif_dict["expense_bigger"]

				if notif_text is not None:
					await add_to_notif_db(r["user_id"], notif_text)
					notif_counter += 1

		now = datetime.utcnow()
		admin_logger.info(f"Total : {notif_counter} notifications have been added to notif db at {now}.")
		





