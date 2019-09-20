from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

class itemAttribute(object):
	query = db_session.query_property()

	
	def __init__(self, attr_name, attr_values, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		attr_name = attr_name.replace("'", "").replace("\"", "").replace("#", "")
		self.attr_name = attr_name
		self.attr_values = attr_values
		self.added = added
		self.updated = updated

	def __str__(self):
		return '<itemAttribute {}>'.format(self.id)


item_attributes = Table('item_attributes', metadata,
	Column('id', Integer(), primary_key=True, unique=True),
	Column('attr_name', String(50)),
	Column('attr_values', Text()),
	Column('added', DateTime(), default=datetime.datetime.utcnow()),
	Column('updated', DateTime(), default=datetime.datetime.utcnow()),
	extend_existing=True
)
mapper(itemAttribute, item_attributes)