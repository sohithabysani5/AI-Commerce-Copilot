from database import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM products")

products = cursor.fetchall()

for product in products:
    print(product)

connection.close()