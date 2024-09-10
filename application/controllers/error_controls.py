from flask import flash, redirect
from flask import current_app as app
from application.models import *
from application.validation import *

# <------------------------- Error Handlers ------------------->

@app.errorhandler(404)
def error_404(e):
    return "<center><h1>The requested page has not found.</h1></center>"

@app.errorhandler(403)
def error_403(e):
    return "<center><h1>You don't have access to this page.</h1></center>"

@app.errorhandler(401)
def error_401(e):
    flash("Please Login to access that page")
    return redirect('/login')
    # return "<center><h1>Please Login to access this page.</h1></center>"

@app.errorhandler(500)
def error_500(e):
    return "<center><h1>Something went wrong. Try again!</h1></center>"