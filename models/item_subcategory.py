from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

class itemSubcategory(object):
	query = db_session.query_property()

	
	def __init__(self, category_id, name, icon, button_color="primary", sort_order=999999, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.category_id = category_id
		self.name = name
		self.icon = icon
		self.button_color = button_color
		self.sort_order = sort_order
		self.added = added
		self.updated = updated

	def __str__(self):
		return '<itemSubcategory {}>'.format(self.id)

	def getCategory(self):
		return itemCategory.query.filter_by(id=self.category_id).first()

	def getType(self):
		return itemType.query.filter_by(id=self.getCategory().type_id).first()

	def getPrice(self):
		return '{:,.2f}'.format(ItemPrice.query.filter_by(item_subcategory=self.id).first().price)

	def getAttributes(self):
		return attr_to_subcategory.query.filter_by(subcategory_id=self.id).all()
		
itemSubcategories = Table('item_subcategories', metadata,
	Column('id', Integer(), primary_key=True, autoincrement=True),
	Column('category_id', Integer()),
	Column('name', String(50)),
	Column('icon', String()),
	Column('sort_order', Integer()),
	Column('button_color', String(50)),
	Column('added', DateTime(), default=datetime.datetime.utcnow()),
	Column('updated', DateTime(), default=datetime.datetime.utcnow()),
	extend_existing=True
)
mapper(itemSubcategory, itemSubcategories)

from models.item_category import itemCategory
from models.item_types import itemType
from models.item_prices import ItemPrice
from models.attr_to_subcategory import attr_to_subcategory