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
    q = "insert into products(name,buying_price,selling_price) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def update_products(vs):
        id = vs[0]
        name = vs[1]
        buying_price = vs[2]
        selling_price = vs[3]
        q = "UPDATE products SET name = %s, buying_price = %s, selling_price = %s WHERE id = %s"
        cur.execute(q, (name, buying_price, selling_price,id))
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
    q = "insert into stockk(pid,quantity, created_at) "\
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

def remaining_stock():
    q = " SELECT * FROM remaining_stock;"
    cur.execute(q)
    results = cur.fetchall()
    return results

def get_remaining_stock():
    q = """ SELECT sd.quantity - COALESCE(sum(sa.quantity), 0::bigint) AS remaining_stock
       FROM products p
       JOIN stock_duka sd ON p.id = sd.pid
       LEFT JOIN sales sa ON p.id = sa.pid
       WHERE p.id = sd.pid
       GROUP BY p.id, sd.quantity"""
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








    









