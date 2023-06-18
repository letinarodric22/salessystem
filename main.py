from flask import Flask, render_template
from main1 import insert_product,fetch_data
from main2 import insert_sales,fetch_data

# create an object called app
# __name__ is used to tell Flask where to access HTML Files


app = Flask(__name__)


# a route is an extension of a url which loads you an HTML page
# techcamp.co.ke/

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():
    # loads records from db here
    prods = [(1, 'kiwi', 40, 50, 100),(2, 'sugar', 150, 200, 200)]

    return render_template("products.html", prods=prods)



app.run()