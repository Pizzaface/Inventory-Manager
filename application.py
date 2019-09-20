from flask import Flask, Response, redirect, url_for, request, abort, render_template, session, jsonify, make_response
from functools import wraps, update_wrapper
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from classes.anonymous import Anonymous

from services.database import init_db, db_session

from models.user import User
from models.item import Item
from models.item_prices import ItemPrice
from models.item_types import itemType
from models.item_category import itemCategory
from models.item_subcategory import itemSubcategory
from models.item_attribute import itemAttribute
from models.attr_to_subcategory import attr_to_subcategory
from models.gio_options import GioOption

from werkzeug.security import generate_password_hash, check_password_hash

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from random import randint

from sqlalchemy import func
import string
import random
import datetime
import json
import urllib
import random
import requests
import re
import os
import timeago
import textwrap
from json import JSONDecoder
from collections import OrderedDict


application = Flask(__name__)
init_db(application)
application.config['SECRET_KEY'] = "<<YOUR SECRET KEY>>"
application.config['UPLOAD_FOLDER'] = os.path.join("static", "img")
application.config['SQLALCHEMY_POOL_RECYCLE'] = 280
application.config['SQLALCHEMY_POOL_SIZE'] = 30
@application.teardown_appcontext
def shutdown_session(exception=None):
	db_session.close()

def nocache(view):
	@wraps(view)
	def no_cache(*args, **kwargs):
		response = make_response(view(*args, **kwargs))
		response.headers['Last-Modified'] = datetime.datetime.now()
		response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
		response.headers['Pragma'] = 'no-cache'
		response.headers['Expires'] = '-1'
		return response
		
	return update_wrapper(no_cache, view)

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters + string.digits
	return ''.join(random.choice(letters) for i in range(stringLength))

