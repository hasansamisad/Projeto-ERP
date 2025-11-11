-- DDL (Data Definition Language) Script para criar a tabela produtos

CREATE TABLE produtos (
    -- Código do produto. Usamos INT e definimos como CHAVE PRIMÁRIA 
    -- para garantir que cada produto tenha um código único e para otimizar buscas.
    codigo INT PRIMARY KEY,
    
    -- Descrição do produto. VARCHAR(255) é um tamanho comum para descrições.
    -- NOT NULL garante que este campo sempre seja preenchido.
    descricao VARCHAR(255) NOT NULL,
    
    -- Categoria: 'Matéria-Prima' ou 'Produto Acabado'.
    categoria VARCHAR(50) NOT NULL,
    
    -- Unidade de medida (ex: 'kg', 'L', 'un').
    unidade VARCHAR(10) NOT NULL,
    
    -- Quantidade: Usamos DECIMAL(10, 2) para armazenar números com até 10 dígitos 
    -- no total, sendo 2 após a vírgula/ponto, adequado para quantidades fracionadas.
    quantidade DECIMAL(10, 2) NOT NULL
);