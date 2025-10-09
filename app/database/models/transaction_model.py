from datetime import datetime
from sqlalchemy import (
	Column, Integer, String, ForeignKey, 
	Boolean, DateTime, CheckConstraint)
from sqlalchemy.orm import relationship

from app.database.db import Base

class Wallets(Base):
	__tablename__ = "wallets"

	__table_args__ = (
		CheckConstraint(
			"wallet_type IN ('cash', 'credit', 'fd', 'bank', 'digital')", 
			name='ck_wallet_type'),
	)

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)

	current_amount = Column(Integer, nullable=False)
	wallet_type = Column(String, nullable=False)

	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(
		"UserDB",
		uselist=False,
		cascade="all, delete-orphan")

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)

class Transactions(Base):
	__tablename__ = "transactions"

	__table_args__ = (
		CheckConstraint(
			"trans_type IN ('income', 'expense', 'transfer')", 
			name='ck_trans_type'),
	)

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Integer, nullable=False)
	trans_type = Column(String, nullable=False) 

	user_id = Column(Integer, ForeignKey('users.id'))
	catg_id = Column(Integer, ForeignKey('categories.id'))
	
	user = relationship(
		"UserDB",
		uselist=False,
		cascade="all, delete-orphan")

	categories = relationship(
		"Categories",
		uselist=False,
		cascade="all, delete-orphan")

	# The User side of datetime, When the transaction happened
	transaction_at = Column(
		DateTime, 
		nullable=False)

	# For the main system datetime, When the transaction was added to db
	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)


class Categories(Base):
	__tablename__ = "categories"

	id = Column(Integer, primary_key=True, index=True)
	
	category = Column(Integer, nullable=False)
	category_normal = Column(
		Integer, 
		nullable=False,
		unique=True)

	transaction = relationship(
		"Transactions",
		uselist=False,
		cascade="all, delete-orphan")

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)