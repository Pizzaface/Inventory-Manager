from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
from sqlalchemy.orm import mapper
from models.item_attribute import itemAttribute

class attr_to_subcategory(object):
	query = db_session.query_property()

	def __init__(self, subcategory_id, attr_id):
		self.subcategory_id = subcategory_id
		self.attr_id = attr_id


	def __str__(self):
		return '<attr_to_subcategory {}>'.format(self.item_id)

	def getCategory(self):
		return itemSubcategory.query.filter_by(id=self.subcategory_id).first()

	def getAttribute(self):
		return itemAttribute.query.filter_by(id=self.attr_id).first()

attr_to_subcategories = Table('attrs_to_subcategories', metadata,
	Column('id', Integer(), primary_key=True, autoincrement=True),
	Column('subcategory_id', Integer()),
	Column('attr_id', Integer()),
	extend_existing=True
)
mapper(attr_to_subcategory, attr_to_subcategories)