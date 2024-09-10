from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from application.models import *
from application.validation import *
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

# <---------------------- Admin Controls ------------------ >

@app.route('/admin/dashboard', methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role == 'admin': # type: ignore
        return render_template('admin/admin_dashboard.html')  
    else:
        return "<center><h2>Only admin can access it</h2></center>" 


# <---------------------- Category ------------------------->

@app.route('/category', methods=["GET", "POST"])
@login_required
def category():
    if current_user.role == 'admin': # type: ignore
        category = Category.query.all()
        return render_template('admin/category.html', category=category)
    else:
        return "<center><h2>Only admin can access it</h2></center>" 

@app.route('/category/create', methods=["GET", "POST"])
@login_required
def create_category():
    if current_user.role == 'admin': # type: ignore   
        if request.method == 'POST':
            result = request.form
            ctg_name = result['ctg']
            ctg = Category.query.filter_by(c_name=ctg_name).all()
            if len(ctg) != 0:
                return "<h1>Category already exists!</h1>"
            else:
                c1 = Category(c_name= result['ctg'], description=result['desc'])
                db.session.add(c1)
                # upload an product image
                file = request.files['image']

                if file:
                    image = secure_filename(file.filename) # type: ignore
                    if allowed_file(file.filename):
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                        c1.image = image
                    else:
                        flash("Upload the images only in 'jpeg', 'jpg', 'png' formats.") 
                        return render_template("admin/add_ctg.html")   

                db.session.commit()    
                return redirect('/category')
        else:
            return render_template("admin/add_ctg.html")
    else:
        return "<center><h2>Only admin can access it</h2></center>"     
        

@app.route('/category/<int:category_id>/delete')
@login_required
def category_delete(category_id):
    if current_user.role == 'admin': # type: ignore
        try:
            ctg = Category.query.filter_by(c_id=category_id).first()
            db.session.delete(ctg)
            # db.session.delete([i for i in ctg.products])
            db.session.commit()
            return redirect ('/category')
        except:
            return "<h1> This category has some products. Can't delete it. </h1>"
    else:
        return "<center><h2>Only admin can access it</h2></center>"     

@app.route('/category/<int:category_id>/update', methods=["GET", "POST"])
@login_required
def update_category(category_id):   
    if current_user.role == 'admin': # type: ignore
        if request.method=="POST":
            c1 = Category.query.get(category_id)
            ctg_name = request.form['ctg']
            ctg_description = request.form['desc']
            c1.c_name = ctg_name
            c1.description = ctg_description
            db.session.add(c1)
            # upload an product image
            file = request.files['image']

            if file:
                image = secure_filename(file.filename) # type: ignore
                if allowed_file(file.filename):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                    c1.image = image
                else:
                    flash("Upload the images only in 'jpeg', 'jpg', 'png' formats.") 
                    ctg = Category.query.filter_by(c_id=category_id).first()
                    return render_template("admin/update_ctg.html", ctg=ctg)  

            db.session.commit()
            return redirect('/category')
        else:
            ctg = Category.query.filter_by(c_id=category_id).first()
            return render_template("admin/update_ctg.html", ctg=ctg)
    else:
        return "<center><h2>Only admin can access it</h2></center>"    


# <---------------------- Products ------------------------->

@app.route('/product')
@login_required
def products():
    if current_user.role == 'admin': # type: ignore
        product = Product.query.all()
        category = Category.query.all()
        return render_template('admin/product.html', product = product, ctg=category)
    else:
        return "<center><h2>Only admin can access it</h2></center>" 

@app.route('/product/create', methods=["GET", "POST"])
@login_required
def create_product():
    if current_user.role == 'admin': # type: ignore
        if request.method == 'POST':
            result = request.form
            prd_name = result['p_name']
            prd = Product.query.filter_by(p_name=prd_name).all()
            if len(prd) != 0:
                return "<h1>Product already exists!</h1>"
            else:
                if check_float(result['price'])==True:
                    p1 = Product(p_name=result['p_name'], price=result['price'], unit=result['unit'], stock = result['qty'], net_weight = result['net_weight'],
                                pkg_date = result['pkg_date'], description = result['desc'], ctg_id = result['category'])
                    db.session.add(p1)   
                    
                    # upload an product image
                    file = request.files['image']

                    if file:
                        image = secure_filename(file.filename) # type: ignore
                        if allowed_file(file.filename):
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                            p1.image = image
                        else:
                            flash("Upload the images only in 'jpeg', 'jpg', 'png' formats.") 
                            category = Category.query.all()
                            return render_template("admin/add_prd.html", category=category)   

                    db.session.commit()

                    return redirect('/product')
                else:
                    return redirect('/product/create')
        else:
            category = Category.query.all()
            return render_template("admin/add_prd.html", category=category)
    else:
        return "<center><h2>Only admin can access it</h2></center>"     

@app.route('/product/<int:product_id>/delete')
@login_required
def product_delete(product_id):
    if current_user.role == 'admin': # type: ignore
        prd = Product.query.filter_by(p_id=product_id).first()
        db.session.delete(prd)
        # db.session.delete([i for i in ctg.products])
        db.session.commit()
        return redirect ('/product')
    else:
        return "<center><h2>Only admin can access it</h2></center>" 

@app.route('/product/<int:product_id>/update', methods=["GET", "POST"])
@login_required
def update_product(product_id): 
    if current_user.role == 'admin': # type: ignore  
        if request.method=="POST":
            result = request.form
            p1 = Product.query.get(product_id)
            if check_float(result['price'])==True:
                p1.p_name = result['p_name']
                p1.unit=result['unit']
                p1.price=result['price']
                p1.stock = result['qty']
                p1.net_weight = result['net_weight']
                p1.pkg_date = result['pkg_date']
                p1.description = result['desc']
                p1.ctg_id = result['category']
                db.session.add(p1)

                # upload an product image
                file = request.files['image']

                if file:
                    image = secure_filename(file.filename) # type: ignore
                    if allowed_file(file.filename):
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                        p1.image = image
                    else:
                        flash("Upload the images only in 'jpeg', 'jpg', 'png' formats.") 
                        prd = Product.query.filter_by(p_id=product_id).first()
                        category = Category.query.all()
                        return render_template("admin/update_prd.html", prd=prd, category = category)  

                db.session.commit()
                return redirect('/product')
            else:
                prd = Product.query.filter_by(p_id=product_id).first()
                category = Category.query.all()
                return render_template("admin/update_prd.html", prd=prd, category = category)
        else:
            prd = Product.query.filter_by(p_id=product_id).first()
            category = Category.query.all()
            return render_template("admin/update_prd.html", prd=prd, category = category)
    else:
        return "<center><h2>Only admin can access it</h2></center>"    

@app.route('/category/<int:c_id>/product')
@login_required
def category_products(c_id):
    if current_user.role=='admin': # type: ignore   
        product = Product.query.filter_by(ctg_id=c_id).all()
        category = Category.query.filter_by(c_id=c_id).first()
        return render_template('admin/ctg_products.html', product = product, category=category)
    else:    
        return "<center><h2>Only admin can access it</h2></center>"  


# <------------------------ Search ----------------------->

@app.route('/category_search')
def category_search():
    q_string = request.args.get('q')
    q_name = '%{}%'.format(q_string)
    
    category = Category.query.filter( Category.c_id.like(q_name) | Category.c_name.like(q_name) | 
                                     Category.description.like(q_name) ).all()
    return render_template('admin/category_search.html', category=category, q_string=q_string)
    

@app.route('/product_search')
def product_search():
    q_string = request.args.get('q')
    q_name = '%{}%'.format(q_string)
    
    product = Product.query.filter( (Product.p_name.like(q_name)) | (Product.price.like(q_name)) | 
                                    (Product.description.like(q_name)) | 
                                    (Product.stock.like(q_name)) | (Product.p_id.like(q_name)) |
                                    (Product.ctg_id.like(q_name)) ).all()
    
    return render_template('admin/product_search.html', product=product, q_string=q_string)

# <---------------------- Offers ------------------------->

@app.route('/offer', methods=["GET", "POST"])
@login_required
def offers():
    if current_user.role=='admin': # type: ignore   
        offers = Offers.query.all()
        return render_template('admin/offers.html', offers=offers)
    else:    
        return "<center><h2>Only admin can access it</h2></center>"  

@app.route('/offer/create', methods=["GET", "POST"])
@login_required
def create_offer():
    if current_user.role=='admin': # type: ignore 
        if request.method=='POST':
            result = request.form
            offers = Offers.query.all()
            offer = Offers.query.filter_by(product_id=result['product']).first()

            if offer in offers:
                return "<center><h1>Offer already exists for that product</h1></center>"
            else:
                if check_discount_float(result['discount'])==True:
                    off = Offers(product_id=result['product'], discount=result['discount'])
                    db.session.add(off)
                    db.session.commit()
                    return redirect('/offer')
                else:
                    return redirect('/offer/create')
        else:
            products = Product.query.all()
            return render_template('admin/add_offer.html', products=products)
    else:    
        return "<center><h2>Only admin can access it</h2></center>"     

@app.route('/offer/<int:offer_id>/update', methods=["GET", "POST"])
@login_required
def update_offer(offer_id):
    if current_user.role=='admin': # type: ignore   
        if request.method=="POST":
            result=request.form
            off = Offers.query.filter_by(offer_id=result['offer_id']).first()
            
            if result['discount']:
                if check_discount_float(result['discount'])==True:   
                    off.discount = result['discount']
                    off.active = bool(int(result['status'])) 
                    db.session.commit()
                    return redirect('/offer')    
                else:
                    return redirect('/offer')
            else:
                off.active = bool(int(result['status']))  
                db.session.commit()
                return redirect('/offer')   
        else:
            return render_template('admin/offers.html', offers=offers)
    else:    
        return "<center><h2>Only admin can access it</h2></center>" 

@app.route('/offer/<int:offer_id>/delete', methods=["GET", "POST"])
@login_required
def delete_offer(offer_id):
    if current_user.role=='admin': # type: ignore   
        offer = Offers.query.filter_by(offer_id=offer_id).first()
        db.session.delete(offer)
        db.session.commit()
        return redirect('/offer')
    else:    
        return "<center><h2>Only admin can access it</h2></center>"  

# <---------------------- Orders ------------------------->

@app.route('/orders', methods=["GET", "POST"])
@login_required
def order_history():
    if current_user.role=='admin': # type: ignore   
        orders = Order.query.all()
        order_list = []
        for ord in orders:
            date = str(ord.ordered_at)[0:10]
            order_list.append((ord.order_id, ord.user_id, ord.product_id, ord.qty, ord.ratings, date, ord.status))
        return render_template('admin/order_history.html', order=order_list)
    else:    
        return "<center><h2>Only admin can access it</h2></center>"   

@app.route('/orders/<int:order_id>/update', methods=["GET", "POST"])
@login_required
def order_status_update(order_id):
    if current_user.role=='admin': # type: ignore
        if request.method=="POST":
            result=request.form
            o1 = Order.query.filter_by(order_id=result['order_id']).first()
            o1.status = result['status']
            db.session.commit()
            return redirect('/orders')
        else:
            return redirect('/orders')
    else:    
        return "<center><h2>Only admin can access it</h2></center>"  

@app.route('/order_detail/<int:order_id>')    
@login_required
def order_detail(order_id):
    if current_user.role=='admin': # type: ignore
        ord_detail = Order.query.filter_by(order_id=order_id).first()
        user_detail = ord_detail.user
        prd_detail = ord_detail.product
        price = ord_detail.qty * ord_detail.price
        return render_template('admin/order_detail.html', order=ord_detail, product=prd_detail, user=user_detail, price=price)
    else:
        return "<center><h2>Only admin can access it</h2></center>" 


# <---------------------- Summary ------------------------->

@app.route('/salesview', methods=["GET", "POST"])
@login_required
def sales_view():
    if current_user.role=='admin': # type: ignore
        if request.method=="POST":
            order = Order.query.filter_by(product_id=request.form['p_id']).all()
            x_axis = []
            y_axis = []
            for ord in order:
                ord_date = ord.ordered_at
                qty = ord.qty
                date = ord_date.strftime("%d/%m")
                x_axis.append(date)
                y_axis.append(qty) 

            plt.plot(x_axis, y_axis, color='b', linewidth='3')
            if len(order)!=0:
                plt.title(f"Order Date vs Quantity ({order[0].product.p_name})")
            plt.xlabel("Date")
            plt.ylabel("Quantity")
            plt.savefig("static/prd_demand.png")    
            plt.close()    

            tot_order = Order.query.count()
            return render_template('admin/sales_view.html', tot_order = tot_order)
        else:
            x_, y_ = [], []
            category = Category.query.all()
            for ctg in category:
                quantity = 0
                x_.append(ctg.c_name)
                products = Product.query.filter_by(ctg_id=ctg.c_id).all()
                for prd in products:
                    order = prd.orders
                    for ord in order:
                        quantity+=ord.qty
                y_.append(quantity)

            plt.pie(y_, labels=x_, startangle=90)
            plt.title("Overview of Sales Category")
            plt.legend()
            plt.savefig("static/ctg_view.png")
            plt.close()

            xaxis, yaxis, name, price = [], [], [], []
            product = Product.query.all()
            for prd in product:
                qty = 0
                xaxis.append(prd.p_name)
                name.append(prd.p_name)
                orders = prd.orders
                for ord in orders:
                    qty+=ord.qty
                yaxis.append(qty)
                rate = prd.price*qty
                price.append(rate)


            plt.bar(xaxis, yaxis)
            plt.xticks(rotation=90, ha='center', va='center', fontsize=10)
            plt.gca().set_xticklabels(xaxis)
            plt.title("Product vs Quantity")
            plt.xlabel("Product")
            plt.ylabel("Quantity")
            plt.tight_layout()
            plt.savefig("static/prd_view.png")    
            plt.close() 

            plt.bar(name, price)
            plt.xticks(rotation=90, ha='center', va='center', fontsize=10)
            plt.gca().set_xticklabels(name)
            plt.xlabel("Product")
            plt.ylabel("Price")
            plt.title("Product vs Price")
            plt.tight_layout()
            plt.savefig("static/prd_price.png")    
            plt.close() 

            x_axis, y_axis = [], []
            plt.plot(x_axis, y_axis, color='b', linewidth='3')
            plt.xticks(rotation=45, ha='center')
            plt.gca().set_xticklabels(x_axis)
            plt.title("Order_date vs Quantity")
            plt.xlabel("Date")
            plt.ylabel("Quantity")
            plt.savefig("static/prd_demand.png")    
            plt.close()

            tot_order = Order.query.count()
            
            return render_template('admin/sales_view.html', tot_order = tot_order)
    else:
        return "<center><h2>Only admin can access it</h2></center>"     
