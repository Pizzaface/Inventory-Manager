from flask_sqlalchemy import SQLAlchemy
import timeago
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
import random
from services.database import Base
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
	__tablename__ = "users" 
	username = Column('username', String(80), unique=True)
	password = Column('password', String(100), nullable=True)
	name = Column('name',String(120))
	id = Column('id',String(50),unique=True, primary_key=True)
	admin = Column('admin',Integer())

	def __init__(self , name, username,password, admin=0, id=None):
		if not id == None:
			self.id = id
		else:
			self.id = randomString(6)

		self.username = username
		self.password = password
		self.admin = admin
		self.name = name

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True
 
	def is_anonymous(self):
		return False
 
	def get_id(self):
		return self.id
 
	def __repr__(self):
		return '<User %r>' % (self.username)