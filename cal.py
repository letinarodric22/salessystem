import calendar
year = 2000
month = 4
x = calendar.month(year, month)
print(x)

@app.route("/index", methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        search_query = request.args.get('search', default='', type=str)
        prods = fetch_data('products')
        prods = [p for p in prods if search_query.lower() in p[1].lower()]
        return render_template('index.html', search_query=search_query, prods=prods)