from mysql.connector import Error

def listar_produtos_com_estoque(conn):
    
    print("\n" + "="*95) 
    print("CATÁLOGO DE PRODUTOS E ESTOQUE")
    print("="*95)
    
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            p.id_produto,
            p.nome_produto,
            c.nome_categoria, -- NOVO: Seleciona o nome da categoria
            p.preco,
            e.quantidade,
            p.unidade 
        FROM 
            produtos p
        INNER JOIN 
            estoque e ON p.id_produto = e.id_produto
        LEFT JOIN -- Garante que produtos sem categoria (id_categoria NULL) também sejam listados
            categorias c ON p.id_categoria = c.id_categoria
        WHERE
            p.ativo = 1
        ORDER BY 
            p.nome_produto ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        if not resultados:
            print(" Nenhum produto ativo cadastrado.\n")
            return
        
        print(f"\n{'ID':<5} | {'PRODUTO':<30} | {'CATEGORIA':<20} | {'PREÇO':>10} | {'ESTOQUE':>10} | {'UNIDADE':<8}")
        print("-" * 95)
        
        total_valor = 0
        for id_produto, nome, nome_categoria, preco, quantidade, unidade in resultados:
            valor_total = preco * quantidade
            total_valor += valor_total
            categoria_exibir = nome_categoria if nome_categoria else "Sem Categoria"
            
            print(f"{id_produto:<5} | {nome:<30} | {categoria_exibir:<20} | R$ {preco:>8.2f} | {quantidade:>10} | {unidade:<8}")
        
        print("-" * 95)
        print(f"{'VALOR TOTAL EM ESTOQUE:':<68} R$ {total_valor:>8.2f}\n")
            
    except Error as e:
        print(f"\n Erro ao listar produtos: {e}\n")
    finally:
        cursor.close()
