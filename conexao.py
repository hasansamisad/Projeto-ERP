import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "erp_user",
    "password": "senha123",
    "database": "mercado"
}

def criar_conexao():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=False  
        )
        
        if conn.is_connected():
            print("Conexão estabelecida com o banco de dados!")
            return conn
        return None
        
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None