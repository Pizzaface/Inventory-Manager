from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, Integer, String, Text, DateTime
from services.database import Base, db_session, metadata
import datetime

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))


class ItemPrice(object):
	__tablename__ = "item_prices"
	id = Column('id', Integer(), primary_key=True)
	type = Column('item_type', Integer())
	item_category = Column('item_category', Integer())
	item_subcategory = Column('item_subcategory', Integer())
	price = Column('price', Float(), nullable=True)
	
	def __init__(self, item_type, category, subcategory, price):
		self.item_type = item_type
		self.item_category = category
		self.item_subcategory = subcategory
		self.price = price