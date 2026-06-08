import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='erp_aqua'
)

cursor = conn.cursor(dictionary=True)

# تست جدول equipment_types
cursor.execute("SELECT * FROM equipment_types")
results = cursor.fetchall()
print("=== equipment_types ===")
for row in results:
    print(row)

cursor.close()
conn.close()