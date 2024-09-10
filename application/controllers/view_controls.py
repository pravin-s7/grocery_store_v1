from flask import Flask, render_template, redirect, url_for, request
from flask import current_app as app
from application.models import *
from application.validation import *


# <----------------------- View Controls ----------------->

@app.route('/')
def home():
    category = Category.query.all()
    product = Product.query.all()
    top_rated = Product.query.order_by(Product.ratings.desc()).all()

    L = []
    for prd in product:
        p1 = Order.query.filter_by(product_id=prd.p_id).count()
        L.append((prd.p_id, p1))
    L = sorted(L, key=lambda x:x[1], reverse=True)

    most_bought_product = [] # based on number of orders of that product

    for i in range(len(L)):
        prd = Product.query.filter_by(p_id=L[i][0]).first()
        most_bought_product.append(prd)

    new_product = Product.query.order_by(Product.created_at.desc()).all()
    offer_product = Offers.query.filter(Offers.active==True).all()

    return render_template('index.html', category = category, product=product, top_rated=top_rated, 
                           most_bought_product=most_bought_product, new_product=new_product,
                           offer_product=offer_product)


@app.route('/view_category')
def view_categories():
    category = Category.query.all()        
    return render_template('view_categories.html', category=category)

@app.route('/view_category/<int:category_id>')
def category_product(category_id):
    ctg = Category.query.filter_by(c_id=category_id).first()
    category = ctg.products
    return render_template('category_products.html', category=category, ctg = ctg)

@app.route('/view_product')
def view_products():
    product = Product.query.all()
    return render_template('view_products.html', product=product)

@app.route('/view_product/<int:product_id>', methods=["GET", "POST"])
def product_detail(product_id):      
    product = Product.query.filter_by(p_id=product_id).first()
    rating = Order.query.filter(Order.ratings>0, Order.product_id==product_id).count()

    # Similar products
    ctg = Category.query.filter_by(c_id = product.category.c_id).first()
    ctg_prd = ctg.products

    # recently bought together
    r1 = Order.query.order_by(Order.order_id.desc()).filter(Order.product_id==product_id).first()   

    recently_bought_together = []
    if r1: 
        recently_bought_together = Order.query.filter(Order.ordered_at==r1.ordered_at).all() 

    # # Similar products with ratings above 4
    # prd_4 = Product.query.filter(Product.ratings>4, Product.ctg_id==ctg.c_id).all()
    return render_template('product_detail.html', product=product, rating=rating, ctg_prd=ctg_prd, 
                           recently_bought_together=recently_bought_together)

@app.route('/top_rated_product')
def top_rated_product():
    top_rated = Product.query.order_by(Product.ratings.desc()).all()
    return render_template('top_rated_prd.html', product=top_rated)

@app.route('/new_product')
def new_product():
    new_product = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('new_added_prd.html', product=new_product)

@app.route('/offer_product')
def offer_product():
    offer_product = Offers.query.filter(Offers.active==True).all()
    return render_template('offer_products.html', product=offer_product)

@app.route('/most_bought_product')
def most_bought_product():
    product = Product.query.all()
    L = []
    for prd in product:
        p1 = Order.query.filter_by(product_id=prd.p_id).count()
        L.append((prd.p_id, p1))
    L = sorted(L, key=lambda x:x[1], reverse=True)

    most_bought_product = []

    for i in range(len(L)):
        prd = Product.query.filter_by(p_id=L[i][0]).first()
        most_bought_product.append(prd)

    return render_template('most_bought_prd.html', product=most_bought_product)

@app.route('/price_range_products/below_100')
def price_range_below_100():
    products = Product.query.filter( (Product.price<100) ).all()
    return render_template('price_range_product.html', products=products, range='below Rs.100')

@app.route('/price_range_products/100_to_200')
def price_range_101_to_200():
    products = Product.query.filter( (Product.price>100) & (Product.price<200) ).all()
    return render_template('price_range_product.html', products=products, range='Rs.100 - Rs.200')

@app.route('/price_range_products/200_to_500')
def price_range_200_to_500():
    products = Product.query.filter( (Product.price>200) & (Product.price<500) ).all()
    return render_template('price_range_product.html', products=products, range='Rs.200 - Rs.500')

@app.route('/price_range_products/above_500')
def price_range_below_500():
    products = Product.query.filter( (Product.price>500) ).all()
    return render_template('price_range_product.html', products=products, range='above Rs.500')

@app.route('/search')
def search():
    q_string = request.args.get('q')
    q_name = '%{}%'.format(q_string)
    
    product = Product.query.filter( (Product.p_name.like(q_name)) | (Product.price.like(q_name)) | 
                                   (Product.ratings.like(q_name)) | (Product.description.like(q_name)) | 
                                   (Product.pkg_date.like(q_name)) | (Product.net_weight.like(q_name))   ).all()
    
    category = Category.query.filter(Category.c_name.like(q_name) | Category.description.like(q_name) ).all()
    
    return render_template('search_results.html', product=product, category=category, q_string=q_string)    
    