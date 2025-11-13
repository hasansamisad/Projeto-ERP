import mysql.connector
from mysql.connector import Error

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_CONFIG = {
    "host": "localhost",
    "user": "seu_usuario",
    "password": "sua_senha",
    "database": "mercado"
}

def criar_conexao():
    """Tenta estabelecer a conexão com o MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

def inicializar_banco(conn):
    """Cria todas as tabelas necessárias: produtos, estoque, e movimentacoes."""
    cursor = conn.cursor()
    
    # Tabela 1: Produtos (Já existe, mas incluímos a criação para segurança)
    tabela_produtos = """
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INT AUTO_INCREMENT PRIMARY KEY,
        nome_produto VARCHAR(100) NOT NULL,
        preco DECIMAL(10, 2) NOT NULL
    )
    """
    
    # Tabela 2: Estoque (Para armazenar o saldo atual de cada produto)
    tabela_estoque = """
    CREATE TABLE IF NOT EXISTS estoque (
        id_produto INT PRIMARY KEY,
        quantidade INT NOT NULL DEFAULT 0,
        FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    )
    """
    
    # Tabela 3: Movimentacoes (Para registrar o histórico de entradas e saídas)
    tabela_movimentacoes = """
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id_movimento INT AUTO_INCREMENT PRIMARY KEY,
        id_produto INT,
        tipo ENUM('ENTRADA', 'SAIDA') NOT NULL,
        quantidade INT NOT NULL,
        data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    )
    """
    
    try:
        cursor.execute(tabela_produtos)
        cursor.execute(tabela_estoque)
        cursor.execute(tabela_movimentacoes)
        conn.commit()
        print("Tabelas (produtos, estoque, movimentacoes) verificadas/criadas.")
    except Error as e:
        print(f"❌ Erro ao inicializar tabelas: {e}")
    finally:
        cursor.close()

# --- 1. FUNÇÃO DE INSERÇÃO DE PRODUTO (REAPROVEITADA E AJUSTADA) ---
def inserir_produto_por_input(conn):
    """Pede input ao usuário, insere o produto e inicializa seu estoque em 0."""
    print("\n--- Cadastro de Novo Produto ---")
    try:
        nome = input("Digite o NOME do produto: ")
        preco_str = input("Digite o PREÇO (ex: 15.99): ")
        preco = float(preco_str.replace(',', '.'))
    except ValueError:
        print("❌ Preço inválido.")
        return

    sql_insert_produto = "INSERT INTO produtos (nome_produto, preco) VALUES (%s, %s)"
    
    cursor = conn.cursor()
    try:
        # Inserir na tabela produtos
        cursor.execute(sql_insert_produto, (nome, preco))
        id_produto = cursor.lastrowid # Pega o ID gerado para o produto
        
        # Inicializar o estoque com 0
        sql_insert_estoque = "INSERT INTO estoque (id_produto, quantidade) VALUES (%s, %s)"
        cursor.execute(sql_insert_estoque, (id_produto, 0))
        
        conn.commit()
        print(f"✅ Produto '{nome}' (ID: {id_produto}) inserido e estoque inicializado com 0.")
    except Error as e:
        print(f"❌ Erro ao inserir produto: {e}")
        conn.rollback()
    finally:
        cursor.close()

# --- 2. FUNÇÃO DE LISTAGEM ---
def listar_produtos_com_estoque(conn):
    """Lista todos os produtos com seu nome, preço e quantidade em estoque."""
    print("\n--- Catálogo de Produtos e Estoque ---")
    
    # Query que junta dados da tabela 'produtos' e 'estoque'
    query = """
    SELECT 
        p.id_produto,
        p.nome_produto,
        p.preco,
        e.quantidade
    FROM 
        produtos p
    JOIN 
        estoque e ON p.id_produto = e.id_produto
    ORDER BY 
        p.nome_produto
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        resultados = cursor.fetchall() # Obtém todos os registros

        if not resultados:
            print("Nenhum produto cadastrado.")
            return

        # Imprime o cabeçalho
        print(f"{'ID':<4} | {'PRODUTO':<30} | {'PREÇO':>10} | {'ESTOQUE':>8}")
        print("-" * 58)
        
        # Imprime os resultados
        for (id_prod, nome, preco, qtd) in resultados:
            preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
            print(f"{id_prod:<4} | {nome:<30} | {preco_formatado:>10} | {qtd:>8}")
            
    except Error as e:
        print(f"❌ Erro ao listar produtos: {e}")
    finally:
        cursor.close()

