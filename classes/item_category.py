from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime

class itemCategory(object):
	__tablename__ = "item_categories"
	id = Column('id', Integer(), primary_key=True, unique=True)
	type_id = Column('type_id', Integer())
	name = Column('name', String(50))
	icon = Column('icon', String())
	button_color = Column('button_color', String(50))
	sort_order = Column('sort_order', Integer())
	added = Column('added', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())

	
	def __init__(self, id, type_id, name, icon, button_color, sort_order, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.id = id
		self.type_id = type_id
		self.name = name
		self.icon = icon
		self.button_color = button_color
		self.sort_order = sort_order
		self.added = added
		self.updated = updated

	def __str__(self):
		return '<itemCategory {}>'.format(self.id)