def randomLetters(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters
	return ''.join(random.choice(letters) for i in range(stringLength))

# flask-login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.session_protection = "strong"
login_manager.anonymous_user = Anonymous
login_manager.init_app(application)

# TOD Creation
def create_ticket(output_image_path, item_title, barcode, price, color, size):
	photo = Image.open(os.path.join( "static", "tod-example.png"))

	# make the image editable
	drawing = ImageDraw.Draw(photo)
	w, h = photo.size
	black = (0, 0, 0)
	item_title_font = ImageFont.truetype(os.path.join( "static", "calibri.ttf"), 9)

	pricefont = ImageFont.truetype(os.path.join( "static", "calibri.ttf"), 40)
	sizefont = ImageFont.truetype(os.path.join( "static", "calibri.ttf"), 20)
	bcfont = ImageFont.truetype(os.path.join( "static", "code39r.ttf"), 30)

	item_size_w, item_size_h  = drawing.textsize(size, sizefont)
	price_w, price_h = drawing.textsize(str('${:,.2f}'.format(price)), pricefont)
	barcode_w, barcode_h = drawing.textsize(barcode.upper(), bcfont)

	drawing.text(((w - price_w) // 2, h - price_h - 20), str('${:,.2f}'.format(price)), fill=black,stroke=(0,0,0),font=pricefont)
	#drawing.multiline_text(((w - item_title_w) // 2, (h - item_title_h) // 2), item_title.replace('Sleeve', 'SLV'), fill=black,font=item_title_font)
	drawing.text(((w - item_size_w) // 2, ((h - item_size_h) // 2) - 10), size, fill=black,stroke=(0,0,0),font=sizefont)
	drawing.text(((w - barcode_w) // 2, (h - 80) - barcode_h), barcode.upper(), fill=black,stroke=(0,0,0),font=bcfont)


	lines = ['\n'.join(textwrap.wrap(line, 25,
                 break_long_words=False, replace_whitespace=False))
                 for line in item_title.splitlines() if line.strip() != '']
	if size == "":
		y_text = (h / 2) - 20
	else:
		y_text = (h / 2) + 10

	for line in lines:
	    width, height = item_title_font.getsize(line)
	    drawing.text((25, y_text), line, font=item_title_font, fill=black)
	    y_text += height + 5

	cor = (0,0, w,h) # (x1,y1, x2,y2)
	drawing.rectangle(cor, outline=color, width=10)
	photo.save(os.path.join("static","tickets", output_image_path))

# -------------------------------------- #
#              Home Page                 #
# -------------------------------------- #
@application.route('/')
@nocache
@login_required
def home():
	if not current_user.is_authenticated():
		return redirect(url_for('login'))
	return render_template("index.html", admin=current_user.admin)

@application.route('/inventory')
@nocache
@login_required
def inventory():
	expiringItems = Item.query.filter(Item.added >= (datetime.datetime.now() - datetime.timedelta(weeks=4))).filter(Item.added <= (datetime.datetime.now() - datetime.timedelta(weeks=3))).filter_by(unsold=0).order_by(Item.added.asc()).limit(25).all()
	expiredItems = Item.query.filter(Item.added <= (datetime.datetime.now() - datetime.timedelta(weeks=4))).filter(Item.unsold == 0).order_by(Item.added.asc()).all()
	otherItems = Item.query.filter(Item.added >= (datetime.datetime.now() - datetime.timedelta(weeks=3))).filter_by(unsold=0).order_by(Item.added.asc()).all()
	unsoldItems = Item.query.filter(Item.unsold == 1).all()
	return render_template("inventory.html", expiringItems=expiringItems, expiredItems=expiredItems, otherItems=otherItems, unsoldItems=unsoldItems)

@login_required
@application.route('/items', methods=['GET'])
def items():
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		subcategories = itemSubcategory.query.all()
		categories = itemCategory.query.all()
		attributes = itemAttribute.query.all()
		types = itemType.query.all()
		return render_template("items.html", attributes=attributes, subcategories=subcategories, categories=categories, types=types, error=error, success=success)


##############################################
##           Attribute Management           ##
##############################################
@login_required
@application.route('/attribute/add', methods=["GET", "POST"])
def addAttribute():
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)

		return render_template("attributes/addAttribute.html",  error=error, success=success)
	elif request.method == "POST":
		name = request.form['attr_name']
		attr_values = request.form['attr_values']

		new_attr = itemAttribute(attr_name=name, attr_values=attr_values)
		
		try:
			db_session.add(new_attr)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that attribute"))
		else:
			return redirect(url_for("items", success="The attribute %s was successfully added" % (name)))

@login_required
@application.route('/attribute/edit/<id>', methods=["GET", "POST"])
def editAttribute(id=None):
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		oldAttr = itemAttribute.query.filter_by(id=id).first()
		return render_template("attributes/editAttribute.html", oldAttr=oldAttr, attr_values=json.loads(oldAttr.attr_values), error=error, success=success)
	elif request.method == "POST":
		name = request.form['attr_name']
		attr_values = request.form['attr_values']

		new_attr = itemAttribute(attr_name=name, attr_values=attr_values)
		
		try:
			db_session.add(new_attr)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that attribute"))
		else:
			return redirect(url_for("items", success="The attribute %s was successfully added" % (name)))

@login_required
@application.route('/attribute/delete', methods=['POST'])
def deleteAttribute():
	if request.method == "POST":
		attr = itemAttribute.query.filter_by(id=request.form['attributeID']).first()

		try:
			db_session.delete(attr)
			db_session.commit()
		except:
			return jsonify({"error": "Error deleting that attribute."})
		else:
			return jsonify(True)

@application.route('/subcategory/getAttributes', methods=['POST'])
def getAttributes():
	if request.method == "POST":
		attrs = attr_to_subcategory.query.filter_by(subcategory_id=request.form['subcategoryID']).all()

		customdecoder = JSONDecoder(object_pairs_hook=OrderedDict)
		data = {}
		for attr in attrs:
			data.update({
				attr.getAttribute().attr_name: attr.getAttribute().attr_values
			})
		print(data)
		if attrs is None:
			return jsonify({"error": "That subcategory wasn't found"})
		else:
			return jsonify(data)

##############################################
##           Category Management            ##
##############################################
@login_required
@application.route('/category/add', methods=["GET", "POST"])
def addCategory():
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		types = itemType.query.all()

		item_types = []
		for item_type in types:
			item_types.append([item_type.id, item_type.name])

		return render_template("categories/addCategory.html", types=item_types, error=error, success=success)
	elif request.method == "POST":
		name = request.form['name']
		icon = request.form['icon']

		new_category = itemCategory(type_id=int(request.form['type']), name=name, icon=icon)
		

		try:
			db_session.add(new_category)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that Subcategory"))
		else:
			return redirect(url_for("items", success="The Subcategory %s was successfully added" % (name)))

@login_required
@application.route('/category/edit/<id>', methods=["GET", "POST"])
def editCategory(id=None):
	oldCategory = itemCategory.query.filter_by(id=id).first()

	if oldCategory == None:
		return redirect(url_for('items', error="That category doesn't exist."))

	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		types = itemType.query.all()

		item_types = []
		for item_type in types:
			item_types.append([item_type.id, item_type.name])

		return render_template("categories/editCategory.html", category=oldCategory, types=item_types, error=error, success=success)
	elif request.method == "POST":
		name = request.form['name']
		icon = request.form['icon']

		oldCategory.type_id = int(request.form['type'])
		oldCategory.name = name
		oldCategory.icon = icon
		

		try:
			db_session.add(oldCategory)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that category"))
		else:
			return redirect(url_for("items", success="The category %s was successfully added" % (name)))

@login_required
@application.route('/category/delete', methods=['POST'])
def deleteCategory():
	if request.method == "POST":
		category = itemCategory.query.filter_by(id=request.form['categoryID']).first()

		try:
			db_session.delete(category)
			db_session.commit()
		except:
			return jsonify({"error": "Error deleting that category."})
		else:
			return jsonify(True)

##############################################
##         Subcategory Management           ##
##############################################
@login_required
@application.route('/subcategory/add', methods=['GET', "POST"])
def addSubcategory():
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		categories = itemCategory.query.all()
		attributes = itemAttribute.query.all()

		category_withTypes = []
		for category in categories:
			cat_type = itemType.query.filter_by(id=category.type_id).first().name
			category_withTypes.append([category.id, cat_type + " - " + category.name])

		return render_template("subcategories/addSubcategory.html", categories=category_withTypes, attributes=attributes, error=error, success=success)
	elif request.method == "POST":
		formDict = dict(request.form)
		print(formDict)
		parent_category = itemCategory.query.filter_by(id=request.form['category']).first()
		name = request.form['name']
		price = request.form['price']
		sort_order = request.form['sort_order'] if not request.form['sort_order'] == "" else 999999
		del formDict['name']
		del formDict['category']
		del formDict['price']
		del formDict['button_color']
		del formDict['sort_order']

		if request.files['icon'].filename == "":
			return redirect(url_for("addSubcategory",error="You need to add an icon for the subcategory"))


		file = request.files['icon']
		file.save(os.path.join(application.config['UPLOAD_FOLDER'], file.filename))

		button_color = request.form['button_color']
		new_subcategory = itemSubcategory(category_id=parent_category.id, name=name, icon=file.filename, button_color=button_color, sort_order=sort_order)
		db_session.add(new_subcategory)
		db_session.commit()


		subcategory_price = ItemPrice(item_type=parent_category.type_id, category=parent_category.id, subcategory=new_subcategory.id, price=price)

		new_attrs = []
		for attr, value in formDict.items():
			if value == "on":
				new_attrs.append(attr_to_subcategory(new_subcategory.id, int(attr)))

		
		db_session.add(subcategory_price)
		db_session.commit()
		try:
			db_session.add_all(new_attrs)
			db_session.add(new_subcategory)
			db_session.add(subcategory_price)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that Subcategory"))
		else:
			return redirect(url_for("items", success="The Subcategory %s was successfully added" % (name)))

@login_required
@application.route('/subcategory/edit/<sub_id>', methods=["GET", "POST"])
def editSubcategory(sub_id=None):
	oldSubcategory = itemSubcategory.query.filter_by(id=sub_id).first()

	if oldSubcategory == None:
		return redirect(url_for('items', error="That category doesn't exist."))

	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		categories = itemCategory.query.all()
		attributes = itemAttribute.query.all()
		subcatAttrs = attr_to_subcategory.query.filter_by(subcategory_id=sub_id).all()

		attr_ids = [attr.attr_id for attr in subcatAttrs]
		item_categories = []
		for item_category in categories:
			item_categories.append([item_category.id, item_category.name])

		print()
		return render_template("subcategories/editSubcategory.html", subcategory=oldSubcategory, categories=item_categories, attributes=attributes, current_attrs=attr_ids, error=error, success=success)
	elif request.method == "POST":
		formDict = dict(request.form)
		print(formDict)
		name = request.form['name']
		button_color = request.form['button_color']
		sort_order = request.form['sort_order']
		del formDict['name']

		if 'icon' in request.files:
			icon = request.files['icon']

			if not icon.filename == '':
				oldSubcategory.icon = icon.filename
				icon.save(os.path.join(application.config['UPLOAD_FOLDER'], icon.filename))
			

		oldSubcategory.category_id = int(request.form['category'])
		del formDict['category']
		oldSubcategory.name = name
		oldSubcategory.button_color = button_color
		oldSubcategory.sort_order = sort_order
		oldPrice = ItemPrice.query.filter_by(item_subcategory=sub_id).first()
		oldPrice.price = request.form['price']
		oldPrice.item_category = int(request.form['category'])
		del formDict['price']

		

		removedAttr = attr_to_subcategory.query.filter_by(subcategory_id=sub_id).delete()
		db_session.commit()

		new_attrs = []
		for attr, value in formDict.items():
			if value == "on":
				new_attrs.append(attr_to_subcategory(int(sub_id), attr))

		try:
			db_session.add_all(new_attrs)
			db_session.add(oldSubcategory)
			db_session.add(oldPrice)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error editing that subcategory"))
		else:
			return redirect(url_for("items", success="The subcategory %s was successfully added" % (name)))

@login_required
@application.route('/subcategory/delete', methods=['POST'])
def deleteSubcategory():
	if request.method == "POST":
		subcategory = itemSubcategory.query.filter_by(id=request.form['subcategoryID']).first()

		try:
			db_session.delete(subcategory)
			db_session.commit()
		except:
			return jsonify({"error": "Error deleting that subcategory."})
		else:
			return jsonify(True)

##############################################
##            Type Management               ##
##############################################
@login_required
@application.route('/type/add', methods=["GET", "POST"])
def addType():
	if request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		return render_template("types/addType.html", error=error, success=success)
	elif request.method == "POST":
		name = request.form['name']
		icon = request.form['icon']

		new_type = itemType(name=name, icon=icon)
		

		try:
			db_session.add(new_type)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that type"))
		else:
			return redirect(url_for("items", success="The type %s was successfully added" % (name)))

@login_required
@application.route('/type/edit/<id>', methods=["GET", "POST"])
def editType(id=None):
	if request.method == "GET":
		oldType = itemType.query.filter_by(id=id).first()
		if oldType is None:
			return redirect(url_for('items', error="That type doesn't exist."))

		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		return render_template("types/editType.html", type=oldType, error=error, success=success)
	elif request.method == "POST":
		oldType = itemType.query.filter_by(id=id).first()
		if oldType is None:
			return redirect('items', error="That type doesn't exist.")

		name = request.form['name']
		icon = request.form['icon']
		oldName = oldType.name
		oldType.name = name
		oldType.icon = icon

		try:
			db_session.add(oldType)
			db_session.commit()
		except:
			return redirect(url_for("items", error="There was an error adding that type"))
		else:
			return redirect(url_for("items", success="The type %s was successfully updated" % (oldName)))

@login_required
@application.route('/type/delete', methods=['POST'])
def deleteType():
	if request.method == "POST":
		del_type = itemType.query.filter_by(id=request.form['typeID']).first()

		try:
			db_session.delete(del_type)
			db_session.commit()
		except:
			return jsonify({"error": "Error deleting that category."})
		else:
			return jsonify(True)


# -------------------------------------- #
#       Registration, Log in/Out         #
# -------------------------------------- #
@login_required
@application.route('/users', methods=["GET"])
def users():
	if request.method == "GET":
		users = User.query.all()
		return render_template('users.html', users=users)

@login_required
@application.route('/users/add', methods=["GET", "POST"])
def addUser():
	if request.method == "GET":
		return render_template('users/addUser.html')
	elif request.method == "POST":
		username = request.form['employeeNumber']
		name = request.form['name']
		password = generate_password_hash(request.form['password'])
		id = request.form['employeeNumber']



		user = User(username=username, password=password, name=name, id=id, admin=int(request.form['admin']))

		try:
			db_session.add(user)
			db_session.commit()
		except:
			return jsonify(False)
		else:
			return redirect(url_for("home"))

@login_required
@application.route('/users/edit/<id>', methods=["GET", "POST"])
def editUser(id=None):
	oldUser = User.query.filter_by(id=id).first()
	if request.method == "GET":
		
		if oldUser is None:
			return redirect(url_for('users', error="That user doesn't exist."))

		error = request.args.get('error', default = None, type = str)
		success = request.args.get('success', default = None, type = str)
		return render_template("users/editUser.html", user=oldUser, error=error, success=success)
	elif request.method == "POST":
		username = request.form['employeeNumber']
		name = request.form['name']
		if not request.form['password'] == "":
			password = generate_password_hash(request.form['password'])
			oldUser.password = password

		id = request.form['employeeNumber']

		oldUser.id = username
		oldUser.name = name
		oldUser.username = username

		try:
			db_session.add(oldUser)
			db_session.commit()
		except:
			return redirect(url_for("users", error="There was a problem updating that user." % (oldUser.name)))
		else:
			return redirect(url_for("users", success="%s was successfully saved." % (oldUser.name)))

@login_required
@application.route("/user/delete", methods=["POST"])
def deleteUser():
	if request.method == "POST":
		item_to_delete = User.query.filter_by(id=request.form['userID']).first()

		if item_to_delete is None:
			return jsonify(False)

		try:
			db_session.delete(item_to_delete)
			db_session.commit()
		except:
			return jsonify(False)
		else:
			return jsonify(True)

# somewhere to login
@application.route("/login", methods=["GET", "POST"])
def login():
	# user = User(username="07161997", password=generate_password_hash("07161997"), name="Jordan Pizza", id="07161997", admin=1)
	# db_session.add(user)
	# db_session.commit()
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		registered_user = User.query.filter_by(username=username).first()
		if registered_user is None:
			return render_template('login.html', error="That user doesn't exist.")

		if not registered_user.check_password(password):
			return render_template('login.html', error = "That didn't work.")
		else:
			login_user(registered_user, remember=True)
			return redirect(url_for("home"))

		# session.add(registered_user)
		# session.commit()

		# if registered_user.is_authenticated():
		# 	login_user(registered_user, remember=True)
		# 	return redirect(url_for("home"))
		
	elif request.method == "GET":
		error = request.args.get('error', default = None, type = str)
		if not error == None:
			return render_template('login.html', error = error)

		# if not current_user.is_anonymous():
		# 	current_user.check_login()
		
		if current_user.is_authenticated():
			return redirect(url_for("home"))
		
	return render_template('login.html')

# somewhere to logout
@application.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("login")

@login_required
@application.route("/deleteItem", methods=["POST"])
def deleteItem():
	if request.method == "POST":
		item_to_delete = Item.query.filter_by(item_id=request.form['itemID']).first()

		if item_to_delete is None:
			return jsonify(False)

		try:
			db_session.delete(item_to_delete)
			db_session.commit()
		except:
			return jsonify(False)
		else:
			return jsonify(True)

@login_required
@login_required
@application.route("/items/markUnsold", methods=["GET", "POST"])
def removeItem():
	if request.method == "GET":
		return render_template("items/markUnsold.html")
	elif request.method == "POST":
		item_to_delete = Item.query.filter_by(item_id=request.form['itemID']).first()
		if item_to_delete is None:
			return jsonify(False)
			
		item_to_delete.unsold = 1
		item_to_delete.removed_by = current_user.id

		if item_to_delete is None:
			return jsonify(False)

		removed_item = {
			"type": item_to_delete.getTypeName(),
			"category": item_to_delete.getCategoryName(),
			"subcategory": item_to_delete.getSubcategoryName()
		}
		print(removed_item)
		try:
			db_session.add(item_to_delete)
			db_session.commit()
		except:
			return jsonify(False)
		else:
			return jsonify(removed_item)

@login_required
@application.route("/items/add", methods=["GET", "POST"])
def addItem():
	if request.method == "GET":
		item_types = itemType.query.all()
		type_ids = [item_type.id for item_type in item_types]

		typeCategories = {}
		typeCategoryIDs = []
		for type_id in type_ids:
			typeCategories[type_id] = itemCategory.query.filter_by(type_id=type_id).order_by(itemCategory.sort_order.asc()).all()
			typeCategoryIDs += [category.id for category in itemCategory.query.filter_by(type_id=type_id).order_by(itemCategory.sort_order.asc()).all()]

		print(typeCategoryIDs)
		typeSubcategories = {}
		for category_id in typeCategoryIDs:
			typeSubcategories[category_id] = itemSubcategory.query.filter_by(category_id=category_id).order_by(itemSubcategory.sort_order.asc()).all()


		print(typeSubcategories)		
		return render_template("items/addItem.html", itemTypes=item_types, typeCategories=typeCategories, typeSubcategories=typeSubcategories)
	elif request.method == "POST":
		item_type = request.form['item_type']
		item_category = request.form['item_category']
		item_subcategory = request.form['item_subcategory']

		item_attributes = request.form['item_attributes']
		item_quantity = int(request.form['quantity'])
		items = []
		print(current_user.id)
		for i in range(0, item_quantity):
			item_id = randomString(10)
			new_item = Item(item_id, item_type, item_category, item_subcategory, entered_by=current_user.id, item_attributes=item_attributes)

			item_title = "Category: " + new_item.getCategoryName() + "\nSubcategory: " + new_item.getSubcategoryName()
			size = ""
			try:
				attrs = json.loads(item_attributes)
			except json.decoder.JSONDecodeError:
				attrs = {}

			if not item_attributes == "":
				size = attrs['Size'] if "Size" in attrs else ""
				if "Size" in attrs:
					del attrs['Size']
				else:
					size = attrs['Mens_Pant_Sizes'] if "Mens_Pant_Sizes" in attrs else ""
					if "Mens_Pant_Sizes" in attrs:
						del attrs['Mens_Pant_Sizes']

					size = attrs['Womens_Pant_Sizes'] if "Womens_Pant_Sizes" in attrs else ""
					if "Womens_Pant_Sizes" in attrs:
						del attrs['Womens_Pant_Sizes']
				
				for attr, value in attrs.items():
					item_title += "\n%s: %s\n" % (attr.replace("_", " "), value)

			color_to_use = ""
			colors = ['red', 'blue', 'green', 'orange', 'purple']
			current_color = GioOption.query.filter_by(option_key="color").first()
			color_to_use = current_color.option_value
			if datetime.datetime.utcnow() >= current_color.updated + datetime.timedelta(weeks=1):
				color_num = colors.index(current_color.option_value) + 1
				if color_num > len(colors) - 1:
					color_num = 0
				new_color = colors[color_num]
				current_color.option_value = new_color

				color_to_use = new_color
				db_session.add(current_color)
				db_session.commit()



			new_item.tag_color = color_to_use
			create_ticket(item_id + ".png", item_title, item_id, new_item.price, color_to_use, size) 
			items.append(new_item)

		db_session.add_all(items)
		db_session.commit()

		try:
			db_session.add_all(items)
			db_session.commit()
		except:
			return jsonify(False)
		else:
			return jsonify([x.as_dict() for x in items])

@login_required
@application.route("/reports")
def reports():
	totalItems = len(Item.query.all())
	types = itemType.query.all()
	type_totals = Item.query.with_entities(Item.type, func.sum(Item.price).label("price")).group_by(Item.type).all()
	type_item_totals = Item.query.with_entities(Item.type, func.count(Item.item_id).label("items")).group_by(Item.type).all()
	category_totals = Item.query.with_entities(Item.category, func.count(Item.item_id).label("items")).group_by(Item.category).all()

	unsold_totals = Item.query.with_entities(Item.type, Item.category, Item.subcategory, func.sum(Item.price).label("unsold")).group_by(Item.subcategory).order_by(Item.unsold.desc()).filter_by(unsold=1).all()

	entered_by = Item.query.filter(Item.added >= datetime.datetime.now() - datetime.timedelta(days=30)).with_entities(Item.entered_by, func.count(Item.item_id)).group_by(Item.entered_by).all()
	removed_by = Item.query.filter(Item.updated >= datetime.datetime.now() - datetime.timedelta(days=30)).with_entities(Item.removed_by, func.count(Item.item_id)).group_by(Item.removed_by).all()

	new_cat_totals = {}
	for category, total in category_totals:
		curCat = itemCategory.query.filter_by(id=category).first()
		new_cat_totals.update({curCat.name : total})

	new_type_totals = {}
	for type_id, total in type_item_totals:
		curType = itemType.query.filter_by(id=type_id).first()
		new_type_totals.update({curType.name : total})

	category_totals= new_cat_totals
	type_item_totals = new_type_totals
	userCounts = {}
	for user_count in entered_by:
		user, value = user_count
		users_name = User.query.filter_by(id=user).first().name
		userCounts[users_name] = {
			"input": value
		}


	for removed_count in removed_by:
		user, value = removed_count
		if user is None:
			continue

		users_name = User.query.filter_by(id=user).first().name
		if not users_name in userCounts:
			userCounts[users_name] = {}

		userCounts[users_name]['removed'] = value

	unsold_finances = {}
	worst_selling = []
	best_selling = []
	for item in unsold_totals:	
		i_type = itemType.query.filter_by(id=item.type).first().name
		i_category = itemCategory.query.filter_by(id=item.category).first().name
		i_subcategory = itemSubcategory.query.filter_by(id=item.subcategory).first().name

		if item == unsold_totals[-1]:
			best_selling = ["%s - %s - %s" % (i_type, i_category, i_subcategory), item.unsold]
			
		if item == unsold_totals[0]:
			worst_selling = ["%s - %s - %s" % (i_type, i_category, i_subcategory), item.unsold]

		if not i_type in unsold_finances:
			unsold_finances[i_type] = {}

		if not i_category in unsold_finances[i_type]:
			unsold_finances[i_type][i_category] = {}

		if not i_subcategory in unsold_finances[i_type][i_category]:
			unsold_finances[i_type][i_category][i_subcategory] = item.unsold


	itemsPerType = {}
	itemsPerSubcategory = {}
	for item_type in types:
		itemsPerType[item_type] = Item.query.filter_by(type=item_type.id).all()
		itemsPerSubcategory[item_type] = {}
		item_categories = itemCategory.query.filter_by(type_id=item_type.id).all()
		for item_category in item_categories:
			item_subcategories = itemSubcategory.query.filter_by(category_id=item_category.id).all()

			itemsPerSubcategory[item_type][item_category] = {}
			for subcategory in item_subcategories:
				# print(subcategory.name, Item.query.filter_by(subcategory=subcategory.id).all())
				itemsPerSubcategory[item_type][item_category][subcategory] = Item.query.filter_by(subcategory=subcategory.id).all()

	inventory_value = 0
	for category in type_totals:
		inventory_value += category[1]


	return render_template("reporting.html", userCounts=userCounts, type_item_totals=type_item_totals, category_totals=category_totals, best_selling=best_selling, worst_selling=worst_selling, unsold_finances=unsold_finances, totalItems=totalItems, itemsPerType=itemsPerType, itemsPerSubcategory=itemsPerSubcategory, inventory_total=round(inventory_value,2), date_friendly=datetime.datetime.now().strftime("%A, %B %d"))

# callback to reload the user object        
@login_manager.user_loader
def reload_user(userid):
	u = User.query.filter_by(id=userid).first()
	if not u is None:
		return u
	else:
		return 
