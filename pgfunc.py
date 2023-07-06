import psycopg2, json


try:
    conn = psycopg2.connect("dbname= duka_june user=postgres password=1234")
    cur =conn.cursor()
except Exception as e:
    print(e)    

def fetch_data(tbname):
    try:
        q = "SELECT * FROM " + tbname + ";"
        cur.execute(q)
        records = cur.fetchall()
        return records 
    except Exception as e:
        return e
    
def insert_products(v):
    vs = str(v)
    q = "insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def update_products(vs):
    
    for product in vs:
        q = "UPDATE products SET name = '{name}', buying_price = {buying_price}, selling_price = {selling_price} WHERE id = {id}"
        .format(
            product[1], product[2], product[3], product[0]
        )
             
        cur.execute(q)
        conn.commit()
        return q
    


   
def insert_sales(v):
    vs = str(v)
    q = "insert into sales(pid,quantity, created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

   
def insert_stock(v):
    vs = str(v)
    q = "insert into stock(pid,quantity, created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def sales_per_day():
    q = "SELECT * FROM sale_per_month;"
    cur.execute(q)
    results =cur.fetchall()
    return results

def sales_per_products():
    q = " SELECT * FROM sales_per_product;"
    cur.execute(q)
    results = cur.fetchall()
    return results


def add_user(v):
    vs = str(v)
    q = "insert into users(full_name,email, password, confirm_password, created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def loginn(email, password):
     q="SELECT email, password FROM users;"
     cur.execute(q)
     results =cur.fetchall()
     return results




    









