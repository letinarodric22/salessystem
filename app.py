from flask import (
    Flask, render_template, request, redirect, session, flash, url_for,jsonify
)
# from flask_sqlalchemy import SQLAlchemy
from pgfunc import *

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pygal
import os, random
from barcode import Code128
from barcode.writer import ImageWriter
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import Counter

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


def admin_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if not session.get('logged_in') or not session.get('is_admin'):
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
        if search_query:
            prods = [p for p in prods if search_query.lower() in p[1]]
        return render_template('index.html', random_products=random_products, search_query=search_query, prods=prods)


@app.route("/products")
def products():
      if not session.get('logged_in'):
        return redirect(url_for('login'))
      else:
        prods = fetch_data("products")
        prods.reverse()
        ser = {i[2] for i in prods}
    # Create a dictionary to store items grouped by category
        items_by_category = {category: [] for category in ser}
    # Populate the items_by_category dictionary
        for item in prods:
            category = item[2]  # Assuming servicetype is at index 1
            items_by_category[category].append(item)
        return render_template('products.html', prods=prods,items_by_category=items_by_category)
      
@app.route('/categories')
def categories():
    prods = fetch_data("products")
    ser = {i[6] for i in prods}
    # Create a dictionary to store items grouped by category
    items_by_category = {category: [] for category in ser}
    # Populate the items_by_category dictionary
    for item in prods:
        category = item[6]  # Assuming servicetype is at index 1
        items_by_category[category].append(item)
    return render_template("category.html", items_by_category=items_by_category, prods=prods)    





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
   
   


@app.route('/addtocart', methods=["POST"])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    pid = request.form["pid"]
    quantity = int(request.form["quantity"])

    # Fetch product information from the database
    cur.execute("SELECT * FROM products WHERE id = %s", (pid,))
    product = cur.fetchone()

    if product:
        # Check if the product is already in the cart
        product_found = False
        for item in session['cart']:
            if item['pid'] == pid:
                # If the product is already in the cart, update the quantity
                item['quantity'] += quantity
                product_found = True
                break
        if not product_found:
            # If the product is not in the cart, add it
            session['cart'].append({
                'pid': pid,
                'name': product[1],
                'image': product[5],
                'price': product[3],
                'quantity': quantity
            })
        # Reconstruct the entire session cart with updated item quantities
        session['cart'] = reconstruct_cart(session['cart'])
        # Redirect to view_cart route
        return redirect('/index#py-5')
    else:
        return "Product not found"


def reconstruct_cart(cart):
    reconstructed_cart = []
    seen_pids = set()  # Track seen product IDs
    for item in cart:
        if item['pid'] not in seen_pids:
            # If product ID is not seen before, add the item directly
            reconstructed_cart.append(item)
            seen_pids.add(item['pid'])
        else:
            # If product ID is seen before, update the quantity
            for existing_item in reconstructed_cart:
                if existing_item['pid'] == item['pid']:
                    existing_item['quantity'] += item['quantity']
                    break
    return reconstructed_cart



@app.route('/deletefromcart', methods=['POST'])
def delete_from_cart():
    if 'cart' in session:
        pid = request.json.get('pid')
        for item in session['cart']:
            if item['pid'] == pid:
                session['cart'].remove(item)  # Remove the item from the cart
                session.modified = True  # Mark the session as modified after deletion
                break
        # Recalculate total price after deleting item
        total_price = sum(float(item['price']) * int(item['quantity']) for item in session['cart'])
        # Return JSON response with updated total price
        return jsonify({'success': True, 'total_price': total_price})
    return jsonify({'success': False})
    


@app.route('/updatecart', methods=["POST"])
def update_cart():
    pid = request.form["pid"]
    quantity = int(request.form["quantity"])
    # Update quantity of item in session cart based on pid
    for item in session['cart']:
        if item['pid'] == pid:
            item['quantity'] = quantity
            break
    return '', 204  # Return empty response with 204 status code


@app.context_processor
def inject_total_items():
    # Get the cart from the session
    cart = session.get('cart', [])
    # Count occurrences of each product ID in the cart
    product_counts = Counter(item['pid'] for item in cart)
    # Total number of specific products in the cart
    total_items = len(product_counts)
    return dict(total_items=total_items)


    
@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price, thank_you=True)

    
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' in session:
        # Iterate over each item in the cart and insert into the sales table
        for item in session['cart']:
            sales = (item['pid'], item['quantity'], 'now()')
            insert_sales(sales)
        # After inserting sales, clear the cart
        session.pop('cart', None)
        return render_template('cart.html', thank_you=True)    # Redirect to the sales page or any other desired page
    else:
        return "Your cart is empty"


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
    line_chart = pygal.Bar()
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


@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html")

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
        role = 'user'  # Set the default role to 'user'
        hashed_password = generate_password_hash(password)
        users = (full_name, email, phone, hashed_password, 'now()', role)  # Include the role parameter
        if len(password) < 8:
            error1 = "Password should be at least 8 characters long."
        elif not any(char.isalpha() for char in password) or not any(char.isdigit() or char.isalnum() for char in password):
            error1 = "Password should contain letters and at least one number or symbol."
        elif email_exists(email):
            error1 = "This email already exists. Please choose a different email."
        else:
            add_user(users)
            sms_instance = SMS()
            sms_instance.send(full_name, phone)
            flash(f"Dear {full_name}, welcome! Your registration is successful. Please check your phone for a confirmation message.")
            return redirect('/login')
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
            role = user[5]  # Assuming role is stored at index 5 in the user tuple
            if db_email == email and check_password_hash(db_hashed_password, password):
                session['logged_in'] = True
                if role == 'admin':
                    return redirect('/admin')  # Redirect admin users to admin page
                else:
                    return redirect('/index')  # Redirect non-admin users to index page
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



# @app.context_processor
# def generate_barcode():
#     id_list = fetch_data("products")
#     barcode_paths = []
#     for pid_tuple in id_list:
#         pid = pid_tuple[0]
#         code = Code128(str(pid), writer=ImageWriter())
#         barcode_path = f"static/barcodes/{pid}.png"
#         code.save(barcode_path)
#         barcode_paths.append(barcode_path)
#     return {'barcode_paths': barcode_paths}

@app.context_processor
def generate_barcode():
    print("Generating barcodes...")  # Debug statement
    id_list = fetch_data("products")
    barcode_paths = []
    
    for pid_tuple in id_list:
        pid = pid_tuple[0]
        
        # Debug the `Code128` object before using it
        print(f"Creating barcode for PID: {pid}")
        try:
            code = Code128(str(pid), writer=ImageWriter())  # Try block
        except Exception as e:
            print(f"Error creating barcode for PID {pid}: {e}")
            continue
        
        barcode_path = f"static/barcodes/{pid}.png"
        code.save(barcode_path)
        barcode_paths.append(barcode_path)
    
    return {'barcode_paths': barcode_paths}



@app.route("/logout")
def logout():
    session.pop("username", None) 
    return redirect(url_for("login"))

def send_email(name, email, message):
    sender_email = "letinaroderick@gmail.com"  # Your email
    sender_password = "uill pfri islt yldd"  # Your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "letinaroderick@gmail.com"
    msg['Subject'] = "New Message from Contact Form"

    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/contact')
def contact():
    return render_template('index.html#contact')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    if send_email(name, email, message):
        return 'Message sent successfully!'
    else:
        return 'Error sending message. Please try again later.'


if __name__ == '__main__': 
    app.run(debug=True)
  
 
