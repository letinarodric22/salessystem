from flask import Flask, render_template
import psycopg2

# create an object called app
# __name__ is used to tell Flask where to access HTML Files
app = Flask(__name__)
def get_db_connection():
    conn = psycopg2.connect("dbname= duka_june user=postgres password=1234")
    return conn




# a route is an extension of a url which loads you an HTML page
# techcamp.co.ke/


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/products")
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products;')
    # loads records from db here
    products = cur.fetchall()
    cur.close
    # prods = [(1, 'kiwi', 40, 50, 100),(2, 'sugar', 150, 200, 250), (3, 'omo', 50, 70, 100)]
    return render_template("products.html", prods=products)
   

@app.route("/sales")
def sales():
    sales = [(1, 'kiwi', 40, 50),(2, 'sugar', 150, 200), (3, 'omo', 50, 70)]

    return render_template("/sales.html", sales=sales)
    
    

app.run()