from flask import Flask, render_template, request, redirect
from pgfunc import fetch_data, insert_sales, insert_products,sales_per_day, sales_per_products
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
      stock_quantity=request.form["stock_quantity"]
      print(name)
      print(buying_price)
      print(selling_price)
      print(stock_quantity)
      products=(name,buying_price,selling_price,stock_quantity)
      insert_products(products)
      return redirect("/products")
   
@app.route('/addsales', methods=["POST", "GET"])
def addsales():
   if request.method=="POST":
      
      pid= request.form["pid"]
      quantity=request.form["quantity"]

      

      
      print(pid)
      print(quantity)
      

      sales=(pid,quantity,'now()')
      insert_sales(sales)
      return redirect("/sales")

      


@app.route("/sales")
def sales():
   sales = fetch_data("sales")
   prods= fetch_data("products")


   return render_template('sales.html', sales=sales, prods=prods)




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


    


   

app.run(debug=True)
