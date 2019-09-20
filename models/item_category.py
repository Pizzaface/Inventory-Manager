from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

class itemCategory(object):
	query = db_session.query_property()

	
	def __init__(self, type_id, name, icon, button_color="primary", sort_order=999999, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.type_id = type_id
		self.name = name
		self.icon = icon
		self.button_color = button_color
		self.sort_order = sort_order
		self.added = added
		self.updated = updated

	def getType(self):
		return itemType.query.filter_by(id=self.type_id).first()

	def __str__(self):
		return '<itemCategory {}>'.format(self.id)



itemCategories = Table('item_categories', metadata,
	Column('id', Integer(), primary_key=True, unique=True),
	Column('type_id', Integer()),
	Column('name', String(50)),
	Column('icon', String()),
	Column('button_color', String(50)),
	Column('sort_order', Integer()),
	Column('added', DateTime(), default=datetime.datetime.utcnow()),
	Column('updated', DateTime(), default=datetime.datetime.utcnow()),
	extend_existing=True
)
mapper(itemCategory, itemCategories)

from models.item_types import itemType