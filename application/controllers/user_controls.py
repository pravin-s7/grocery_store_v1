from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app
from application.models import *
from application.validation import *
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from application.controllers.view_controls import *

# <--------------------- User Controls -------------------->

@app.route('/myprofile', methods=["GET", "POST"])
@login_required
def my_profile():
    user = User.query.filter_by(id=current_user.id).first() #type: ignore
    vouchers = Voucher.query.filter_by(user_id=current_user.id).order_by(Voucher.voucher_id.desc()).all() #type: ignore
    return render_template('user/user_profile.html', user=user, vouchers=vouchers)

@app.route('/updateprofile/<int:user_id>', methods=["GET", "POST"])
@login_required
def update_profile(user_id):
    if request.method=="POST":
        result = request.form
        user = User.query.filter_by(id=user_id).first() # type: ignore
        user.name = result["name"]
        user.username = result["username"]
        user.mobile = result['mobile']
        user.address = result["address"]
        if check_mobile(result['mobile'])==True:
            db.session.commit()
            flash("Your profile has been successfully updated")
            return redirect('/myprofile')
        else:
            user = User.query.filter_by(id=current_user.id).first() # type: ignore
            return render_template("user/update_profile.html", user=user)
    else:
        user = User.query.filter_by(id=current_user.id).first() # type: ignore
        return render_template("user/update_profile.html", user=user)

@app.route('/change_password/<int:user_id>', methods=["GET", "POST"])
@login_required
def change_password(user_id):
    if request.method=="POST":
        result = request.form
        user = User.query.filter_by(id=user_id).first() # type: ignore
        if check_password_hash(user.password, result['password']):
            if check_password(user.username, result['new_pass'])==True:
                if result['new_pass']==result['re_new_pass']:
                    user.password = generate_password_hash(result['new_pass'])
                    db.session.commit()
                    flash("Your password has been successfully changed")
                    return redirect('/myprofile')
                else:
                    flash("Password should be same as new password")
                    user = User.query.filter_by(id=current_user.id).first() # type: ignore
                    return render_template("user/change_password.html", user=user)
            else:
                user = User.query.filter_by(id=current_user.id).first() # type: ignore
                return render_template("user/change_password.html", user=user)
        else:
            flash("Type your correct Old password")
            user = User.query.filter_by(id=current_user.id).first() # type: ignore
            return render_template("user/change_password.html", user=user)
    else:
        user = User.query.filter_by(id=current_user.id).first() # type: ignore
        return render_template("user/change_password.html", user=user)

@app.route('/wishlist', methods=["GET", "POST"])
@login_required
def wishlist():
    wishlist = Wishlist.query.filter_by(user_id = current_user.id).all() # type: ignore
    return render_template('user/wishlist.html', wishlist = wishlist)

@app.route('/add_wishlist', methods=["POST"])
@login_required
def add_wishlist():
    result=request.form
    wish = Wishlist.query.filter_by(user_id=result['user_id'] ,product_id=result['p_id']).first()
    wish_list = Wishlist.query.filter_by(user_id = result['user_id'], product_id=result['p_id']).all()
    if wish in wish_list:
        flash("This product is already in your wishlist")
        return redirect(url_for('product_detail', product_id=result['p_id']))
    else:
        wish = Wishlist(user_id = result['user_id'], product_id = result['p_id'])
        db.session.add(wish)
        db.session.commit()
        flash("Product has been successfully added to the your Wishlist")
        return redirect(url_for('product_detail', product_id=result['p_id']))

@app.route('/wishlist/<int:w_id>/delete')
@login_required
def delete_from_wishlist(w_id):
    item = Wishlist.query.filter_by(w_id=w_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect('/wishlist')

@app.route('/mycart', methods=["GET", "POST"])
@login_required
def my_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).all() # type: ignore
    vouchers = Voucher.query.filter_by(user_id = current_user.id, expired=False).all() # type: ignore
    

    product = []
    for crt in cart:
        prd = crt.products
        if prd:
            if prd.offer:
                if prd.offer.active:
                    product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, crt.product_id, prd.stock, prd.offer.discount, prd.unit, prd.image))
                else:
                    product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, crt.product_id, prd.stock, None, prd.unit, prd.image))        
            else:    
                product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, crt.product_id, prd.stock, None, prd.unit, prd.image))

    total_cost = 0
    for p in product:
        if p[8]>0 and p[9]:
            discount_price = (((100 - p[9])/100)*p[3])*p[5]
            total_cost += discount_price
        elif p[8]>0:
            total_cost += p[3]*p[5]
        else:
            pass    

    voucher = Voucher.query.filter_by(user_id=current_user.id, active=True).first() # type: ignore

    discount = 0        
    if voucher:
        if total_cost>=1000:
            discount = float(total_cost) * (voucher.discount/100)
        elif 500<=total_cost<1000:
            discount = float(total_cost) * ((voucher.discount - 10)/100)
        else:
            discount = float(total_cost) * ((voucher.discount - 15)/100)

    return render_template('user/cart.html', cart=cart, product=product, total_cost=float(round(total_cost,2)), vouchers=vouchers, discount=float(discount))


