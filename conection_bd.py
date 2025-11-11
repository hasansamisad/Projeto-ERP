# db.py
import mysql.connector
from mysql.connector import Error

def criar_conexao():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.
    Retorna:
        conexao (mysql.connector.connection.MySQLConnection) ou None
    """
    try:
        conexao = mysql.connector.connect(
            host='localhost',       # endereço do servidor MySQL
            user='erp_user',            # nome de usuário do MySQL
            password='senha123',   # senha do MySQL
            database='erp'          # nome do banco de dados
        )

        if conexao.is_connected():
            print("✅ Conexão bem-sucedida com o banco de dados!")
            return conexao

    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None


def fechar_conexao(conexao):
    """
    Fecha a conexão com o banco, se estiver aberta.
    """
    if conexao and conexao.is_connected():
        conexao.close()
        print("🔒 Conexão encerrada com sucesso.")
