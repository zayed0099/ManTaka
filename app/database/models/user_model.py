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
	password = Column(String, nullable=True)
	
	is_oauth_login = Column(Boolean, default=False, nullable=False)

	role = Column(String, default="user", nullable=False)
	is_banned = Column(Boolean, default=False, nullable=False)

	currency = Column(String, default="bdt", nullable=False)
	
	
	# For future use
	is_pro_user = Column(Boolean, default=False, nullable=False)

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False
	)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False
	)
	
	# Relationships
	transactions = relationship(
		"Transactions", 
		back_populates="user_tr",
		cascade="all, delete-orphan"
	)

	wallets = relationship(
		"Wallets", 
		back_populates="user_wa", 
		cascade="all, delete-orphan"
	)

	tasks = relationship(
		"Tasks",
		back_populates="task_user",
		cascade="all, delete-orphan"
	)

	notifications = relationship(
		"UserNotifications", 
		back_populates="user_notif", 
		cascade="all, delete-orphan"
	)


class UserNotifications(Base):
	__tablename__ = "user_notifications"

	id = Column(Integer, primary_key=True, index=True)

	notification = Column(Text, nullable=True)
	is_seen = Column(Boolean, default=False, nullable=False)

	created_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		nullable=False
	)
	
	updated_at = Column(
		DateTime, 
		default=datetime.utcnow, 
		onupdate=datetime.utcnow,
		nullable=False
	)

	user_id = Column(Integer,
		ForeignKey('users.id'), index=True)

	user_notif = relationship(
		"UserDB",
		back_populates="notifications",
		cascade="all, delete-orphan")



