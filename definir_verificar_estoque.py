from mysql.connector import Error

def definir_e_verificar_estoque_seguranca(conn):
    print("\n" + "="*70)
    print("GESTÃO E MONITORAMENTO DO ESTOQUE DE SEGURANÇA")
    print("="*70)
    
    cursor = conn.cursor()
    
    try:    
        print("\n -- 1. Configurar Limites de Estoque --")
        
        while True:
            acao = input(" Deseja (D)efinir um limite ou apenas (M)onitorar o estoque? (D/M/0-Cancelar): ").strip().upper()
            if acao == '0':
                return
            if acao in ('D', 'M'):
                break
            print(" Opção inválida.")
        
        if acao == 'D':
            while True:
                try:
                    id_prod = int(input(" Digite o ID do produto para configurar: ").strip())
                    cursor.execute("SELECT nome_produto FROM produtos WHERE id_produto = %s", (id_prod,))

                    if cursor.fetchone() is None:
                        print(f" Produto com ID {id_prod} não encontrado.")
                        continue
                    
                    min_qnt = int(input(" Novo Estoque MÍNIMO (Segurança): ").strip())
                    max_qnt = int(input(" Novo Estoque MÁXIMO (Limite Superior): ").strip())
                    
                    if min_qnt < 0 or max_qnt < min_qnt:
                        print(" Limites inválidos. Mínimo não pode ser negativo e Máximo deve ser maior que o Mínimo.")
                        continue

                    sql_update = """
                    UPDATE produtos SET estoque_minimo = %s, estoque_maximo = %s 
                    WHERE id_produto = %s
                    """
                    cursor.execute(sql_update, (min_qnt, max_qnt, id_prod))
                    conn.commit()
                    print(f"\n Limites de estoque de segurança atualizados para o produto ID {id_prod}.")
                    break          
                except ValueError:
                    print("Entrada inválida. Digite um número inteiro.")
                except Error as e:
                    print(f"Erro ao atualizar o produto: {e}")
                    conn.rollback()
        print("\n -- 2. Status Atual do Estoque de Segurança --")
        
        sql_monitor = """
        SELECT 
            p.id_produto, 
            p.nome_produto, 
            e.quantidade, 
            p.estoque_minimo, 
            p.estoque_maximo
        FROM 
            produtos p
        INNER JOIN 
            estoque e ON p.id_produto = e.id_produto
        WHERE 
            p.ativo = 1
        ORDER BY
            p.nome_produto ASC
        """
        cursor.execute(sql_monitor)
        resultados = cursor.fetchall()
        
        if not resultados:
            print(" Nenhum produto ativo com dados de estoque para monitorar.")
            return

        print(f"\n{'ID':<5} | {'PRODUTO':<30} | {'ESTOQUE ATUAL':>15} | {'MÍNIMO':>10} | {'MÁXIMO':>10} | {'STATUS':<20}")
        print("-" * 100)
        
        for id_prod, nome, atual, min_qnt, max_qnt in resultados:
            status = ""
            
            if atual < min_qnt:
                status = "ABAIXO DO MÍNIMO (COMPRAR!)"
            elif atual > max_qnt:
                status = "ACIMA DO MÁXIMO (EXCESSO!)"
            else:
                status = "OK (Nível Seguro)"
            
            print(f"{id_prod:<5} | {nome:<30} | {atual:>15} | {min_qnt:>10} | {max_qnt:>10} | {status:<20}")
            
        print("-" * 100)

    except Error as e:
        print(f"\n Erro geral de acesso ao banco de dados: {e}\n")
    finally:
        cursor.close()
