from mysql.connector import Error

def excluir_produto_por_id(conn):
    print("\n" + "="*50)
    print("EXCLUSÃO PERMANENTE DE PRODUTO")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        while True:
            try:
                id_produto = int(input(" Digite o ID do produto a ser EXCLUÍDO (0 para cancelar): ").strip())
                if id_produto == 0:
                    print(" Operação cancelada.")
                    return
                if id_produto < 0:
                    print(" ID inválido.")
                    continue
                break
            except ValueError:
                print(" ID inválido. Digite um número inteiro.")
                
        confirmacao = input(f" ATENÇÃO: Confirma a EXCLUSÃO do produto ID {id_produto}? (sim/nao): ").strip().lower()
        if confirmacao != 'sim':
            print(" Exclusão cancelada.")
            return
        
        cursor.execute("SELECT nome_produto FROM produtos WHERE id_produto = %s", (id_produto,))
        produto_data = cursor.fetchone()
        
        if produto_data is None:
            print(f"Produto com ID {id_produto} não encontrado.")
            return

        nome_produto = produto_data[0]
        sql_delete = "DELETE FROM produtos WHERE id_produto = %s"
        cursor.execute(sql_delete, (id_produto,))

        if cursor.rowcount > 0:
            conn.commit()
            print(f"\n Produto '{nome_produto}' (ID: {id_produto}) EXCLUÍDO do sistema.")
        else:
            conn.rollback()
            print(f"\n Erro: Não foi possível excluir o produto ID {id_produto}.")
            
    except Error as e:
        conn.rollback()
        print(f"\n Erro ao excluir produto: {e}\n")
    except Exception as e:
        conn.rollback()
        print(f"\n Erro inesperado: {e}\n")
    finally:
        if cursor: 
            cursor.close()