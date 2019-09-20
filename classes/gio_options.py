from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
import timeago

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))


class GioOption(object):
	__tablename__ = "gio_options"
	id = Column('id', Integer(), primary_key=True, unique=True)
	meta_key = Column('option_key', Text())
	meta_value = Column('option_value', Text())
	created = Column('created', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())

	
	def __init__(self, id, option_key, option_value, created, updated):
		self.id = item_id
		self.option_key = meta_key
		self.option_value = meta_value
		self.created = created
		self.updated = updated

	def __str__(self):
		return '<gioOption {}>'.format(self.item_id)