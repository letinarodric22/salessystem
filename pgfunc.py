import psycopg2
# psycopg2 is a popular Python adapter for PostgreSQL that allows you to interact with PostgreSQL databases using Python code

try:
    conn = psycopg2.connect("dbname= inventory user=postgres password=1234")
    cur =conn.cursor()
except Exception as e: 
    print(e)    


def fetch_product(pid):
    cur.execute("SELECT * FROM products WHERE id = %s", (pid,))
    return cur.fetchone()


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
    q = "insert into products(name,buying_price,selling_price, image_url,category) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def update_products(vs):
        id = vs[0]
        name = vs[1]
        buying_price = vs[2]
        selling_price = vs[3]
        image_url = vs[4]
        category = vs[5]
        q = "UPDATE products SET name = %s, buying_price = %s, selling_price = %s, image_url = %s, category = %s WHERE id = %s"
        cur.execute(q, (name, buying_price, selling_price, image_url,category,id))
        conn.commit()
        return q

def delete_product(id):
    # Delete referencing records in the "stocks" table first
    q_delete_stocks = "DELETE FROM stocks WHERE pid = %s;"
    cur.execute(q_delete_stocks, (id,))

   # Delete referencing records in the "stocks" table first
    q_delete_sales = "DELETE FROM sales WHERE pid = %s;"
    cur.execute(q_delete_sales, (id,))

    # Now, delete the record in the "products" table
    q_delete_product = "DELETE FROM products WHERE id = %s;"
    cur.execute(q_delete_product, (id,))
    conn.commit()


    
def insert_sales(v):
    vs = str(v)
    q = "insert into sales(pid,quantity, created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

   
def insert_stock(v):
    vs = str(v)
    q = "insert into stocks(pid,quantity, created_at) "\
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


def get_remaining_stock(product_id=None):
    q = """ SELECT 
            COALESCE(st.stock_quantity, 0) - COALESCE(sa.sales_quantity, 0) AS closing_stock
            FROM
                (SELECT pid, SUM(quantity) AS stock_quantity FROM stocks GROUP BY pid) AS st
            LEFT JOIN
                (SELECT pid, SUM(quantity) AS sales_quantity FROM sales GROUP BY pid) AS sa
            ON st.pid = sa.pid
            WHERE st.pid = %s
            GROUP BY st.stock_quantity,sa.sales_quantity;"""
    cur.execute(q, (product_id,))
    results = cur.fetchall()
    if results:
        return results[0]
    else:
        return None
    

def add_user(v):
    vs = str(v)
    q = "insert into users(full_name,email,phone, h_password, created_at,role) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

def revenue_per_day():
    q = "SELECT TO_CHAR(s.created_at, 'DD-MM-YYYY') AS sale_month, SUM(s.quantity * p.selling_price) AS revenue FROM sales s JOIN products p ON s.pid = p.id GROUP BY TO_CHAR(s.created_at, 'DD-MM-YYYY');;"
    cur.execute(q)
    results = cur.fetchall()
    return results

def revenue_per_month():
    q = "SELECT TO_CHAR(s.created_at, 'MM-YYYY') AS sale_month, SUM(s.quantity * p.selling_price) AS revenue FROM sales s JOIN products p ON s.pid = p.id GROUP BY TO_CHAR(s.created_at, 'MM-YYYY');"
    cur.execute(q)
    results = cur.fetchall()
    return results







    









