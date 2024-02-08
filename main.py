from flask import Flask, render_template, request, redirect,session,flash, g, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from pgfunc import fetch_data, insert_sales, insert_products,sales_per_day, add_user, loginn, insert_stock, update_products
from pgfunc import sales_per_products, remaining_stock,get_remaining_stock,get_pid, revenue_per_month, revenue_per_day

import pygal
import os
import psycopg2
from barcode import Code128
from barcode.writer import ImageWriter
from functools import wraps
conn = psycopg2.connect("dbname=duka_june user=postgres password=1234")
cur = conn.cursor()
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime






# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder by convention.... Flask follows a concept called "templating"
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@5432/duka_june'
# db = SQLAlchemy(app)
app.secret_key = os.urandom(24)



    

def login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return decorated_view


# @app.before_request
# def restrict_pages():
#     # List of routes that require authentication
#     protected_routes = ['/products', '/sales', '/dashboard', '/stockk']

#     # Check if the requested path is a protected route
#     if request.path in protected_routes and not session.get('logged_in'):
#         return redirect('/login')

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
        prods = [p for p in prods if search_query.lower() in p[1].lower()]
        return render_template('index.html', search_query=search_query, prods=prods)



@app.route("/products")
# @login_required
def products():
      if not session.get('logged_in'):
        return redirect(url_for('login'))
      else:
        prods = fetch_data("products")
        return render_template('products.html', prods=prods)



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
      products=(name,buying_price,selling_price)
      insert_products(products)
      return redirect("/products")
   

@app.route('/editproduct', methods=["POST", "GET"])
def editproducts():
   if request.method=="POST":
      id = request.form['id']
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      print(name)
      print(buying_price)
      print(selling_price)
      vs=(id,name,buying_price,selling_price)
      update_products(vs)
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
           stockk = fetch_data("stockk")
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
   if request.method == "POST":
      full_name = request.form["full_name"]
      email = request.form["email"]
      password  = request.form["password"]
      confirm_password=request.form["password"]
      hashed_password = generate_password_hash(password)
      users=(full_name,email, hashed_password, 'now()')
      add_user(users)
      error1="account created successfully..back to login"
      if password != confirm_password:
         error1 = "password do not match! please enter again."
         return redirect('/register')
   return render_template("register.html", error1=error1)
   
      

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = loginn()
        for user in users:
            db_email = user[0]
            db_hashed_password = user[1]
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
    id_list = get_pid()
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
    app.run(host = "0.0.0.0", port = 3400, debug=True)
  
 
