# <----------- Basic Packages --------------->
from flask import Flask
from flask_restful import Api
from flask_login import LoginManager
from flask_cors import CORS

# <----------- For Logging --------------->
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# <-------------------- Import the models, api ------------------>
from application.models import *
from application.resources import *

# <--------------------- Configuration ------------------->

app = None
api = None

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///grocerydb.sqlite3"
    app.config['SECRET_KEY'] = "my_secret_key"
    app.config['UPLOAD_FOLDER'] = './static/images'

    api = Api(app)
    CORS(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    app.app_context().push()

    return app, api

app, api = create_app()

# <--------------------- Import all the controllers ------------------------->

from application.controller import *

# ----------------------- API endpoints -------------------------

api.add_resource(Api_Category, "/api/category", "/api/category/<int:id>")
api.add_resource(Api_Product, "/api/product", "/api/product/<int:id>")
api.add_resource(Api_all_Category, "/api/all_category")
api.add_resource(Api_all_Product, "/api/all_product")
api.add_resource(Api_all_category_product, "/api/all_product/<int:id>")

# <-------------------- Main ------------------- >

if __name__=='__main__':
    app.run(debug=True)