@app.route('/addcart', methods=["POST"])
@login_required
def add_to_cart():
    result = request.form
    crt = Cart.query.filter_by(user_id=result['user_id'] ,product_id=result['p_id']).first()
    cart_product = Cart.query.filter_by(user_id = result['user_id'], product_id=result['p_id']).all()

    if int(result['stock'])==0:
        flash("Currently the product is out of stock you can't add to your cart")
        return redirect(url_for('product_detail', product_id=result['p_id']))

    elif crt in cart_product:
        flash("This product is already in your cart.")
        return redirect(url_for('product_detail', product_id=result['p_id']))

    else:    
        cart = Cart(user_id = result['user_id'], product_id = result['p_id'])
        db.session.add(cart)
        db.session.commit()
        flash("Product has been successfully added to your cart")
        return redirect(url_for('product_detail', product_id=result['p_id']))

@app.route('/mycart/<int:cart_id>/delete')
@login_required
def delete_from_cart(cart_id):
    item = Cart.query.filter_by(cart_id=cart_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect('/mycart')

@app.route('/mycart/<int:cart_id>', methods=["POST"])
@login_required
def update_qty(cart_id):
    result = request.form
    item = Cart.query.filter_by(cart_id=cart_id).first()
    item.qty = result['qty']
    
    product = Product.query.filter_by(p_id = result['product_id']).first()

    if int(result['qty'])<=int(product.stock):
        db.session.commit()
    else:
        flash("This product has only maximum of {stock} quantity".format(stock=product.stock))
        return redirect('/mycart')  
    return redirect('/mycart')


@app.route('/voucher/apply', methods=["POST"])
@login_required
def voucher_apply():
    result=request.form
    voucher = Voucher.query.filter_by(user_id=current_user.id, active=True, expired=False).all() # type: ignore
    v1 = Voucher.query.filter_by(voucher_id=result['voucher_id']).first()

    if len(voucher)>0:
        flash("Already a voucher is active")
        return redirect('/mycart')
    else:    
        if not v1.expired:
            v1.active = True
            db.session.commit()
        return redirect('/mycart')

@app.route('/voucher/remove', methods=["POST"])
@login_required
def voucher_remove():
    result=request.form
    v1 = Voucher.query.filter_by(voucher_id=result['voucher_id']).first()
    if not v1.expired:
        v1.active = False
        db.session.commit()
        return redirect('/mycart')
    return redirect('/mycart')

@app.route('/orderpage', methods=["POST"])
@login_required
def order_page():
    result = request.form
    user = User.query.filter_by(id=current_user.id).first() # type: ignore
    cart = Cart.query.filter_by(user_id=current_user.id).all() # type: ignore
    voucher = Voucher.query.filter_by(user_id=current_user.id, active=True).first() # type: ignore
    product = []
    order_list = []
    for crt in cart:
        prd = crt.products
        if prd:
            if prd.stock>0:
                if prd.offer:
                    if prd.offer.active:
                        product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, prd.offer.discount, prd.unit, prd.image))
                        order_list.append((current_user.id, prd.p_id, crt.qty, str(prd.offer.discount))) # type: ignore
                    else:
                        product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, None, prd.unit, prd.image))
                        order_list.append((current_user.id, prd.p_id, crt.qty, None)) # type: ignore
                else:
                    product.append((prd.p_name, prd.ratings, prd.category.c_name, prd.price, prd.net_weight, crt.qty, crt.cart_id, None, prd.unit, prd.image))
                    order_list.append((current_user.id, prd.p_id, crt.qty, None)) # type: ignore        

    total_cost = 0
    for p in product:
        if p[7]:
            discount_price = (((100 - p[7])/100)*p[3])*p[5]
            total_cost += discount_price
        else:    
            total_cost += p[3]*p[5]    
    
    discount = 0        
    if voucher:
        if total_cost>=1000:
            discount = float(total_cost) * (voucher.discount/100)
        elif 500<=total_cost<1000:
            discount = float(total_cost) * ((voucher.discount - 10)/100)
        else:
            discount = float(total_cost) * ((voucher.discount - 15)/100)

    order_list.append((float(total_cost), float(discount)))
    return render_template('user/order_page.html', user=user, product=product, total_cost=float(round(total_cost,2)), order_list=order_list, discount=round(discount,2))

