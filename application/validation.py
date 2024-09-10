from flask import flash, redirect, url_for

# <--------------------------- Validation Functions ------------------------>

def check_password(username, password):
  score=0
  up=False
  low=False
  digit=False 
  if username in password:
    flash("Password should not contain the username")
    return redirect(url_for("signup"))  
  if len(password)>7:
    score+=1
  else:
    flash("Length of the password should be greater than 8")
    return redirect(url_for("signup"))  
  if not password.isalnum():
      score+=1  
  else:
    flash("You password should also contain special characters like @, #, $")
    return redirect(url_for("signup"))   

  for i in password:
    if i.isupper():
      up=True 
    if i.islower():
      low=True  
    if i.isdigit():
      digit=True     

  if up and low:
    score+=1
  else:
      flash("You password should contain atleast one upper case and lower case")
      return redirect(url_for("signup"))     

  
  if digit:
    repit_digit=True
    for x in range(len(password)):
      if x!=len(password)-1:
        # Checks the condition for consecutive digits
        if password[x].isdigit() and password[x+1].isdigit() and int(password[x+1])==int(password[x])+1 :
          repit_digit = False  
  else:
    flash("You password should also contain atleast one digit")
    return redirect(url_for("signup"))   
  

  if digit and repit_digit: # type: ignore
    score+=1

  if score>=3: # password is strong
    return True
  else: # password is weak
    flash("You password is weak. Try other password")
    return redirect(url_for("signup"))   
     
def check_mobile(mobile_no):
  valid=False
  if mobile_no.isdigit() and len(mobile_no)==10 and int(mobile_no[0])>5:
    for x in mobile_no:
      if mobile_no.count(x)<=7:
        valid=True
        if x*6 in mobile_no:
          valid=False
          break
      else:
        break
  if valid:
    return True
  else:
    flash("Please Enter a valid mobile number")
    return redirect(url_for("signup"))
  
def check_float(price):
  price = price.replace('.','',1).isnumeric()
  if price:
    return True
  else:
    flash("Enter a valid price")

def check_discount_float(discount):
  dis = check_float(discount)
  if dis==True:
    if 0<int(float(discount))<100:
      return True
    else:
      flash("Enter a valid Discount") 
  else:
    flash("Enter a valid Discount")  


ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
  filename = filename.split('.', 1)[1].lower()
  if filename in ALLOWED_EXTENSIONS:
    return True
  else:
    return False