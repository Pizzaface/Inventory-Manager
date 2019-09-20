from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime

class itemType(object):
	__tablename__ = "item_types"
	id = Column('id', Integer(), primary_key=True, unique=True)
	name = Column('name', String(50))
	icon = Column('icon', String())
	added = Column('added', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())

	
	def __init__(self, id, name, icon, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.id = id
		self.name = name
		self.icon = icon
		self.added = added
		self.updated = updated

	def __str__(self):
		return '<itemType {}>'.format(self.item_id)