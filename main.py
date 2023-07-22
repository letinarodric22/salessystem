from flask import Flask, render_template, request, redirect,session,logging,flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from pgfunc import fetch_data, insert_sales, insert_products,sales_per_day, add_user, loginn, insert_stock, update_products,sales_per_products, remaining_stock,get_remaining_stock,get_pid
import pygal
import barcode
from barcode import Code128
from barcode.writer import ImageWriter
import base64
import io


# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder by convention.... Flask follows a concept called "templating"
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)

# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/index")
def home1():
    return render_template("index.html")



@app.route("/products")
def products():
   prods = fetch_data("products")
   return render_template('products.html', prods=prods)



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
   sales = fetch_data("sales")
   prods= fetch_data("products")
   return render_template('sales.html', sales=sales, prods=prods)



@app.route("/stockk")
def stockk():
   stockk = fetch_data("stockk")
   prods= fetch_data("products")
   return render_template('stock.html', stockk=stockk, prods=prods)


@app.route('/addstock', methods=["POST"])
def addstock():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      stockk=(pid,quantity,'now()')
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
    return render_template('dashboard.html', line_chart=line_chart, bar_chart=bar_chart, bar_chart1=bar_chart1)

# @app.route("/login") 
# def login():
#    return render_template('login.html')

@app.context_processor
def inject_remaining_stock():
     def generate_barcode(product_id=None):
       data = get_pid("products")
       data = Code128(product_id)
       data.save("barcode")
       generate_barcode(data) 
       return data[0] if data is not None else int("0")
     return {'generate_barcode': generate_barcode}




@app.route("/register") 
def register():
   return render_template('register.html')


@app.route('/signup', methods=["POST", "GET"])
def adduser():
   if request.method=="POST":
      full_name = request.form["full_name"]
      email = request.form["email"]
      password  = request.form["password"]
      confirm_password=request.form["confirm_password"]
      error1 = None
      error1="account created successfully..back to login"
      if password != confirm_password:
         error1 = "password do not match! please enter again."
   users=(full_name,email,password,confirm_password,'now()')
   add_user(users)
   return render_template("register.html", error1=error1)
   
      

@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = loginn(email, password)
        if users:
            for user in users:
                db_email = user[0]
                db_password = user[1]
                if db_email == email and db_password == password:
                    return redirect("/index")
            error = "Invalid password or email. Please try again."
        else:
            error = "Account not found. Please register first."
    return render_template("login.html", error=error)  


@app.context_processor
def inject_remaining_stock():
    def remain_stock(product_id=None):
      stock = get_remaining_stock(product_id)
      return stock[0] if stock is not None else int("0")
    return {'remain_stock': remain_stock}



   
app.run(debug=True)
