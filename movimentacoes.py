from mysql.connector import Error
from datetime import datetime

def registrar_movimentacao(conn):
   
    print("\n" + "="*50)
    print("      REGISTRO DE MOVIMENTAÇÃO DE ESTOQUE")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        while True:
            try:
                id_prod = int(input("\n Digite o ID do produto: ").strip())
                break
            except ValueError:
                print(" ID inválido. Digite um número inteiro.")

        while True:
            tipo = input(" Tipo de movimento (E=ENTRADA / S=SAÍDA): ").strip().upper()
            if tipo in ('E', 'S'):
                break
            print(" Digite 'E' para ENTRADA ou 'S' para SAÍDA.")

        while True:
            try:
                quantidade = int(input(" Quantidade: ").strip())
                if quantidade <= 0:
                    print(" Quantidade deve ser maior que zero.")
                    continue
                break
            except ValueError:
                print(" Quantidade inválida. Digite um número inteiro.")
        
        tipo_completo = "ENTRADA" if tipo == 'E' else "SAIDA"
        
        sql_check = "SELECT quantidade FROM estoque WHERE id_produto = %s FOR UPDATE"
        cursor.execute(sql_check, (id_prod,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            print(f"\n Produto com ID {id_prod} não encontrado no estoque.\n")
            conn.rollback() 
            return 
        
        quantidade_atual = resultado[0]
        
        if tipo == 'S' and quantidade_atual < quantidade:
            print(f"\n ESTOQUE INSUFICIENTE!")
            print(f"   Quantidade em estoque: {quantidade_atual}")
            print(f"   Quantidade solicitada: {quantidade}\n")
            conn.rollback() 
            return 
        
        if tipo == 'E':
            sql_update = "UPDATE estoque SET quantidade = quantidade + %s WHERE id_produto = %s"
        else: 
            sql_update = "UPDATE estoque SET quantidade = quantidade - %s WHERE id_produto = %s"
        
        cursor.execute(sql_update, (quantidade, id_prod))
        
        sql_mov = """
        INSERT INTO movimentacoes (id_produto, tipo, quantidade) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_mov, (id_prod, tipo_completo, quantidade))
        conn.commit()
        cursor.execute("SELECT quantidade FROM estoque WHERE id_produto = %s", (id_prod,))
        novo_saldo = cursor.fetchone()[0]
  
        print("\n" + " MOVIMENTAÇÃO REGISTRADA COM SUCESSO!")
        print(f"   Tipo: {tipo_completo}")
        print(f"   Quantidade movimentada: {quantidade}")
        print(f"   Saldo anterior: {quantidade_atual}")
        print(f"   Saldo atual: {novo_saldo}")
        print(f"   Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
    except Error as e:
        conn.rollback() 
        print(f"\n Erro na movimentação: {e}\n")
    except Exception as e:
        conn.rollback() 
        print(f"\n Erro inesperado: {e}\n")
    finally:
        if cursor: 
            cursor.close()
