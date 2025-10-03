import psycopg2

#Connect to database
connection = psycopg2.connect(
    host="localhost",
    database="sqli_db",
    user="postgres",
    password="250705",
)
connection.set_session(autocommit=True)

#Cursor

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
                username = '%s'
        """ % username)
        result = cursor.fetchone()

    if result is None:
        # User does not exist
        return False

    admin, = result
    return admin

#For testing
print(is_admin(input('')))