@app.route('/placeorder', methods=["POST"])
@login_required
def place_order():
    try:
        # place the order
        result=request.form
        order_list = result['order']  
        order_list = eval(order_list)

        for ord in order_list[:-1]:
            # Make order
            user_id = ord[0]
            product_id = ord[1]
            qty = ord[2]
            offer = ord[3]

            p1 = Product.query.filter_by(p_id = product_id).first()
            if offer:
                offer_price = ((100-float(offer))/100)*float(p1.price)
                o1 = Order(user_id = user_id, product_id=product_id, qty=qty, price=offer_price, address=current_user.address, mobile=current_user.mobile) #type: ignore
            else:
                o1 = Order(user_id = user_id, product_id=product_id, qty=qty, price=p1.price, address=current_user.address, mobile=current_user.mobile) #type: ignore    

            db.session.add(o1)
            db.session.commit()
            # update the stock in product  
            # p1 = Product.query.filter_by(p_id = product_id).first()
            p1.stock = p1.stock - qty
            db.session.add(p1)
            db.session.commit()

        # After placing the order delete the voucher if anything is active
        voucher = Voucher.query.filter_by(user_id=current_user.id, active=True).first() # type: ignore
        if voucher:
            voucher.expired = True
            voucher.active = False
            db.session.commit()

        # if a customer purchase more than Rs.2000 give another voucher    
        total_price = order_list[-1][0]
        discounted_price = order_list[-1][1]

        if float(total_price) - float(discounted_price)>=2000:
            v1 = Voucher(user_id = current_user.id) # type: ignore
            db.session.add(v1)
            db.session.commit()

        # delete all cart items    
        cart = Cart.query.filter_by(user_id=current_user.id).all() #type: ignore
        for crt in cart:
            db.session.delete(crt)
            db.session.commit()  
        
        return redirect('/myorders')
    except:
        db.session.rollback()
        flash("Something went wrong. Try again")
        return redirect(url_for("my_cart"))

@app.route('/myorders', methods=["GET"])
@login_required
def my_orders():
    user = User.query.filter_by(id = current_user.id).first() # type: ignore
    orders = Order.query.filter(Order.user_id==current_user.id).order_by(Order.ordered_at.desc()).all() # type: ignore
    product_list = []
    for product in orders:
        if product:
            ordered_at = str(product.ordered_at)[0:10]
            prd = product.product
            if prd:
                price = product.price * product.qty
                product_list.append((prd.p_name, prd.ratings, prd.category.c_name, product.price, prd.net_weight, product.qty, price, ordered_at, product.status, product.order_id, product.product_id, product.address, product.mobile, product.ratings, prd.image, product.review))
    return render_template('user/my_orders.html', product=product_list, user=user)

@app.route('/review', methods=["POST"])
def review():
    try:    
        # update rating for order
        result = request.form
        order = Order.query.filter_by(order_id=result['order_id']).first()
        order.ratings = result['rating']
        if result['review']:
            order.review = result['review']
        db.session.commit()

        # update rating for product which is average of all orders of that product
        products = Order.query.filter_by(product_id=result['product_id']).all()

        count = 0
        total_ratings = 0

        for p in products:
            if p.ratings:
                count +=1
                total_ratings+=int(p.ratings)

        avg_ratings = total_ratings/count

        product = Product.query.filter_by(p_id=result['product_id']).first()

        product.ratings = avg_ratings
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('my_orders'))
    except:
        db.session.rollback()
        flash("Something went wrong. Try again")
        return redirect(url_for("my_orders"))