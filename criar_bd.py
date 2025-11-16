from mysql.connector import Error

def inicializar_banco(conn):

    cursor = conn.cursor()
    
    try:
        sql_categorias = """
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nome_categoria VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_categorias)

        sql_produtos = """
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INT AUTO_INCREMENT PRIMARY KEY,
            nome_produto VARCHAR(100) NOT NULL UNIQUE,
            preco DECIMAL(10, 2) NOT NULL CHECK (preco > 0),
            unidade VARCHAR(20) NOT NULL DEFAULT 'unidade',
            estoque_minimo INT NOT NULL DEFAULT 5 CHECK (estoque_minimo >= 0),
            estoque_maximo INT NOT NULL DEFAULT 100,
            id_categoria INT NULL, 
            ativo TINYINT(1) NOT NULL DEFAULT 1,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (estoque_minimo <= estoque_maximo),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_produtos)
        
       
        sql_estoque = """
        CREATE TABLE IF NOT EXISTS estoque (
            id_produto INT PRIMARY KEY,
            quantidade INT NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(sql_estoque)
        
        
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
        print(f" Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()
