from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, String, Text, DateTime, Integer
from services.database import Base, db_session, metadata
import datetime
from sqlalchemy.orm import mapper

import json

class GioOption(object):
	query = db_session.query_property()
	id = Column('id', Integer(), primary_key=True, unique=True)
	option_key = Column('option_key', Text())
	option_value = Column('option_value', Text())
	created = Column('created', DateTime(), default=datetime.datetime.utcnow())
	updated = Column('updated', DateTime(), default=datetime.datetime.utcnow())

	
	def __init__(self, id, option_key, option_value, created, updated):
		self.id = item_id
		self.option_key = option_key
		self.option_value = option_value
		self.created = created
		self.updated = updated


options = Table("gio_options", metadata,
	Column('id', Integer(), primary_key=True, unique=True),
	Column('option_key', Text()),
	Column('option_value', Text()),
	Column('created', DateTime(), default=datetime.datetime.utcnow()),
	Column('updated', DateTime(), default=datetime.datetime.utcnow()),
	extend_existing=True
)
mapper(GioOption, options)