from datetime import datetime
from sqlalchemy import (
	Column, Integer, String, ForeignKey, 
	Boolean, DateTime, CheckConstraint)
from sqlalchemy.orm import relationship
from app.database.db import Base

class UserDB(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	password = Column(String, nullable=False)
	
	role = Column(String, default="user", nullable=False)
	is_banned = Column(Boolean, default=False, nullable=False)

	currency = Column(String, default="bdt", nullable=False)

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False)

	transactions = relationship(
		"Transactions", 
		back_populates="user_tr",
		uselist=False,
		cascade="all, delete-orphan")

	wallets = relationship(
		"Wallets", 
		back_populates="user_wallet", 
		uselist=False,
		cascade="all, delete-orphan")