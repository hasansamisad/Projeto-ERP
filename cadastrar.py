from mysql.connector import Error

def adicionar_categoria(conn):
    nome = input("Digite o nome da nova categoria: ").strip()
    if not nome:
        print("Nome da categoria não pode ser vazio.")
        return
        
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO categorias (nome_categoria) VALUES (%s)"
        cursor.execute(sql, (nome,))
        conn.commit()
        print(f"Categoria '{nome}' cadastrada com sucesso!")
    except Error as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
             print(f"Erro: Categoria '{nome}' já existe.")
        else:
             print(f"Erro ao cadastrar categoria: {e}")
    finally:
        cursor.close()


def cadastrar_produto(conn):

    print("\n" + "="*50)
    print("           CADASTRO DE NOVO PRODUTO")
    print("="*50)
    
    cursor = conn.cursor()
    
    try:
        while True:
            nome_produto = input(" Nome do produto: ").strip()
            if not nome_produto or len(nome_produto) < 3:
                print("Nome deve ter pelo menos 3 caracteres.")
                continue
            break

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
        
        while True:
            try:
                quantidade = int(input("Quantidade inicial em estoque: ").strip())
                if quantidade < 0:
                    print(" Quantidade não pode ser negativa.")
                    continue
                break
            except ValueError:
                print(" Quantidade inválida. Digite um número inteiro.")

        while True:
            unidade = input("Unidade (kg, L, un, caixa, etc.): ").strip().lower()
            if not unidade or len(unidade) < 1:
                print("Unidade não pode ser vazia.")
                continue
            break

        cursor.execute("SELECT id_categoria, nome_categoria FROM categorias ORDER BY nome_categoria")
        categorias = cursor.fetchall()
        id_categoria = None 
        nome_categoria_selecionada = "Sem Categoria"
        
        if categorias:
            print("\n -- Seleção de Categoria --")
            for id_c, nome_c in categorias:
                print(f"{id_c}: {nome_c}")
            print(" 0: Sem Categoria (Opcional)")
            
            while True:
                try:
                    escolha_cat = input("Escolha o ID da Categoria (0 para ignorar): ").strip()

                    if escolha_cat == '0' or escolha_cat == '':
                        break             

                    id_selecionado = int(escolha_cat)

                    categoria_encontrada = next((c for c in categorias if c[0] == id_selecionado), None)
                    
                    if categoria_encontrada:
                        id_categoria = id_selecionado
                        nome_categoria_selecionada = categoria_encontrada[1]
                        break
                    else:
                        print(f"ID de categoria {id_selecionado} inválido. Tente novamente.")
                except ValueError:
                    print("Entrada inválida. Digite um número.")
        else:
            print(" Nenhuma categoria cadastrada. O produto será adicionado sem categoria.")

        sql_produto = """
        INSERT INTO produtos (nome_produto, preco, unidade, id_categoria, ativo) 
        VALUES (%s, %s, %s, %s, 1)
        """
        cursor.execute(sql_produto, (nome_produto, preco, unidade, id_categoria))
        id_produto = cursor.lastrowid
        
        sql_estoque = """
        INSERT INTO estoque (id_produto, quantidade) 
        VALUES (%s, %s)
        """
        cursor.execute(sql_estoque, (id_produto, quantidade))
        conn.commit()

        print("\n  Produto cadastrado com sucesso!")
        print(f"   ID: {id_produto}")
        print(f"   Nome: {nome_produto}")
        print(f"   Preço: R$ {preco:.2f}")
        print(f"   Estoque Inicial: {quantidade} {unidade}")
        print(f"   Categoria: {nome_categoria_selecionada}\n")
        
    except Error as e:
        conn.rollback() 
        if "Duplicate entry" in str(e) and nome_produto:
            print(f"\n Erro: Já existe um produto com o nome '{nome_produto}'.\n")
        elif "Cannot add or update a child row" in str(e):
             print(f"\n Erro: O ID de Categoria selecionado ({id_categoria}) não existe.\n")
        else:
            print(f"\n Erro ao cadastrar produto: {e}\n")
    except Exception as e:
        conn.rollback()
        print(f"\n Erro inesperado: {e}\n")
    finally:
        cursor.close()