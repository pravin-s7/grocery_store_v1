from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# < -------------------- Models ------------------- >

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True, nullable = False, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(), unique = True)
    mobile = db.Column(db.Integer(), unique=True)
    address = db.Column(db.String(250))
    role = db.Column(db.String(5), nullable=False, default='user')
    orders = db.relationship('Order', backref='user', lazy = True)
    cart_products = db.relationship('Cart', backref='user', lazy = True)
    wishlist = db.relationship('Wishlist', backref='user', lazy = True)
    vouchers = db.relationship('Voucher', backref='user', lazy = True)
    
class Category(db.Model):
    __tablename__ = 'category'
    c_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    c_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String())
    image = db.Column(db.String())
    products = db.relationship('Product', backref = 'category', cascade = "all,delete", lazy = True)

class Product(db.Model):
    __tablename__ = 'product'
    p_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    p_name = db.Column(db.String(50), nullable=False, unique = True)
    unit = db.Column(db.String(), nullable = False)
    price = db.Column(db.Numeric(6,2), nullable=False)
    description = db.Column(db.String())
    stock = db.Column(db.Integer(), nullable = False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    net_weight = db.Column(db.String())
    pkg_date = db.Column(db.String()) 
    ratings = db.Column(db.Numeric(1,1), default=0)
    image = db.Column(db.String())
    ctg_id  = db.Column(db.Integer(), db.ForeignKey('category.c_id'), nullable=False)
    offer = db.Relationship('Offers', backref='product', uselist=False) # one-to-one relationship

class Order(db.Model): 
    __tablename__ = 'order'
    order_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    price = db.Column(db.Numeric(6,2), nullable=False)
    qty = db.Column(db.Integer(), nullable=False)
    mobile = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    ordered_at = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    ratings = db.Column(db.Numeric(1,1), default=0)
    review = db.Column(db.String())
    status = db.Column(db.String(), default="Delivered soon")
    product_id = db.Column(db.Integer(), db.ForeignKey("product.p_id"))
    product = db.relationship('Product', backref = 'orders') # one to many relationship

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer(), db.ForeignKey("product.p_id"))
    qty = db.Column(db.Integer(), nullable=False, default=1)
    products = db.relationship('Product', backref = 'cart')

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    w_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)
    product_id = db.Column(db.Integer(), db.ForeignKey("product.p_id"), nullable = False)
    products = db.relationship('Product', backref = 'wish_list')

class Offers(db.Model):
    __tablename__ = 'offers'
    offer_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    product_id = db.Column(db.Integer(), db.ForeignKey("product.p_id"), unique=True)
    discount = db.Column(db.Numeric(2,2), nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)

class Voucher(db.Model):
    __tablename__ = 'voucher'
    voucher_id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    voucher_name = db.Column(db.String(10), nullable=False, default="GROC20")
    discount = db.Column(db.Integer(), nullable=False, default=20)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    expired = db.Column(db.Boolean(), nullable=False, default=False)