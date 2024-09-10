from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask import make_response
from werkzeug.exceptions import HTTPException
import json
from application.models import *

# ------------------ Exception Handling --------------------

class Not_Found_Error(HTTPException):
    def __init__(self, error_message, status_code, error_code):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

class Already_Exists_Error(HTTPException):
    def __init__(self, error_message, status_code, error_code):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

class Not_Exists_Error(HTTPException):
    def __init__(self, error_message, status_code, error_code):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

class Delete_Error(HTTPException):
    def __init__(self, error_message, status_code, error_code):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

# ----------------- Output field --------------------

category_fields = {
    "c_id": fields.Integer,
    "c_name": fields.String,
    "description": fields.String
}

product_fields = {
    "p_id": fields.Integer,
    "p_name": fields.String,
    "unit": fields.String,
    "price": fields.Float,
    "description": fields.String,
    "stock": fields.Integer,
    "created_at": fields.DateTime,
    "net_weight": fields.String,
    "pkg_date": fields.String,
    "ratings": fields.Float,
    "ctg_id": fields.Integer
}

# ---------------- Parser ----------------
category_parser = reqparse.RequestParser()
category_parser.add_argument('c_id')
category_parser.add_argument('c_name')
category_parser.add_argument('description')

product_parser = reqparse.RequestParser()
product_parser.add_argument('p_name')
product_parser.add_argument('unit')
product_parser.add_argument('price')
product_parser.add_argument('stock')
product_parser.add_argument('description')
product_parser.add_argument('net_weight')
product_parser.add_argument('pkg_date')
product_parser.add_argument('ctg_id')


# ------------------ CRUD on Category(API) ------------------
class Api_Category(Resource):
    @marshal_with(category_fields)
    def get(self, id):
        category = Category.query.filter_by(c_id=id).first()
        if category:
            return category, 200
        else:
            raise Not_Found_Error(status_code=404, error_code="CTG004", error_message="Category not found")
    
    @marshal_with(category_fields)
    def post(self):
        info = category_parser.parse_args()
        c1 = Category.query.filter_by(c_name=info['c_name']).all()
        if len(c1)!=0:
            raise Already_Exists_Error(status_code=409, error_code="CTG001", error_message="Category name already exists")
        else:
            category = Category(c_name=info['c_name'])
            db.session.add(category)
            db.session.commit()
            return category, 201

    @marshal_with(category_fields)    
    def delete(self, id):
        c1 = Category.query.get(id)
        if c1:
            p1 = Product.query.filter_by(ctg_id=c1.c_id).all()
            if len(p1)!=0:
                raise Delete_Error(status_code=400, error_code="CTG003", error_message="This category has some products can't delete it")
            else:
                db.session.delete(c1)
                db.session.commit()
                return c1, 200 
        else:
            raise Not_Exists_Error(status_code=404, error_code="CTG002", error_message="Category not exists")
        
    @marshal_with(category_fields)
    def put(self, id):
        info = category_parser.parse_args()
        c1 = Category.query.get(id) 
        if c1:   
            c1.c_name = info['c_name']
            c1.description = info['description']
            db.session.commit()
            return c1, 202
        else:
            raise Not_Exists_Error(status_code=400, error_code="CTG002", error_message="Category not exists")

# ------------------ CRUD on Product(API) ------------------
class Api_Product(Resource):
    @marshal_with(product_fields)
    def get(self, id):
        product = Product.query.filter_by(p_id=id).first()
        if product:
            return product, 200
        else:
            raise Not_Found_Error(status_code=404, error_code="PRD004", error_message="Product not found")
    
    @marshal_with(product_fields)
    def post(self):
        info = product_parser.parse_args()
        product = Product.query.filter_by(p_name=info['p_name']).all()
        if len(product)!=0:
            raise Already_Exists_Error(status_code=409, error_code="PRD001", error_message="Product name already exists")
        else:
            p1 = Product(p_name = info['p_name'], unit=info['unit'], price = info['price'], stock = info['stock'], pkg_date = info['pkg_date'], net_weight = info['net_weight'], ctg_id = info['ctg_id'], description = info['description'])
            db.session.add(p1)
            db.session.commit()
            return p1, 201
        
    @marshal_with(product_fields)    
    def delete(self, id):
        p1 = Product.query.get(id)
        if p1:
            db.session.delete(p1)
            db.session.commit()
            return p1, 200
        else:
            raise Not_Exists_Error(status_code=404, error_code="PRD002", error_message="Product not exists")

    @marshal_with(product_fields)    
    def put(self, id):
        info = product_parser.parse_args()
        p1 = Product.query.get(id)    
        if p1:
            p1.p_name = info['p_name']
            p1.unit = info['unit']
            p1.price = info['price']
            p1.stock = info['stock']
            p1.pkg_date = info['pkg_date']
            p1.net_weight = info['net_weight']
            p1.ctg_id = info['ctg_id']
            p1.description = info['description']
            db.session.commit()
            return p1, 200
        else:
            raise Not_Exists_Error(status_code=404, error_code="PRD002", error_message="Product not exists")   
        
# -------------------------- Api for all category ---------------------

class Api_all_Category(Resource):
    @marshal_with(category_fields)
    def get(self):
        category = Category.query.all()
        return category, 200

# -------------------------- Api for all product -----------------------

class Api_all_Product(Resource):
    @marshal_with(product_fields)
    def get(self):
        product = Product.query.all()
        return product, 200

class Api_all_category_product(Resource):    
    @marshal_with(product_fields)
    def get(self, id):
        product = Product.query.filter_by(ctg_id=id).all()
        if product:
            return product, 200
        else:
            raise Not_Exists_Error(status_code=404, error_code="PRD002", error_message="No product exist in that category")