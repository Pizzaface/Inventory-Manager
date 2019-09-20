from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
import timeago

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))


class item(object):
	__tablename__ = "items"
	item_id = Column('item_id', String(), primary_key=True, unique=True)
	type = Column('type', Integer())
	category = Column('category', Integer())
	subcategory = Column('subcategory', Integer())
	price = Column('price', Float(), nullable=True)
	tag_color = Column('tag_color', Text(), nullable=True)
	unsold = Column('unsold', Integer(), default=0)
	entered_by = Column('entered_by', Integer())
	removed_by = Column('removed_by', Integer(), nullable=True)
	added = Column('added', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())
	item_attributes = Column('item_attributes', Text(), nullable=True)

	
	def __init__(self, item_id, item_type, category, subcategory, entered_by, removed_by=None, item_attributes={}, unsold=0, price=None, tag_color=None, added=datetime.datetime.utcnow(), updated=datetime.datetime.utcnow()):
		self.item_id = item_id
		self.type = item_type
		self.category = category
		self.subcategory = subcategory
		self.price = ItemPrice.query.filter_by(item_type=item_type, item_category=category, item_subcategory=subcategory).first().price
		self.item_attributes = item_attributes
		self.tag_color = tag_color
		self.added = added
		self.entered_by = entered_by
		self.removed_by = removed_by
		self.unsold = 0
		self.updated = updated

	def getTimeLeft(self):
		return timeago.format(self.added + datetime.timedelta(weeks=4))

	def __str__(self):
		return '<item {}>'.format(self.item_id)