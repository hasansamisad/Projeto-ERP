import matplotlib.pyplot as plt
import numpy as np  
from mysql.connector import Error

def obter_dados_abc(conn):
    cursor = conn.cursor()
    try:
        query = """
        SELECT 
            p.nome_produto,
            (p.preco * e.quantidade) AS custo_total
        FROM 
            produtos p
        INNER JOIN 
            estoque e ON p.id_produto = e.id_produto
        WHERE
            p.ativo = 1 AND e.quantidade > 0
        ORDER BY 
            custo_total DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f" Erro ao obter dados para Curva ABC: {e}")
        return []
    finally:
        cursor.close()

def obter_dados_evolucao_estoque(conn):
    cursor = conn.cursor()
    try:
        query = """
        SELECT 
            DATE_FORMAT(data_movimento, '%Y-%m') AS mes_ano, 
            SUM(CASE 
                WHEN tipo = 'ENTRADA' THEN quantidade 
                WHEN tipo = 'SAIDA' THEN -quantidade
                ELSE 0 
            END) AS saldo_net
        FROM movimentacoes
        GROUP BY mes_ano
        ORDER BY mes_ano;
        """
        cursor.execute(query)
        return cursor.fetchall() 
        
    except Error as e:
        print(f"Erro ao obter dados de evolução de estoque: {e}")
        return []
    finally:
        if cursor:
            cursor.close()

def obter_dados_categorias(conn):
   
    cursor = conn.cursor()
    try:
        query = """
        SELECT 
            COALESCE(c.nome_categoria, 'SEM CATEGORIA') AS nome_categoria,
            SUM(e.quantidade) AS total_estoque
        FROM produtos p
        INNER JOIN estoque e ON p.id_produto = e.id_produto
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE p.ativo = 1 AND e.quantidade > 0
        GROUP BY nome_categoria
        ORDER BY total_estoque DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao obter dados por categoria: {e}")
        return []
    finally:
        cursor.close()

def gerar_relatorios_graficos(conn):
    print("\n" + "="*80)
    print("                      GERAÇÃO DO DASHBOARD DE ESTOQUE")
    print("="*80)
    
    dados_abc = obter_dados_abc(conn)
    dados_categorias = obter_dados_categorias(conn)
    dados_evolucao = obter_dados_evolucao_estoque(conn)
    
    if not dados_abc and not dados_categorias and not dados_evolucao:
        print(" Sem dados suficientes para gerar qualquer relatório.")
        return
    
    fig = plt.figure(figsize=(18, 6))
    plt.suptitle('Dashboard de Acompanhamento de Estoque', fontsize=16, y=1.02)

    
    # ------------------------------------------------------------------
    # CURVA ABC (CUSTOS)
    # ------------------------------------------------------------------
    
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_title('Curva ABC de Custos')
    
    if dados_abc:
        nomes = [item[0] for item in dados_abc]
        custos = np.array([item[1] for item in dados_abc])
        custos_ordenados = np.sort(custos)[::-1]
        total_geral = custos_ordenados.sum()
        
        if total_geral > 0:
            custo_acumulado = np.cumsum(custos_ordenados)
            percentual_acumulado = (custo_acumulado / total_geral) * 100
        
            ax1.bar(nomes, custos_ordenados, color='blue', alpha=0.6)
            ax1.set_ylabel('Custo Total (R$)', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.tick_params(axis='x', rotation=45) 

            ax2 = ax1.twinx() 
            ax2.plot(nomes, percentual_acumulado, color='red', marker='o', linestyle='-', linewidth=2)
            ax2.axhline(80, color='red', linestyle='--', alpha=0.7)
            ax2.set_ylabel('Percentual Acumulado (%)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_ylim(0, 110)
        else:
            ax1.text(0.5, 0.5, 'Custo total zero.', ha='center', va='center', transform=ax1.transAxes)
    else:
        ax1.text(0.5, 0.5, 'Sem dados de custos de estoque.', ha='center', va='center', transform=ax1.transAxes)


    # ------------------------------------------------------------------
    # COMPARAÇÃO DE CATEGORIAS
    # ------------------------------------------------------------------
    
    ax3 = fig.add_subplot(1, 3, 2)
    ax3.set_title('Estoque por Categoria')
    
    if dados_categorias:
        categorias = [item[0] for item in dados_categorias]
        quantidades = [item[1] for item in dados_categorias]
        ax3.bar(categorias, quantidades, color='green', alpha=0.7)
        ax3.set_ylabel('Quantidade Total (Unidades)')
        ax3.tick_params(axis='x', rotation=45)
    else:
        ax3.text(0.5, 0.5, 'Sem dados de categorias para agrupar.', ha='center', va='center', transform=ax3.transAxes)


    # ------------------------------------------------------------------
    #  EVOLUÇÃO DO ESTOQUE (SALDO LÍQUIDO MENSAL)
    # ------------------------------------------------------------------

    ax4 = fig.add_subplot(1, 3, 3)
    ax4.set_title('Evolução do Saldo Líquido Mensal')
    
    if dados_evolucao:
        meses = [item[0] for item in dados_evolucao]
        saldo_net = np.array([item[1] for item in dados_evolucao])
        
        ax4.plot(meses, saldo_net, marker='o', linestyle='-', color='purple')
        ax4.axhline(0, color='black', linestyle='--', linewidth=0.8)
        ax4.set_xlabel('Mês/Ano')
        ax4.set_ylabel('Saldo Líquido (Entrada - Saída)')
        ax4.tick_params(axis='x', rotation=45)
    else:
        ax4.text(0.5, 0.5, 'Sem dados de movimentação histórica.', ha='center', va='center', transform=ax4.transAxes)

    plt.tight_layout() 
    plt.show()