# --- 3. FUNÇÃO DE MOVIMENTAÇÃO DE ESTOQUE ---
def registrar_movimentacao(conn):
    """Registra entrada ou saída de estoque, atualizando o saldo e o histórico."""
    print("\n--- Registro de Movimentação de Estoque ---")
    
    # Pede os inputs
    try:
        id_prod = int(input("Digite o ID do produto a movimentar: "))
        tipo = input("Tipo (E=ENTRADA / S=SAIDA): ").upper()
        if tipo not in ('E', 'S'):
            print("❌ Tipo de movimentação inválido. Use 'E' ou 'S'.")
            return
        
        quantidade = int(input("Quantidade: "))
        if quantidade <= 0:
            print("❌ A quantidade deve ser maior que zero.")
            return

    except ValueError:
        print("❌ ID ou Quantidade inválida.")
        return

    tipo_completo = "ENTRADA" if tipo == 'E' else "SAIDA"
    
    # 1. Atualizar o saldo na tabela 'estoque'
    if tipo == 'E':
        # Se for ENTRADA, somar ao estoque
        sql_update_estoque = "UPDATE estoque SET quantidade = quantidade + %s WHERE id_produto = %s"
    else: # SAIDA
        # Se for SAÍDA, subtrair do estoque
        sql_update_estoque = "UPDATE estoque SET quantidade = quantidade - %s WHERE id_produto = %s"

    # 2. Registrar o histórico na tabela 'movimentacoes'
    sql_insert_mov = """
    INSERT INTO movimentacoes (id_produto, tipo, quantidade) 
    VALUES (%s, %s, %s)
    """
    
    cursor = conn.cursor()
    try:
        # Inicia a transação
        conn.start_transaction()
        
        # Etapa A: Atualiza a tabela 'estoque'
        cursor.execute(sql_update_estoque, (quantidade, id_prod))
        
        if cursor.rowcount == 0:
            print(f"❌ Produto com ID {id_prod} não encontrado ou sem estoque inicializado.")
            conn.rollback()
            return
            
        # Etapa B: Insere o registro na tabela 'movimentacoes'
        cursor.execute(sql_insert_mov, (id_prod, tipo_completo, quantidade))
        
        # Confirma e persiste as duas operações
        conn.commit()
        print(f"✅ Movimentação de {tipo_completo} de {quantidade} unidade(s) para o produto ID {id_prod} registrada com sucesso.")
        
    except Error as e:
        print(f"❌ Erro na transação de movimentação: {e}")
        conn.rollback() # Desfaz as operações se algo falhar
    finally:
        cursor.close()

# --- EXECUÇÃO PRINCIPAL E MENU ---
def menu_principal():
    """Exibe um menu de opções para o usuário."""
    conexao = criar_conexao()
    if not conexao:
        return

    try:
        inicializar_banco(conexao) # Garante que as tabelas existam
        
        while True:
            print("\n==================================")
            print("        MENU ERP BÁSICO")
            print("==================================")
            print("1. Cadastrar Novo Produto")
            print("2. Listar Produtos e Estoque")
            print("3. Registrar Movimentação (Entrada/Saída)")
            print("4. Sair")
            
            escolha = input("Escolha uma opção: ")
            
            if escolha == '1':
                inserir_produto_por_input(conexao)
            elif escolha == '2':
                listar_produtos_com_estoque(conexao)
            elif escolha == '3':
                registrar_movimentacao(conexao)
            elif escolha == '4':
                print("Saindo do sistema. Até logo!")
                break
            else:
                print("Opção inválida. Tente novamente.")

    finally:
        if conexao and conexao.is_connected():
            conexao.close()
            print("\nConexão MySQL encerrada.")

if __name__ == "__main__":
    menu_principal()
