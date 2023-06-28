import psycopg2


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


   
def insert_sales(v):
    vs = str(v)
    q = "insert into sales(pid,quantity, created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def sales_per_day():
    q = "SELECT substring(TO_CHAR(created_at, 'MM-YYYY'),1,7) as m, SUM(quantity) as total_sales FROM sales GROUP BY m ORDER BY m;"
    cur.execute(q)
    results =cur.fetchall()
    return results

def sales_per_products():
    q = " SELECT p.name, COUNT(s.*) AS total_sales FROM products p JOIN sales s ON p.id = s.pid GROUP BY p.name"
    cur.execute(q)
    results = cur.fetchall()
    return results








