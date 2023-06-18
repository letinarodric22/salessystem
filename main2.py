import psycopg2

try:
    conn = psycopg2.connect("dbname= duka_june user=postgres password=1234")
    cur = conn.cursor()
except Exception as e:
    print(e)


def fetch_data(tbln):
    try:
        allowed_tables = ['products', 'sales' ]  
        if tbln in allowed_tables:
            q = "SELECT * FROM {}".format(tbln)
            cur.execute(q)
            records = cur.fetchall()
            return records
        else:
            return "Invalid table name"
    except Exception as e:
        return str(e)

def insert_sales(vs):
    try:
        q = "INSERT INTO sales (id, pid, quantity, created_at) VALUES (%s, %s, %s, %s)"
        cur.execute(q, vs)
        conn.commit()
        return "Sales successfully added"
    except Exception as e:
        return str(e)