from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

class itemType(object):
	query = db_session.query_property()

	
	def __init__(self, name, icon, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.name = name
		self.icon = icon
		self.added = added
		self.updated = updated


	def __str__(self):
		return '<itemType {}>'.format(self.item_id)



itemTypes = Table('item_types', metadata,
	Column('id', Integer(), primary_key=True, unique=True),
	Column('name', String(50)),
	Column('icon', String()),
	Column('added', DateTime(), default=datetime.datetime.utcnow()),
	Column('updated', DateTime(), default=datetime.datetime.utcnow()),
	extend_existing=True
)
mapper(itemType, itemTypes)