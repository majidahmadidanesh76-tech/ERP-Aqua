import sys
from PyQt5 import QtWidgets
import mysql.connector

app = QtWidgets.QApplication(sys.argv)

widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(widget)

combo = QtWidgets.QComboBox()
combo.addItem("همه تجهیزات", None)

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='erp_aqua'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, display_name FROM equipment_types ORDER BY display_name")
    equipments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for eq in equipments:
        display_text = eq.get('display_name', eq.get('name', ''))
        combo.addItem(display_text, eq.get('name'))
        print(f"اضافه شد: {display_text}")
        
except Exception as e:
    print(f"خطا: {e}")

layout.addWidget(combo)
widget.show()
sys.exit(app.exec_())