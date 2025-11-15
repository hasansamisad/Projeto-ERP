from conection_bd import criar_conexao, fechar_conexao
from datetime import datetime
from mysql.connector import Error

# --- FUNÇÃO DE CONEXÃO ---
def conectar_bd():
    """Alias para criar_conexao() por compatibilidade."""
    return criar_conexao()

# --- FUNÇÃO PRINCIPAL DE CADASTRO ---
def cadastrar_produto_sql(conexao):
    if conexao is None or not conexao.is_connected():
        print("Erro: Conexão com o banco de dados não está ativa.")
        return

    cursor = conexao.cursor()
    
    while True:
        deseja_cadastrar = input("Deseja cadastrar um novo produto? (s/n): ").strip().lower()
        if deseja_cadastrar == 'n':
            print("Cadastro de produtos encerrado.")
            break
        elif deseja_cadastrar != 's':
            print("Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")
            continue

        try:
            # 1. COLETANDO CÓDIGO E VERIFICANDO DUPLICIDADE (No BD)
            while True:
                try:
                    codigo = int(input("Digite o código do produto: "))
                    # Verifica se o código já existe no BD
                    cursor.execute("SELECT codigo FROM produtos WHERE codigo = %s", (codigo,))
                    if cursor.fetchone():
                        print("Código já cadastrado. Tente novamente com um código diferente.")
                        continue
                    break
                except ValueError:
                    print("Código inválido. Digite um número inteiro.")

            # 2. COLETANDO DESCRIÇÃO
            while True:
                descricao = input("Digite a descrição do produto: ").strip()
                if not descricao:
                    print("Descrição não pode ser vazia. Tente novamente.")
                    continue
                break

            # 3. COLETANDO CATEGORIA
            categoria_map = {'1': 'Matéria-Prima', '2': 'Produto Acabado'}
            while True:
                escolha = input("Digite a categoria (1-Matéria-Prima ou 2-Produto Acabado): ").strip()
                if escolha in categoria_map:
                    categoria = categoria_map[escolha]
                    break
                print("Categoria inválida. Digite 1 ou 2.")

            # 4. COLETANDO UNIDADE
            while True:
                unidade = input("Digite a unidade do produto (kg, L, un, etc.): ").strip()
                if not unidade:
                    print("Unidade não pode ser vazia. Tente novamente.")
                    continue
                break

            # 5. COLETANDO QUANTIDADE
            while True:
                try:
                    quantidade = float(input("Digite a quantidade do produto: ").replace(',', '.'))
                    break
                except ValueError:
                    print("Quantidade inválida. Digite um número válido.")

            # --- EXECUÇÃO DO INSERT NO BANCO DE DADOS ---
            sql_insert = """
            INSERT INTO produtos (codigo, descricao, categoria, unidade, quantidade)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            valores = (codigo, descricao, categoria, unidade, quantidade)

            cursor.execute(sql_insert, valores)
            conexao.commit()
            
            print("Produto cadastrado com sucesso no Banco de Dados!!!\n")

        except Error as e:
            conexao.rollback() # Desfaz a operação em caso de erro no BD
            print(f"Erro ao inserir registro no MySQL: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            continue

# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    # 1. Conecta ao BD
    minha_conexao = conectar_bd()

    # 2. Executa a função de cadastro
    if minha_conexao:
        cadastrar_produto_sql(minha_conexao)
        minha_conexao.close()

def listar_produtos():
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, preco, estoque FROM produtos")
        produtos = cursor.fetchall()

        print("📦 Lista de produtos:")
        for p in produtos:
            print(p)

        fechar_conexao(conexao)

def registrar_movimentacao(produto_id, quantidade, tipo):
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        data_atual = datetime.now()

        comando = """
        INSERT INTO movimentacoes (produto_id, quantidade, tipo, data)
        VALUES (%s, %s, %s, %s)
        """
        valores = (produto_id, quantidade, tipo, data_atual)

        cursor.execute(comando, valores)
        conexao.commit()
        print("✅ Movimentação registrada com sucesso!")

        fechar_conexao(conexao)

