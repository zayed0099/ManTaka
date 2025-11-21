import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from app.database.db import get_db
from app.core.logging import admin_logger
from app.tasks.monthly_payments import make_monthly_payments, clean_completed_tasks

def start_scheduler(app: FastAPI):
	scheduler = AsyncIOScheduler()
	
	scheduler.add_job(
		make_monthly_payments,
		CronTrigger(day=5 ,hour=10, minute=30),
		id="monthly_payments_maker",
		replace_existing=True
	)

	scheduler.add_job(
		clean_completed_tasks,
		CronTrigger(hour=11, minute=00),
		id="completed_tasks_deleter",
		replace_existing=True
	)

	scheduler.start()
	admin_logger.info("Server started and scheduler initialized.")

