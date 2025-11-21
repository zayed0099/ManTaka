from datetime import datetime
from sqlalchemy import (
	Column, Integer, Text, String, ForeignKey, 
	Boolean, DateTime, CheckConstraint)
from sqlalchemy.orm import relationship, backref
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
	description = Column(Text, nullable=True)

	user_id = Column(Integer,
		ForeignKey('users.id'), index=True)
	
	# Relationships
	user_wa = relationship(
		"UserDB",
		back_populates="wallets",
		cascade="all, delete-orphan")

	tr_wallet = relationship(
		"Transactions",
		back_populates="wallet_tr",
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
			"trx_type IN ('income', 'expense', 'transfer')", 
			name='ck_trans_type'),
	)

	id = Column(Integer, primary_key=True, index=True)
	amount = Column(Integer, nullable=False)
	trx_type = Column(String, nullable=False) 

	# Foreign Keys
	user_id = Column(Integer, 
		ForeignKey('users.id'), index=True)
	
	catg_id = Column(Integer, 
		ForeignKey('categories.id'), index=True)

	wallet_id = Column(Integer, 
		ForeignKey('wallets.id'), index=True)

	# The User side of datetime, When the transaction happened
	trx_at = Column(
		DateTime, 
		nullable=False)

	# Db side of datetime to track when data was added to/updated at db
	created_at_db = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at_db = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)

	# Relationships
	user_tr = relationship(
		"UserDB",
		back_populates="transactions",
		cascade="all, delete-orphan")

	categories_tr = relationship(
		"Categories",
		back_populates="transaction",
		cascade="all, delete-orphan")

	wallet_tr = relationship(
		"Wallets",
		back_populates="tr_wallet",
		cascade="all, delete-orphan")


class Categories(Base):
	__tablename__ = "categories"

	id = Column(Integer, primary_key=True, index=True)
	
	category = Column(String, nullable=False)
	category_normal = Column(
		String,
		nullable=False,
		index=True,
		unique=True)

	is_archieved = Column(Boolean, default=False, nullable=False)
	
	# For future use. To add categories by user in future
	user_id = Column(Integer, 
		ForeignKey('users.id'), nullable=True)
	
	transaction = relationship(
		"Transactions",
		back_populates="categories_tr",
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