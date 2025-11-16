import mysql.connector
from mysql.connector import Error
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_CONFIG = {
    "host": "localhost",
    "user": "erp_user",
    "password": "senha123",
    "database": "mercado"
}

# =====================================================================
# FUNÇÃO 1: CONEXÃO COM O BANCO DE DADOS
# =====================================================================
def criar_conexao():
    """
    Estabelece conexão com MySQL em modo transacional.
    Retorna a conexão ou None em caso de erro.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=False  # Desativa autocommit para controlar transações manualmente
        )
        
        if conn.is_connected():
            print("Conexão estabelecida com o banco de dados!")
            return conn
        return None
        
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


# =====================================================================
# FUNÇÃO 2: INICIALIZAÇÃO DO BANCO DE DADOS
# =====================================================================

def inicializar_banco(conn):
    """
    Cria as tabelas necessárias se não existirem:
    - categorias: armazena grupos de produtos (NOVO)
    - produtos: armazena informações do produto (ATUALIZADO com FK de categoria)
    - estoque: armazena quantidade em estoque
    - movimentacoes: histórico de entrada/saída
    """
    cursor = conn.cursor()
    
    try:
        # 1. NOVO: Tabela CATEGORIAS (Para agrupar produtos)
        sql_categorias = """
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nome_categoria VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_categorias)

        # 2. Tabela PRODUTOS (ATUALIZADA para incluir a Chave Estrangeira de Categoria)
        sql_produtos = """
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INT AUTO_INCREMENT PRIMARY KEY,
            nome_produto VARCHAR(100) NOT NULL UNIQUE,
            preco DECIMAL(10, 2) NOT NULL CHECK (preco > 0),
            unidade VARCHAR(20) NOT NULL DEFAULT 'unidade',
            
            -- NOVO CAMPO: Chave estrangeira para categorias
            id_categoria INT NULL, 
            
            ativo TINYINT(1) NOT NULL DEFAULT 1,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- NOVA FOREIGN KEY: Vincula o produto à categoria
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_produtos)
        
        # 3. Tabela ESTOQUE (Sem alterações necessárias)
        sql_estoque = """
        CREATE TABLE IF NOT EXISTS estoque (
            id_produto INT PRIMARY KEY,
            quantidade INT NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_estoque)
        
        # 4. Tabela MOVIMENTACOES (Sem alterações necessárias)
        sql_movimentacoes = """
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id_movimento INT AUTO_INCREMENT PRIMARY KEY,
            id_produto INT NOT NULL,
            tipo ENUM('ENTRADA', 'SAIDA') NOT NULL,
            quantidade INT NOT NULL CHECK (quantidade > 0),
            data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacoes VARCHAR(255),
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_movimentacoes)
        
        conn.commit()
        print("Tabelas verificadas/criadas com sucesso.\n")
        
    except Error as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()


# =====================================================================
# FUNÇÃO 3: CADASTRO DE PRODUTOS
# =====================================================================

def inserir_produto_por_input(conn):
    """
    Cadastra um novo produto, incluindo a seleção de Categoria.
    - Nome do produto
    - Preço unitário
    - Quantidade inicial em estoque
    - Unidade de medida
    - Categoria (NOVO)
    """
    print("\n" + "="*50)
    print("           CADASTRO DE NOVO PRODUTO")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        # Coleta e validação: NOME
        while True:
            nome_produto = input(" Nome do produto: ").strip()
            if not nome_produto or len(nome_produto) < 3:
                print("Nome deve ter pelo menos 3 caracteres.")
                continue
            break
        
        # Coleta e validação: PREÇO
        while True:
            try:
                preco_str = input("Preço unitário (R$): ").strip().replace(',', '.')
                preco = float(preco_str)
                if preco <= 0:
                    print(" Preço deve ser maior que zero.")
                    continue
                break
            except ValueError:
                print(" Preço inválido. Digite um número válido.")
        
        # Coleta e validação: QUANTIDADE
        while True:
            try:
                quantidade = int(input("Quantidade inicial em estoque: ").strip())
                if quantidade < 0:
                    print(" Quantidade não pode ser negativa.")
                    continue
                break
            except ValueError:
                print(" Quantidade inválida. Digite um número inteiro.")
        
        # Coleta e validação: UNIDADE
        while True:
            unidade = input("Unidade (kg, L, un, caixa, etc.): ").strip().lower()
            if not unidade or len(unidade) < 1:
                print("Unidade não pode ser vazia.")
                continue
            break
        
        # -----------------------------------------------
        # NOVO: SELEÇÃO DE CATEGORIA
        # -----------------------------------------------
        
        # 1. Busca categorias existentes
        cursor.execute("SELECT id_categoria, nome_categoria FROM categorias ORDER BY nome_categoria")
        categorias = cursor.fetchall()
        
        id_categoria = None # Valor padrão NULL para o banco
        nome_categoria_selecionada = "Sem Categoria"
        
        if categorias:
            print("\n -- Seleção de Categoria --")
            for id_c, nome_c in categorias:
                print(f" 📦 {id_c}: {nome_c}")
            print(" 0: Sem Categoria (Opcional)")
            
            while True:
                try:
                    escolha_cat = input("Escolha o ID da Categoria (0 para ignorar): ").strip()
                    
                    if escolha_cat == '0' or escolha_cat == '':
                        break # Mantém id_categoria = None
                    
                    id_selecionado = int(escolha_cat)
                    
                    # Validação e atribuição
                    categoria_encontrada = next((c for c in categorias if c[0] == id_selecionado), None)
                    
                    if categoria_encontrada:
                        id_categoria = id_selecionado
                        nome_categoria_selecionada = categoria_encontrada[1]
                        break
                    else:
                        print(f" ❌ ID de categoria {id_selecionado} inválido. Tente novamente.")
                except ValueError:
                    print(" ❌ Entrada inválida. Digite um número.")
        else:
            print(" ℹ️  Nenhuma categoria cadastrada. O produto será adicionado sem categoria.")

        # -----------------------------------------------
        # 1. Insere o produto (SQL ATUALIZADO)
        # -----------------------------------------------
        sql_produto = """
        INSERT INTO produtos (nome_produto, preco, unidade, id_categoria, ativo) 
        VALUES (%s, %s, %s, %s, 1)
        """
        # Note que id_categoria será None se o usuário escolheu 0 ou ignorou.
        cursor.execute(sql_produto, (nome_produto, preco, unidade, id_categoria))
        id_produto = cursor.lastrowid
        
        # 2. Insere estoque inicial
        sql_estoque = """
        INSERT INTO estoque (id_produto, quantidade) 
        VALUES (%s, %s)
        """
        cursor.execute(sql_estoque, (id_produto, quantidade))
        
        conn.commit()
        
        # -----------------------------------------------
        # Exibe resultado final
        # -----------------------------------------------
        print("\n" + " ✅ Produto cadastrado com sucesso!")
        print(f"   ID: {id_produto}")
        print(f"   Nome: {nome_produto}")
        print(f"   Preço: R$ {preco:.2f}")
        print(f"   Estoque Inicial: {quantidade} {unidade}")
        print(f"   Categoria: {nome_categoria_selecionada}\n")
        
    except Error as e:
        conn.rollback() # Desfaz o produto e o estoque em caso de erro
        if "Duplicate entry" in str(e) and nome_produto:
            print(f"\n ❌ Erro: Já existe um produto com o nome '{nome_produto}'.\n")
        elif "Cannot add or update a child row" in str(e):
             print(f"\n ❌ Erro: O ID de Categoria selecionado ({id_categoria}) não existe.\n")
        else:
            print(f"\n ❌ Erro ao cadastrar produto: {e}\n")
    except Exception as e:
        conn.rollback()
        print(f"\n ❌ Erro inesperado: {e}\n")
    finally:
        cursor.close()
# =====================================================================
# FUNÇÃO 4: LISTAGEM DE PRODUTOS E ESTOQUE
# =====================================================================
def listar_produtos_com_estoque(conn):
    """
    Exibe todos os produtos ativos com:
    - ID do produto
    - Nome
    - Preço
    - Quantidade em estoque
    - Unidade
    """
    print("\n" + "="*80)
    print("                    CATÁLOGO DE PRODUTOS E ESTOQUE")
    print("="*80)
    
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            p.id_produto,
            p.nome_produto,
            p.preco,
            e.quantidade,
            p.unidade 
        FROM 
            produtos p
        INNER JOIN 
            estoque e ON p.id_produto = e.id_produto
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

        # Cabeçalho da tabela
        print(f"\n{'ID':<5} | {'PRODUTO':<35} | {'PREÇO':>10} | {'ESTOQUE':>10} | {'UNIDADE':<8}")
        print("-" * 80)
        
        # Linhas de dados
        total_valor = 0
        for id_produto, nome, preco, quantidade, unidade in resultados:
            valor_total = preco * quantidade
            total_valor += valor_total
            print(f"{id_produto:<5} | {nome:<35} | R$ {preco:>8.2f} | {quantidade:>10} | {unidade:<8}")
        
        print("-" * 80)
        print(f"{'VALOR TOTAL EM ESTOQUE:':<55} R$ {total_valor:>8.2f}\n")
            
    except Error as e:
        print(f"\n Erro ao listar produtos: {e}\n")
    finally:
        cursor.close()


# =====================================================================
# FUNÇÃO 5: REGISTRO DE MOVIMENTAÇÃO (ENTRADA/SAÍDA)
# =====================================================================
def registrar_movimentacao(conn):
    """
    Registra entrada ou saída de estoque, garantindo atomicidade e concorrência.
    """
    print("\n" + "="*50)
    print("      REGISTRO DE MOVIMENTAÇÃO DE ESTOQUE")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        # Coleta e validação: ID DO PRODUTO
        while True:
            try:
                id_prod = int(input("\n Digite o ID do produto: ").strip())
                break
            except ValueError:
                print(" ID inválido. Digite um número inteiro.")
        
        # Coleta e validação: TIPO DE MOVIMENTO
        while True:
            tipo = input(" Tipo de movimento (E=ENTRADA / S=SAÍDA): ").strip().upper()
            if tipo in ('E', 'S'):
                break
            print(" Digite 'E' para ENTRADA ou 'S' para SAÍDA.")
        
        # Coleta e validação: QUANTIDADE
        while True:
            try:
                quantidade = int(input("📊 Quantidade: ").strip())
                if quantidade <= 0:
                    print(" Quantidade deve ser maior que zero.")
                    continue
                break
            except ValueError:
                print(" Quantidade inválida. Digite um número inteiro.")
        
        tipo_completo = "ENTRADA" if tipo == 'E' else "SAÍDA"
        
        sql_check = "SELECT quantidade FROM estoque WHERE id_produto = %s FOR UPDATE"
        cursor.execute(sql_check, (id_prod,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            print(f"\n Produto com ID {id_prod} não encontrado no estoque.\n")
            conn.rollback() # Desfaz o início da transação implícita
            return # Não fecha o cursor aqui
        
        quantidade_atual = resultado[0]
        
        # Etapa 2: Validação de quantidade para SAÍDA
        if tipo == 'S' and quantidade_atual < quantidade:
            print(f"\n ESTOQUE INSUFICIENTE!")
            print(f"   Quantidade em estoque: {quantidade_atual}")
            print(f"   Quantidade solicitada: {quantidade}\n")
            conn.rollback() # Desfaz a transação
            return # Não fecha o cursor aqui
        
        # Etapa 3: Atualiza o estoque
        if tipo == 'E':
            sql_update = "UPDATE estoque SET quantidade = quantidade + %s WHERE id_produto = %s"
        else: # SAÍDA
            sql_update = "UPDATE estoque SET quantidade = quantidade - %s WHERE id_produto = %s"
        
        cursor.execute(sql_update, (quantidade, id_prod))
        
        # Etapa 4: Registra no histórico
        sql_mov = """
        INSERT INTO movimentacoes (id_produto, tipo, quantidade) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_mov, (id_prod, tipo_completo, quantidade))
        
        # Etapa 5: Commit (persiste as duas operações: UPDATE + INSERT)
        conn.commit()
        
        # Etapa 6: Obtém novo saldo
        # É necessário re-executar a consulta após o commit para obter o valor atualizado.
        cursor.execute("SELECT quantidade FROM estoque WHERE id_produto = %s", (id_prod,))
        novo_saldo = cursor.fetchone()[0]
        
        # Exibe resultado
        print("\n" + " MOVIMENTAÇÃO REGISTRADA COM SUCESSO!")
        print(f"   Tipo: {tipo_completo}")
        print(f"   Quantidade movimentada: {quantidade}")
        print(f"   Saldo anterior: {quantidade_atual}")
        print(f"   Saldo atual: {novo_saldo}")
        print(f"   Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
    except Error as e:
        conn.rollback() # Desfaz qualquer operação em caso de erro no BD
        print(f"\n Erro na movimentação: {e}\n")
    except Exception as e:
        conn.rollback() # Desfaz em caso de erro inesperado (ex: erro de tipo)
        print(f"\n Erro inesperado: {e}\n")
    finally:
        # Garante que o cursor seja fechado, independentemente do resultado
        if cursor: 
            cursor.close()

# =====================================================================
# FUNÇÃO AUXILIAR: BUSCA DE DADOS PARA CURVA ABC (Mantida)
# =====================================================================

def obter_dados_abc(conn):
    """ Busca o custo total de estoque por produto. """
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

# =====================================================================
# FUNÇÃO AUXILIAR: BUSCA DE DADOS PARA EVOLUÇÃO (NOVA)
# =====================================================================

def obter_dados_evolucao_estoque(conn):
    """
    Busca o saldo líquido mensal (ENTRADA - SAÍDA) de todas as movimentações.
    Assume 'data_movimentacao' existe na tabela 'movimentacoes'.
    """
    cursor = conn.cursor()
    try:
        query = """
        SELECT 
            DATE_FORMAT(data_movimentacao, '%Y-%m') AS mes_ano,
            SUM(CASE 
                WHEN tipo = 'ENTRADA' THEN quantidade 
                ELSE -quantidade 
            END) AS saldo_net
        FROM movimentacoes
        GROUP BY mes_ano
        ORDER BY mes_ano;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f" Erro ao obter dados de evolução de estoque: {e}")
        return []
    finally:
        cursor.close()

# =====================================================================
# FUNÇÃO AUXILIAR: BUSCA DE DADOS POR CATEGORIA (NOVA)
# =====================================================================

def obter_dados_categorias(conn):
    """ 
    Soma a quantidade total de estoque agrupada por categoria.
    Assume a tabela 'categorias' e 'id_categoria' em 'produtos'.
    """
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

# =====================================================================
# FUNÇÃO 7: GERAÇÃO DE RELATÓRIOS E GRÁFICOS (DASHBOARD)
# =====================================================================

def gerar_relatorios_graficos(conn):
    """
    Gera um dashboard com três gráficos de acompanhamento de estoque:
    1. Curva ABC (custos)
    2. Comparação de Categorias
    3. Evolução do Estoque (saldo líquido mensal)
    """
    print("\n" + "="*80)
    print("                      GERAÇÃO DO DASHBOARD DE ESTOQUE")
    print("="*80)
    
    dados_abc = obter_dados_abc(conn)
    dados_categorias = obter_dados_categorias(conn)
    dados_evolucao = obter_dados_evolucao_estoque(conn)
    
    if not dados_abc and not dados_categorias and not dados_evolucao:
        print(" Sem dados suficientes para gerar qualquer relatório.")
        return

    # 1. Configura a figura principal do Dashboard (3 subplots em 1 linha)
    fig = plt.figure(figsize=(18, 6))
    plt.suptitle('Dashboard de Acompanhamento de Estoque', fontsize=16, y=1.02)

    
    # ------------------------------------------------------------------
    # GRÁFICO 1: CURVA ABC (CUSTOS)
    # ------------------------------------------------------------------
    
    ax1 = fig.add_subplot(1, 3, 1) # Primeiro subplot (1 linha, 3 colunas, posição 1)
    ax1.set_title('Curva ABC de Custos')
    
    if dados_abc:
        nomes = [item[0] for item in dados_abc]
        custos = np.array([item[1] for item in dados_abc])
        custos_ordenados = np.sort(custos)[::-1]
        total_geral = custos_ordenados.sum()
        
        if total_geral > 0:
            custo_acumulado = np.cumsum(custos_ordenados)
            percentual_acumulado = (custo_acumulado / total_geral) * 100
            
            # Eixo Esquerdo (Barras)
            ax1.bar(nomes, custos_ordenados, color='blue', alpha=0.6)
            ax1.set_ylabel('Custo Total (R$)', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.tick_params(axis='x', rotation=45) 

            # Eixo Direito (Linha de Pareto)
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
    # GRÁFICO 2: COMPARAÇÃO DE CATEGORIAS
    # ------------------------------------------------------------------
    
    ax3 = fig.add_subplot(1, 3, 2) # Segundo subplot
    ax3.set_title('Estoque por Categoria')
    
    if dados_categorias:
        categorias = [item[0] for item in dados_categorias]
        quantidades = [item[1] for item in dados_categorias]
        
        # Gráfico de barras simples para categorias
        ax3.bar(categorias, quantidades, color='green', alpha=0.7)
        ax3.set_ylabel('Quantidade Total (Unidades)')
        ax3.tick_params(axis='x', rotation=45)
    else:
        ax3.text(0.5, 0.5, 'Sem dados de categorias para agrupar.', ha='center', va='center', transform=ax3.transAxes)


    # ------------------------------------------------------------------
    # GRÁFICO 3: EVOLUÇÃO DO ESTOQUE (SALDO LÍQUIDO MENSAL)
    # ------------------------------------------------------------------

    ax4 = fig.add_subplot(1, 3, 3) # Terceiro subplot
    ax4.set_title('Evolução do Saldo Líquido Mensal')
    
    if dados_evolucao:
        meses = [item[0] for item in dados_evolucao]
        saldo_net = np.array([item[1] for item in dados_evolucao])
        
        # Gráfico de linha mostrando o saldo líquido
        ax4.plot(meses, saldo_net, marker='o', linestyle='-', color='purple')
        ax4.axhline(0, color='black', linestyle='--', linewidth=0.8)
        ax4.set_xlabel('Mês/Ano')
        ax4.set_ylabel('Saldo Líquido (Entrada - Saída)')
        ax4.tick_params(axis='x', rotation=45)
    else:
        ax4.text(0.5, 0.5, 'Sem dados de movimentação histórica.', ha='center', va='center', transform=ax4.transAxes)

    # Ajusta o layout para evitar sobreposição
    plt.tight_layout() 
    plt.show()
# =====================================================================
# FUNÇÃO 6: MENU PRINCIPAL
# =====================================================================

def menu_principal():
    """
    Menu interativo com as opções:
    1. Cadastrar produto
    2. Listar produtos
    3. Registrar movimentação
    4. Gerar relatórios e gráficos
    5. Sair
    """
    conexao = criar_conexao()
    if not conexao:
        print(" Não foi possível conectar ao banco de dados.")
        return

    try:
        # Inicializa o banco
        inicializar_banco(conexao)
        
        while True:
            print("\n" + "="*50)
            print("        SISTEMA ERP - MENU PRINCIPAL")
            print("="*50)
            print("1️  Cadastrar Novo Produto")
            print("2️  Listar Produtos e Estoque")
            print("3️  Registrar Movimentação (Entrada/Saída)")
            print("4️  Gerar Relatórios e Gráficos")
            print("5  Sair")
            print("="*50)
            
            escolha = input("Escolha uma opção (1-5): ").strip()
            
            if escolha == '1':
                inserir_produto_por_input(conexao)
            elif escolha == '2':
                listar_produtos_com_estoque(conexao)
            elif escolha == '3':
                registrar_movimentacao(conexao)
            elif escolha == '4':
                gerar_relatorios_graficos(conexao)
            elif escolha == '5':
                print("\n Saindo do sistema. Até logo!\n")
                break
            else:
                print(" Opção inválida. Tente novamente (1-4).")

    except KeyboardInterrupt:
        print("\n\n Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"\n Erro inesperado: {e}")
    finally:
        if conexao and conexao.is_connected():
            conexao.close()
            print(" Conexão com o banco de dados encerrada.\n")


# =====================================================================
# PONTO DE ENTRADA DO PROGRAMA
# =====================================================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("    BEM-VINDO AO SISTEMA ERP DE ESTOQUE")
    print("="*50)
    menu_principal()