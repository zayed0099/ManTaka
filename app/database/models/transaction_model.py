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
	user = relationship("UserDB")

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
	user = relationship("UserDB")

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)