from src.db.connection import conn, POOL


def run_sql(sql, data=None):
    cur = conn.cursor()

    try:
        cur.execute(sql, data or ())
    except Exception as e:
        conn.commit()
        print(e)
        return None

    try: 
        result = cur.fetchall()
    except Exception as e:
        print(e)

    conn.commit()
    return result


async def async_sql(sql, data=None):
    args = data or ()
    recs = None

    print(sql, "|", *args)

    try:
        async with POOL[0].acquire() as conn:
            async with conn.transaction():
                recs = await conn.fetch(sql, *args)
    except Exception as e:
        print(e)

    return recs
