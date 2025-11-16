from mysql.connector import Error

def analisar_giro_estoque(conn):

    print("\n" + "="*50)
    print(" ANÁLISE DE GIRO DE ESTOQUE")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        sql_dados_base = """
        SELECT 
            p.id_produto, 
            p.nome_produto, 
            p.preco, 
            e.quantidade AS estoque_atual,
            c.nome_categoria
        FROM 
            produtos p
        INNER JOIN 
            estoque e ON p.id_produto = e.id_produto
        LEFT JOIN
            categorias c ON p.id_categoria = c.id_categoria
        WHERE 
            p.ativo = 1
        """
        cursor.execute(sql_dados_base)
        produtos_base = cursor.fetchall()

        if not produtos_base:
            print(" Nenhum produto ativo encontrado para análise.")
            return
        
        sql_saidas_totais = """
        SELECT 
            id_produto, 
            SUM(quantidade) AS total_saidas 
        FROM 
            movimentacoes 
        WHERE 
            tipo = 'SAIDA' 
        GROUP BY 
            id_produto
        """
        cursor.execute(sql_saidas_totais)
        saidas_por_produto = {row[0]: row[1] for row in cursor.fetchall()}
        giro_total_cmv = 0.0
        giro_total_estoque_atual = 0.0
        produtos_para_exibir = []

        for id_produto, nome, preco, estoque_atual, nome_categoria in produtos_base:
            custo_produto = preco 
            total_saidas = saidas_por_produto.get(id_produto, 0)
            
            cmv_produto_decimal = total_saidas * custo_produto
            valor_estoque_atual_decimal = estoque_atual * custo_produto
            
            giro_total_cmv += float(cmv_produto_decimal)
            giro_total_estoque_atual += float(valor_estoque_atual_decimal)

            cmv_produto_float = float(cmv_produto_decimal)
            valor_estoque_atual_float = float(valor_estoque_atual_decimal)
            
            giro_produto = (cmv_produto_float / valor_estoque_atual_float) if valor_estoque_atual_float > 0 else 0
            
            produtos_para_exibir.append({
                'id': id_produto,
                'nome': nome,
                'categoria': nome_categoria if nome_categoria else "Sem Categoria",
                'saidas': total_saidas,
                'estoque': estoque_atual,
                'giro': giro_produto
            })
       
        giro_estoque_total = (giro_total_cmv / giro_total_estoque_atual) if giro_total_estoque_atual > 0 else 0
   
        print("\n" + "="*50)
        print(f"Custo das Mercadorias Vendidas (CMV): R$ {giro_total_cmv:.2f}")
        print(f"Valor Total do Estoque Atual: R$ {giro_total_estoque_atual:.2f}")
        print("-" * 50)
        print(f"GIRO DE ESTOQUE GLOBAL:{giro_estoque_total:.2f} vezes")
        print("="*50)
        print("\n -- Giro de Estoque por Produto --")
        print(f"\n{'ID':<5} | {'PRODUTO':<30} | {'SAÍDAS':>8} | {'ESTOQUE':>8} | {'GIRO':>8} | {'CATEGORIA':<15}")
        print("-" * 90)

        produtos_para_exibir.sort(key=lambda x: x['giro'], reverse=True)
        
        for p in produtos_para_exibir:
            giro_formatado = f"{p['giro']:.2f}" if p['estoque'] > 0 else "N/A"
            
            print(f"{p['id']:<5} | {p['nome']:<30} | {p['saidas']:>8} | {p['estoque']:>8} | {giro_formatado:>8} | {p['categoria']:<15}")
            
        print("-" * 90)


    except Error as e:
        print(f"\n Erro ao analisar o giro de estoque: {e}\n")
    finally:
        cursor.close()