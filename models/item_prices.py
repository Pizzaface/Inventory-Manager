from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, Integer, String, Text, DateTime
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

class ItemPrice(object):
	query = db_session.query_property()

	
	def __init__(self, item_type, category, subcategory, price):
		self.item_type = item_type
		self.item_category = category
		self.item_subcategory = subcategory
		self.price = price

item_prices = Table('item_prices', metadata,
	Column('id', Integer(), primary_key=True),
	Column('item_type', Integer()),
	Column('item_category', Integer()),
	Column('item_subcategory', Integer()),
	Column('price', Float(), nullable=True),
	extend_existing=True
)
mapper(ItemPrice, item_prices)