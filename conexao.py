import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="erp_user",
    password="senha123",
    database="mercado"
)

if conn.is_connected():
    print("Conectado!")
