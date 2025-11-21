from datetime import datetime
from sqlalchemy import (
	Column, Integer, Text, String, ForeignKey, 
	Boolean, DateTime, CheckConstraint)
from sqlalchemy.orm import relationship, backref
from app.database.db import Base

class Tasks(Base):
	__tablename__ = "tasks"
	
	__table_args__ = (
		CheckConstraint(
			"trx_type IN ('income', 'expense', 'transfer')", 
			name='ck_trans_type_tasks'),
	)

	id = Column(Integer, primary_key=True, index=True)
	
	amount = Column(Integer, nullable=False)
	trx_type = Column(String, nullable=False)
	description = Column(Text, nullable=True)
	
	catg_id = Column(Integer, nullable=False)
	user_id = Column(Integer, ForeignKey('users.id'), index=True)
	wallet_id = Column(Integer, nullable=False)

	intended_time = Column(DateTime, nullable=False)
	is_completed = Column(Boolean, default=False, nullable=False)

	# Relationships
	task_user = relationship(
		"UserDB",
		back_populates="tasks",
		cascade="all, delete-orphan"
	)

	# Database Side data
	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)