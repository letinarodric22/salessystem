from flask import (
    Flask, render_template, request, redirect, session, flash, url_for
)
# from flask_sqlalchemy import SQLAlchemy
from pgfunc import *
from sms import *
import pygal
import os, random
from barcode import Code128
from barcode.writer import ImageWriter
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder by convention.... Flask follows a concept called "templating"
# All CSS/JS/ Images are put inside "static" folder

app = Flask(__name__)
# secret key
app.secret_key = os.urandom(24)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@5432/inventory'
# db = SQLAlchemy(app)



def login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return decorated_view



# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/index", methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:

        search_query = request.args.get('search', default='', type=str)
        prods = fetch_data('products')
        random.shuffle(prods)
        random_products = random.sample(prods, 7)
        prods = [p for p in prods if search_query.lower() in p[1].lower()]
        return render_template('index.html', random_products=random_products,search_query=search_query, prods=prods)



@app.route("/products")
def products():
      if not session.get('logged_in'):
        return redirect(url_for('login'))
      else:
        prods = fetch_data("products")
        prods.reverse()
        return render_template('products.html', prods=prods)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if not session.get('cart'):
        session['cart'] = {}

    product_id = request.form.get('id')
    quantity = int(request.form.get('stock_quantity', 1))

    # Update the cart with the new quantity
    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity

    return redirect('/products', '/cart')

@app.route('/cart')
def cart():
    if 'cart' in session:
        return render_template('cart.html')
    else:
        return render_template('cart_empty.html')
    
@app.route('/checkout', methods=['POST'])
def checkout():
    # Process the checkout logic here
    session.pop('cart', None)
    return render_template('checkout_success.html')

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('id')
    if product_id in session['cart']:
        del session['cart'][product_id]
    return redirect('/cart')


def calculate_cart_total():
    # Retrieve the cart items from the session
    cart_items = session.get('cart', [])

    # Fetch product prices from the database
    products = fetch_data("products")

    # Calculate the total cart value
    total = 0
    for item in cart_items:
        product_id = item['id']
        quantity = item['quantity']
        for product in products:
            if product[0] == product_id:
                price = product[3]  # Assuming price is in the fourth column
                total += price * quantity
    return redirect('/cart', total=total)



@app.context_processor
def inject_datetime():
    now = datetime.now()
    return {'current_date': now.strftime('%d-%m-%Y'), 'current_time': now.strftime('%I:%M:%S %p')}



@app.route('/addproducts', methods=["POST", "GET"])
def addproducts():
   if request.method=="POST":
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      image_url=request.form["image_url"]
      category = request.form["category"]
      products=(name,buying_price,selling_price,image_url,category)
      insert_products(products)
      return redirect("/products")
   

@app.route('/editproduct', methods=["POST", "GET"])
def editproducts():
   if request.method=="POST":
      id = request.form['id']
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      image_url=request.form["image_url"]
      category = request.form["category"]
      print(name)
      print(buying_price)
      print(selling_price)
      vs=(id,name,buying_price,selling_price,image_url,category)
      update_products(vs)
      return redirect("/products")
   
@app.route('/deleteproduct', methods=["POST"])
@login_required
def deleteproduct():
    if request.method == "POST":
        product_id = request.form["id"]
        delete_product(product_id)
        return redirect("/products")

   
 
@app.route('/addsales', methods=["POST", "GET"])
def addsales():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      sales=(pid,quantity,'now()')
      insert_sales(sales)
      return redirect("/sales")

      

@app.route("/sales")
def sales():
   if not session.get('logged_in'):
        return redirect(url_for('login'))
   else:
       sales = fetch_data("sales")
       prods= fetch_data("products")
       return render_template('sales.html', sales=sales, prods=prods)



@app.route("/stockk")
def stockk():
       if not session.get('logged_in'):
        return redirect(url_for('login'))
       else:
           stockk = fetch_data("stocks")
           prods= fetch_data("products")
           return render_template('stock.html', stockk=stockk, prods=prods)


@app.route('/addstock', methods=["POST"])
def addstock():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      stockk=(pid,quantity, 'now()')
      insert_stock(stockk)
      return redirect("/stockk")


