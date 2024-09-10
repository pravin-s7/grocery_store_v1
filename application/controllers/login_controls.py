from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app
from application.models import *
from application.validation import *
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, login_manager
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


login_manager = LoginManager(app)

# <------------------ Login Controls ------------------>

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=["GET", "POST"]) # type: ignore
def login():
    if request.method=="POST":
        result = request.form
        username = result['user']
        password = result['password']
        this_user = User.query.filter_by(email = username).first()

        if this_user:
            if this_user and check_password_hash(this_user.password, password):
                login_user(this_user, remember=True)
                flash("You have been Logged In successfully")
                return redirect('/')       
            else:
                flash("Please fill the right credential to login")
                return redirect('/login')
        else:
            flash("Account doesn't exists. Create a new one by clicking on Signup button")
            return redirect('/login')

    if request.method=='GET':
        return render_template('login/loginpage.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    try:
        if request.method=="POST":
            result = request.form
            name = result['name']
            username = result['username']
            password = result['password']
            # hash the password and store it database
            hashed_password = generate_password_hash(password, method='scrypt')
            re_password = result['re-password']
            email = result['email']
            mobile = result['mobile']
            address = result['door_no']+', '+result['street']+', '+result['place']+', '+result['district']+' - '+result['pincode']


            # check for user already exist
            user = User.query.filter((User.email == email) | (User.username == username) | (User.mobile == mobile) ).all()
            if user:
                message = "Account already exist. Do Login "
                flash(message)
                return  redirect('/signup') 
            else:
                if check_password(username, password)==True:
                    if password==re_password:
                        if check_mobile(mobile)==True:
                            u1 = User(name = name, username=username, password=hashed_password, email=email, mobile=mobile, address=address)
                            db.session.add(u1)
                            db.session.commit()

                            # On signing up, create a voucher for the users
                            v1 = Voucher(user_id = u1.id)
                            db.session.add(v1)
                            db.session.commit()
                            flash("Your account has been successfully created")
                            return redirect('/login') 
                        else:
                            return  redirect('/signup')    
                    else:
                        flash("Type the same password in fields both password and retype-password")
                        return redirect('/signup')  
                else:
                    return  redirect('/signup')  
        else:
            return render_template('login/signup.html')
    except:
        db.session.rollback()  
        flash("Something went wrong. Try again.")  
        return render_template('login/signup.html')

@app.route('/admin/login', methods=["GET", "POST"])
def adminlogin():
    if request.method=="POST":
        result = request.form
        username = result['user']
        password = result['password']
        this_user = User.query.filter_by(email = username).first()
        if this_user:
            if this_user and this_user.role == 'admin' and check_password_hash(this_user.password, password):
                login_user(this_user, remember=True, duration=datetime.timedelta(minutes=10))
                return redirect('/admin/dashboard')
            else:
                return "<center><h1>You don't have access to this page.</h1></center>"
        else:
            return "<center><h1>Please fill the right credential to login</h1></center>"   
    else:
        return render_template('login/adminlogin.html')