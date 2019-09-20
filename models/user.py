from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
from services.database import metadata, db_session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import timeago
import random
import string

def randomNumbers(stringLength=6):
	"""Generate a random string of fixed length """
	letters = string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))

class User(object):
	query = db_session.query_property()

	def __init__(self, name, username,password, admin=0, id=None):
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

users = Table('users', metadata,
	Column('username', String(80), unique=True, index=True, nullable=True),
	Column('password', String(100), nullable=True),
	Column('name',String(120)),
	Column('id',String(50),unique=True, primary_key=True),
	Column('admin',Integer()),
	extend_existing=True)
mapper(User, users)