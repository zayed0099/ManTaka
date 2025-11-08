# visuals.py
import calendar
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response
from sqlalchemy import select, desc, extract
from sqlalchemy.sql import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime, date, timedelta
import pygal

# Local Import
from app.database.db import get_db
from app.core.jwt_config import get_current_user
from app.core.config import API_VERSION
from app.database import Transactions, Wallets, Categories
from app.schemas import APIResponse

# Router Setup
visual_router = APIRouter(
	prefix=f"{API_VERSION}/visuals",
	dependencies=[Depends(get_current_user)],
	tags=["visuals"])

@visual_router.get("/bar/income-expense")
async def income_expense_bar(
	start_year: int = datetime.now().year,
	end_year: int = datetime.now().year, 
	start_month: int = 1, 
	end_month: int = 6,
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	):

	start_date = date(start_year, start_month, 1)
	end_date = date(end_year, end_month, 28 if end_month == 2 else 30)
	difference = abs(end_date - start_date)

	if not timedelta(days=180) <= difference <= timedelta(days=186):
		raise HTTPException(
			status_code=400, 
			detail="There should be a 6 month difference between start and end date.")

	result = await db.execute(
		select(Transactions)
		.where(
			and_(
				Transactions.user_id == current_user["user_id"],
				Transactions.trx_at.between(start_date, end_date)
				)
			)
		)
	transactions = result.scalars().all()
	
	incomes = []
	expenses = []
	
	def filter_data_to_list(object_, start, end):
		temp_income = []
		temp_expense = []

		for row in object_:
			if start <= row.trx_at <= end:
				if row.trx_type == "expense":
					temp_expense.append(row.amount)
				elif row.trx_type == "income":
					temp_income.append(row.amount)
		
		total_income = sum(temp_income)
		incomes.append(total_income)

		total_expense = sum(temp_expense)
		expenses.append(total_expense)

	months = []
	current = start_date

	while current <= end_date:
		months.append(f"{calendar.month_name[current.month]}, {current.year}")
		
		if current.month == 12:
			current = date(current.year + 1, 1, 1)
		else:
			current = date(current.year, current.month + 1, 1)


	bar_chart = pygal.Bar()
	bar_chart.title = (
		f'Income and Expenditure comparison graph between {start_month}/{year} to {end_month}/{year}.')
	bar_chart.x_labels = months
	
	counter = False
	for month in range(start_month, end_month+1):
		start = start_date if not counter else end
		end = end_date if not counter else start + timedelta(days=30)
		
		filter_data_to_list(transactions, start, end) 
		counter = True

	bar_chart.add("Income", incomes)
	bar_chart.add("Expense", expenses)
	
	income_expense_bar = bar_chart.render()
	return Response(content=income_expense_bar, media_type="image/svg+xml")

@visual_router.get("/bar/expense")
async def expense_six_months(
	start_year: int = datetime.now().year,
	end_year: int = datetime.now().year, 
	start_month: int = 1, 
	end_month: int = 6,
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	):
	
	start_date = date(start_year, start_month, 1)
	end_date = date(end_year, end_month, 28 if end_month == 2 else 30)
	difference = abs(end_date - start_date)

	if not timedelta(days=180) <= difference <= timedelta(days=186):
		raise HTTPException(
			status_code=400, 
			detail="There should be a 6 month difference between start and end date.")

	query = await db.execute(
		select(
			func.extract("year", Transactions.trx_at).label("year"),
			func.extract("month", Transactions.trx_at).label("month"),
			func.sum(Transactions.amount).label("total")
		)
		.where(
			and_(
				Transactions.user_id == current_user["user_id"],
				Transactions.trx_type == "expense",
				Transactions.trx_at.between(start_date, end_date)
				)
			)
		.group_by("year", "month")
		.order_by("year", "month")
	)
	transactions = query.mappings().all()

	bar_chart = pygal.HorizontalBar()
	bar_chart.title = (
		'Expense between {start_month}/{start_year} to {end_month}/{end_year}'
	)
	
	for row in transactions:
		month_name = calendar.month_name[int(row['month'])]
		bar_chart.add(
			f"{month_name}, {int(row["year"])}", 
			row["total"]
		)

	expense_six_months_bar = bar_chart.render()
	return Response(content=expense_six_months_bar, media_type="image/svg+xml")

@visual_router.get("/pie/monthly-summary")
async def monthly_summary_pie(
	year: int = datetime.now().year, 
	month: int = 1, 
	current_user: dict = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
	):

	start_date = date(year, month, 1)
	end_date = date(year, month, 28 if month == 2 else 30)

	query = await db.execute(
		select(
			Categories.category,
			func.sum(Transactions.amount).label("total_spent")
		)
		.join(Categories, Transactions.catg_id == Categories.id)
		.where(
			and_(
				Transactions.user_id == current_user["user_id"],
				Transactions.trx_type == "expense",
				Transactions.trx_at.between(start_date, end_date)
				)
			)
		.group_by(Categories.id)
	)
	category_details = query.mappings().all()

	pie_chart = pygal.Pie(inner_radius=.4)
	pie_chart.title = 'Expense in {month}/{year} grouped by category.'
	
	for row in category_details:
		pie_chart.add(row["category"], row["total_spent"])

	monthly_summary_pie = pie_chart.render()
	return Response(content=monthly_summary_pie, media_type="image/svg+xml")
