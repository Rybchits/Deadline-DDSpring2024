from src.db.connection import conn

def run_sql(sql, data=None):
    cur = conn.cursor()

    try:
        cur.execute(sql, data or ())
    except Exception as e:
        conn.commit()
        print(e)
        return None

    result = None
    try: 
        result = cur.fetchall()
    except Exception as e:
        print(e)

    conn.commit()
    return result