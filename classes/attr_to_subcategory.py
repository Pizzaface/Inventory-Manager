from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata

class attr_to_subcategory(object):
	__tablename__ = "attrs_to_subcategories"
	id = Column('id', Integer(), primary_key=True, unique=True)
	type = Column('subcategory_id', Integer())
	category = Column('attr_id', Integer())

	
	def __init__(self, subcategory_id, attr_id):
		self.subcategory_id = subcategory_id
		self.attr_id = attr_id


	def __str__(self):
		return '<attr_to_subcategory {}>'.format(self.item_id)