from flask import Flask, render_template, request, redirect
from pgfunc import fetch_data, insert_sales, insert_products

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


   return render_template('sales.html', sales=sales)

app.run(debug=True)
