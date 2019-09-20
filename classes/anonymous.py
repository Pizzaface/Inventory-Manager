from flask_login import AnonymousUserMixin

class Anonymous(AnonymousUserMixin):
	def __init__(self):
		self.username = 'Guest'
		self.admin = 0

	def is_authenticated(self):
		return False
 
	def is_active(self):
		return False
 
	def is_anonymous(self):
		return True

	def __type__(self):
		return "Anonymous()"