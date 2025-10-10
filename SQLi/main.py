import psycopg2

#Connect to database
connection = psycopg2.connect(
    host="localhost",
    database="sqli_db",
    user="postgres",
    password="250705",
)
connection.set_session(autocommit=True)

#Cursor VV Unused code

#with connection.cursor() as cursor:
#    cursor.execute('SELECT COUNT(*) FROM users')
#    result =  cursor.fetchone()
#print(result)

#Cursor

def is_admin(username: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                admin
            FROM
                users
            WHERE
                username = %(username)s
        """, {
            'username': username
        })
        result = cursor.fetchone()

    if result is None:
        # User does not exist
        return False

    admin, = result
    return admin

#SQL Composition
from psycopg2 import sql

def count_rows(table_name: str, limit: int) -> int:
    with connection.cursor() as cursor:
        stmt = sql.SQL("""
            SELECT
                COUNT(*)
            FROM (
                SELECT
                    1
                FROM
                    {table_name}
                LIMIT
                    {limit}
            ) AS limit_query
        """).format(
            table_name = sql.Identifier(table_name),
            limit = sql.Literal(limit),
        )
        cursor.execute(stmt)
        result = cursor.fetchone()

    rowcount, = result
    return rowcount

#Test Query
#cursor.execute("SELECT admin FROM users WHERE username = '" + username + '")
#cursor.execute("SELECT admin FROM users WHERE username = '%s' % username)
#cursor.execute("SELECT admin FROM users WHERE username = '{}'".format(username))
#cursor.execute(f"SELECT admin FROM users WHERE username = '{username}'")

#Test Query
#cursor.execute("SELECT admin FROM users WHERE username = %s'", (username, ))
#cursor.execute("SELECT admin FROM users WHERE username = %(username)s", {'username': username})

with connection.cursor as cursor:
    #cursor.execute("SELECT admin FROM users WHERE username =  + " username " + ")

    cursor.execute("SELECT admin FROM users WHERE username = %s'", (username, ))
    cursor.execute("SELECT admin FROM users WHERE username = %(username)s", {'username': username})

#Output
print(is_admin(input('')))
print(count_rows(input('')))
