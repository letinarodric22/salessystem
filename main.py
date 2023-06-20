from flask import Flask, render_template
from pgfunc import fetch_data

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

@app.route("/sales")
def sales():
   sales = fetch_data("sales")


   return render_template('sales.html', sales=sales)

app.run()
