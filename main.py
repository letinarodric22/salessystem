from flask import Flask, render_template, request, redirect
# from flask_sqlalchemy import SQLAlchemy
from pgfunc import fetch_data, insert_sales, insert_products,sales_per_day, sales_per_products, add_user, loginn, insert_stock, update_products
import pygal
from datetime import datetime, timedelta


# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
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
   print(prods)
   return render_template('products.html', prods=prods)



@app.route('/addproducts', methods=["POST", "GET"])
def addproducts():
   if request.method=="POST":
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      stock_quantity=request.form["stock_quantity"]
      print(name)
      print(buying_price)
      print(selling_price)
      print(stock_quantity)
      products=(name,buying_price,selling_price,stock_quantity)
      insert_products(products)
      return redirect("/products")
   
@app.route('/editproduct', methods=["POST", "GET"])
def editproducts():
   if request.method=="POST":
      name = request.form["name"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      print(name)
      print(buying_price)
      print(selling_price)
      products=(name,buying_price,selling_price)
      update_products(products)
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



@app.route("/stock")
def stock():
   stock = fetch_data("stock")
   prods= fetch_data("products")
   return render_template('stock.html', stock=stock, prods=prods)

@app.route('/addstock', methods=["POST"])
def addstock():
   if request.method=="POST":
      pid= request.form["pid"]
      quantity=request.form["quantity"]
      stock=(pid,quantity,'now()')
      insert_stock(stock)
      return redirect("/stock")




@app.route("/dashboard")
def bar1():   
    bar_chart = pygal.Bar()
    bar_chart.title = 'sales per product'
    sale_product = sales_per_products()
    name1 = []
    sale1 = []
    for j in sale_product:
       name1.append(j[0])
       sale1.append(j[1])
    bar_chart.x_labels = name1
    bar_chart.add('Sale1', sale1)
    bar_chart=bar_chart.render_data_uri()
    

    line_chart = pygal.Line()
    line_chart.title = 'Sales per Day'
    daily_sales = sales_per_day()
    dates = []
    sales = []
    for i in daily_sales:
       dates.append(i[0])
       sales.append(i[1])
    line_chart.x_labels = dates
    line_chart.add('Sales', sales)
    line_chart=line_chart.render_data_uri()

    return render_template('dashboard.html', line_chart=line_chart, bar_chart=bar_chart)

# @app.route("/login") 
# def login():
#    return render_template('login.html')

@app.route("/register") 
def register():
   return render_template('register.html')



@app.route('/signup', methods=["POST", "GET"])
def adduser():
   error1 = None
   if request.method=="POST":
      full_name= request.form["full_name"]
      email=request.form["email"]
      password=request.form["password"]
      confirm_password=request.form["confirm_password"]
      error1="account created successfully..back to login"
      if password != confirm_password:
         error1 = "password do not match! please enter again."
         
   users=(full_name,email,password,confirm_password,'now()')
   add_user(users)
   return render_template("register.html", error1=error1)
   
      
         
      
   

   

@app.route('/login', methods=["POST", "GET"])
def login():
    error2 = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = loginn(email,password)
        if user:
          for i in user:
                db_email = i[0]
                db_password = i[1]
          if db_password== password and db_email== email:
             return redirect("/login")
          else:
             error2 = "Invalid password or email. Please try again."
            #  return render_template("login.html", error2)
        else:
            error2 = "Account not found. Please register first."
    return render_template("index.html", error2=error2)   
   
 

app.run(debug=True)
