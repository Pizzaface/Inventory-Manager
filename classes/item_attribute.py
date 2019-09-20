from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime

class itemAttribute(object):
	__tablename__ = "item_attributes"
	id = Column('id', Integer(), primary_key=True, unique=True)
	attr_name = Column('attr_name', String(50))
	attr_values = Column('attr_values', Text())
	added = Column('added', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())

	
	def __init__(self, attr_name, attr_values, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.attr_name = attr_name
		self.attr_values = attr_values
		self.added = added
		self.updated = updated

	def __str__(self):
		return '<itemAttribute {}>'.format(self.id)