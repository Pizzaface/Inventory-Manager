from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper
from models.item_prices import ItemPrice
import timeago
from models.item_category import itemCategory
from models.item_subcategory import itemSubcategory
from models.item_types import itemType
from models.attr_to_subcategory import attr_to_subcategory
import json

class Item(object):
	query = db_session.query_property()

	
	def __init__(self, item_id, item_type, category, subcategory, entered_by, removed_by=None, item_attributes="{}", unsold=0, price=None, tag_color=None, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.item_id = item_id
		self.type = item_type
		self.category = category
		self.subcategory = subcategory
		self.entered_by = entered_by
		self.removed_by = removed_by

		original_price = ItemPrice.query.filter_by(item_type=item_type, item_category=category, item_subcategory=subcategory).first().price

		print(item_attributes)
		if not item_attributes == "{}":
			for attr in itemSubcategory.query.filter_by(id=self.subcategory).first().getAttributes():
				if not type(item_attributes) is dict:
					item_attributes = json.loads(item_attributes)
					
				if attr.getAttribute().attr_name.replace(" ", "_") in item_attributes.keys():
					attr_value = item_attributes[attr.getAttribute().attr_name.replace(" ", "_")]
					original_price += float(json.loads(attr.getAttribute().attr_values)[attr_value][1:])

		self.price = original_price
		self.item_attributes = json.dumps(item_attributes)
		self.tag_color = tag_color
		self.added = added
		self.unsold = 0
		self.updated = updated


	def __str__(self):
		return '<item {}>'.format(self.item_id)

	def as_dict(self):
		return {
			"item_id": self.item_id,
			"price": self.price,
			"tag_color": self.tag_color
		}

	def getTypeName(self):
		return itemType.query.filter_by(id=self.type).first().name

	def getCategoryName(self):
		return itemCategory.query.filter_by(id=self.category).first().name

	def getSubcategoryName(self):
		return itemSubcategory.query.filter_by(id=self.subcategory).first().name

	def getAttributes(self):
		return itemSubcategory.query.filter_by(id=self.subcategory).first().getAttributes()

	def getAttributeValues(self):
		return json.loads(self.item_attributes)

	def getTimeLeft(self):
		if self.unsold == 0:
			return timeago.format(self.added + datetime.timedelta(weeks=4))
		else:
			return "Unsold"

items = Table('items', metadata,
	Column('item_id', String(), primary_key=True, unique=True),
	Column('type', Integer()),
	Column('category', Integer()),
	Column('subcategory', Integer()),
	Column('price', Float(), nullable=True),
	Column('item_attributes', Text(), nullable=True),
	Column('tag_color', Text(), nullable=True),
	Column('entered_by', Integer()),
	Column('removed_by', Integer(), nullable=True),
	Column('unsold', Integer(), default=0),
	Column('added', DateTime()),
	Column('updated', DateTime()),
	extend_existing=True
)
mapper(Item, items)