@app.route("/dashboard")
def bar1():   
   #  bar graph for sales per product
    bar_chart = pygal.Bar()
    bar_chart.title = 'sales per product'
    sale_product = sales_per_products()
    name1 = []
    sale1 = []
    for j in sale_product:
       name1.append(j[0])
       sale1.append(j[1])
    bar_chart.x_labels = name1
    bar_chart.add('Sale', sale1)
    bar_chart=bar_chart.render_data_uri()

   #  line graph for sales per month
    line_chart = pygal.Line()
    line_chart.title = 'Sales per Month'
    daily_sales = sales_per_day()
    dates = []
    sales = []
    for i in daily_sales:
       dates.append(i[0])
       sales.append(i[1])
    line_chart.x_labels = dates
    line_chart.add('Sales', sales)
    line_chart=line_chart.render_data_uri()

# remaining_stock
    bar_chart1 = pygal.Bar()
    bar_chart1.title = 'remaining stock'
    remain_stock = remaining_stock()
    name1 = []
    stockk = []
    for j in remain_stock:
       name1.append(j[1])
       stockk.append(j[2])
    bar_chart1.x_labels = name1
    bar_chart1.add('stock', stockk)
    bar_chart1=bar_chart1.render_data_uri()

    

       #Graph to show revenue per day
    daily_revenue = revenue_per_day()
    dates = []
    sales_revenue_per_day = [] 
    for i in daily_revenue:
     dates.append(i[0])
     sales_revenue_per_day.append(i[1]) 
    line_chart2 = pygal.Line()
    line_chart2.title = "Revenue per Day"
    line_chart2.x_labels = dates
    line_chart2.add("Revenue(KSh)", sales_revenue_per_day)
    line_chart2=line_chart2.render_data_uri()

   #Graph to show revenue per month
    monthly_revenue = revenue_per_month()
    dates = []
    sales_revenue_per_month = [] 
    for i in monthly_revenue:
     dates.append(i[0])
     sales_revenue_per_month.append(i[1]) 
    line_chart1 = pygal.Line()
    line_chart1.title = "Revenue per Month"
    line_chart1.x_labels = dates
    line_chart1.add("Revenue(KSh)", sales_revenue_per_month)
    line_chart1=line_chart1.render_data_uri()
    return render_template('dashboard.html', line_chart=line_chart, bar_chart=bar_chart, bar_chart1=bar_chart1, line_chart1=line_chart1, line_chart2=line_chart2)




@app.route('/signup', methods=["POST", "GET"])
def adduser():
    error1 = None
    full_name_value = ""
    email_value = ""

    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        users = (full_name, email, phone, hashed_password, 'now()')

        if len(password) < 8:
            error1 = "Password should be at least 8 characters long."
        elif not any(char.isalpha() for char in password) or not any(char.isdigit() or char.isalnum() for char in password):
            error1 = "Password should contain letters and at least one number or symbol."
        elif email_exists(email):
            error1 = "This email already exists. Please choose a different email."
        else:
            # If there are no errors, continue with user creation and redirection
            add_user(users)
            
            # Create an instance of the SMS class
            sms_instance = SMS()
            
            # Send SMS and get the message
            sms_instance.send(full_name, phone)
            
            # Customize your flash message
            flash(f"Dear {full_name}, welcome! Your registration is successful. Please check your phone for a confirmation message.")
            
            return redirect('/login')

    # Retain entered values for error display
    full_name_value = request.form.get("full_name", "")
    email_value = request.form.get("email", "")

    return render_template("register.html", error1=error1, full_name_value=full_name_value, email_value=email_value)

def email_exists(email):
    # Check if the email already exists in the database
    users = fetch_data("users")
    for user in users:
        db_email = user[1]
        if db_email == email:
            return True  # Email already exists
    return False  # Email does not exist




      

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = fetch_data("users")
        for user in users:
            db_email = user[1]
            db_hashed_password = user[3]
            if db_email == email and check_password_hash(db_hashed_password, password):
                session['logged_in'] = True
                return redirect('/index')
        flash('Incorrect email or password, please try again.', 'error')
    return render_template("login.html")

# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('login'))


@app.context_processor
def inject_remaining_stock():
    def remain_stock(product_id=None):
      stock = get_remaining_stock(product_id)
      return stock[0] if stock is not None else int("0")
    return {'remain_stock': remain_stock}

@app.context_processor
def generate_barcode():
    id_list = fetch_data("products")
    barcode_paths = []
    for pid_tuple in id_list:
        pid = pid_tuple[0]
        code = Code128(str(pid), writer=ImageWriter())
        barcode_path = f"static/barcodes/{pid}.png"
        code.save(barcode_path)
        barcode_paths.append(barcode_path)
    return {'generate_barcode': generate_barcode}


@app.route("/logout")
def logout():
    session.pop("username", None) 
    return redirect(url_for("login"))


if __name__ == '__main__': 
    app.run(debug=True)
  
 
