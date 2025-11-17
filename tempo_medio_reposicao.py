from mysql.connector import Error
from datetime import timedelta

def analisar_tempo_medio_reposicao(conn):

    print("\n" + "="*50)
    print("TEMPO MÉDIO DE REPOSIÇÃO (LEAD TIME)")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        sql_entradas = """
        SELECT 
            id_produto, 
            data_movimento 
        FROM 
            movimentacoes 
        WHERE 
            tipo = 'ENTRADA'
        ORDER BY 
            id_produto ASC, data_movimento ASC
        """
        cursor.execute(sql_entradas)
        entradas = cursor.fetchall()

        if not entradas:
            print(" Não há registros de ENTRADA para calcular o TMR.")
            return
        sql_nome = "SELECT nome_produto FROM produtos WHERE id_produto = %s"
        resultados_tmr = {}    
        id_produto_anterior = None
        data_entrada_anterior = None
        
        for id_produto, data_atual in entradas:
            if id_produto == id_produto_anterior and data_entrada_anterior is not None:
                diferenca: timedelta = data_atual - data_entrada_anterior
                intervalo_dias = diferenca.total_seconds() / (60 * 60 * 24)        
                if id_produto not in resultados_tmr:
                    resultados_tmr[id_produto] = []
                resultados_tmr[id_produto].append(intervalo_dias)

            id_produto_anterior = id_produto
            data_entrada_anterior = data_atual

        print("\n -- Resultados do Tempo Médio de Reposição (TMR) --")
        print(f"\n{'ID':<5} | {'PRODUTO':<30} | {'TMR MÉDIO (DIAS)':>18} | {'Nº de Reposições':>18}")
        print("-" * 75)
        
        tmr_encontrado = False
        
        for id_prod, intervalos in resultados_tmr.items():
            if len(intervalos) > 0:
                cursor.execute(sql_nome, (id_prod,))
                nome_produto = cursor.fetchone()[0]
                
                tmr_medio = sum(intervalos) / len(intervalos)
                
                print(f"{id_prod:<5} | {nome_produto:<30} | {tmr_medio:>18.2f} | {len(intervalos):>18}")
                tmr_encontrado = True
                
        if not tmr_encontrado:
            print("Não há dados suficientes (pelo menos duas entradas por produto) para calcular o TMR.")
        
        print("-" * 75)

    except Error as e:
        print(f"\n Erro ao analisar o TMR: {e}\n")
    finally:
        cursor.close()