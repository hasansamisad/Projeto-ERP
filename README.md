# 🏪 Sistema ERP de Estoque

Sistema completo de gerenciamento de estoque desenvolvido em Python com MySQL, incluindo cadastro de produtos, listagem com valor total e movimentações de entrada/saída.

## ✨ Funcionalidades

- ✅ **Cadastro de Produtos**: Nome, preço, unidade e estoque inicial
- ✅ **Listagem**: Tabela com todos os produtos e valor total em estoque
- ✅ **Movimentações**: Entrada e saída com histórico
- ✅ **Validações**: Previne erros como saída sem estoque
- ✅ **Transações ACID**: Garante integridade dos dados
- ✅ **Interface Amigável**: Menu interativo com emojis

## 🔧 Instalação

### 1. Pré-requisitos

```bash
# Python 3.7+
python --version

# MySQL 5.7+ ou MariaDB
mysql --version

# Pip (gerenciador de pacotes Python)
pip --version
```

### 2. Instalar MySQL Connector

```bash
pip install mysql-connector-python
```

### 3. Preparar Banco de Dados

**Opção A: Automático (recomendado)**
O script `completo.py` cria automaticamente:
- Database `mercado`
- User `erp_user` com senha `senha123`
- Todas as tabelas necessárias

**Opção B: Manual**
Execute no MySQL:
```sql
-- No MySQL CLI
mysql -u root -p < setup_database.sql
```

Ou copie o conteúdo de `setup_database.sql` e execute no MySQL Workbench.

### 4. Configurar Credenciais (opcional)

Se seu MySQL está em outra máquina ou com credenciais diferentes, edite em `completo.py`:

```python
DB_CONFIG = {
    "host": "localhost",      # IP ou hostname do MySQL
    "user": "erp_user",       # Seu usuário
    "password": "senha123",   # Sua senha
    "database": "mercado"     # Seu banco
}
```

## 🚀 Como Usar

### Iniciar o Programa

```bash
python completo.py
```

### Menu Principal

```
==================================================
       BEM-VINDO AO SISTEMA ERP DE ESTOQUE
==================================================

==================================================
         🏪 SISTEMA ERP - MENU PRINCIPAL
==================================================
1️⃣  Cadastrar Novo Produto
2️⃣  Listar Produtos e Estoque
3️⃣  Registrar Movimentação (Entrada/Saída)
4️⃣  Sair
==================================================

Escolha uma opção (1-4):
```

### Opção 1: Cadastrar Novo Produto

```
==================================================
       CADASTRO DE NOVO PRODUTO
==================================================

📦 Nome do produto: Arroz 5kg
💰 Preço unitário (R$): 18.90
📊 Quantidade inicial em estoque: 100
📏 Unidade (kg, L, un, caixa, etc.): kg

✅ Produto cadastrado com sucesso!
   ID: 1
   Nome: Arroz 5kg
   Preço: R$ 18.90
   Estoque Inicial: 100 kg
```

**Validações**:
- Nome: mínimo 3 caracteres, único
- Preço: deve ser > 0
- Quantidade: não pode ser negativa
- Unidade: obrigatória

### Opção 2: Listar Produtos e Estoque

```
================================================================================
                    CATÁLOGO DE PRODUTOS E ESTOQUE
================================================================================

ID    | PRODUTO                         | PREÇO      | ESTOQUE    | UNIDADE
-----+--------------------------------+----------+----------+---------
1     | Arroz 5kg                      | R$  18.90 |       100 | kg
2     | Feijão Carioca                 | R$  15.50 |        50 | kg
3     | Óleo de Soja                   | R$  12.00 |       200 | L
-----+--------------------------------+----------+----------+---------
VALOR TOTAL EM ESTOQUE:                              R$ 5234.50
```

### Opção 3: Registrar Movimentação

#### Entrada de Estoque
```
==================================================
      REGISTRO DE MOVIMENTAÇÃO DE ESTOQUE
==================================================

🔍 Digite o ID do produto: 1
📤 Tipo de movimento (E=ENTRADA / S=SAÍDA): E
📊 Quantidade: 50

✅ MOVIMENTAÇÃO REGISTRADA COM SUCESSO!
   Tipo: ENTRADA
   Quantidade movimentada: 50
   Saldo anterior: 100
   Saldo atual: 150
   Data/Hora: 15/11/2025 14:35:20
```

#### Saída de Estoque
```
🔍 Digite o ID do produto: 2
📤 Tipo de movimento (E=ENTRADA / S=SAÍDA): S
📊 Quantidade: 20

✅ MOVIMENTAÇÃO REGISTRADA COM SUCESSO!
   Tipo: SAÍDA
   Quantidade movimentada: 20
   Saldo anterior: 50
   Saldo atual: 30
   Data/Hora: 15/11/2025 14:36:10
```

#### Erro: Estoque Insuficiente
```
🔍 Digite o ID do produto: 2
📤 Tipo de movimento (E=ENTRADA / S=SAÍDA): S
📊 Quantidade: 100

❌ ESTOQUE INSUFICIENTE!
   Quantidade em estoque: 30
   Quantidade solicitada: 100
```

### Opção 4: Sair

```
👋 Saindo do sistema. Até logo!

✅ Conexão com o banco de dados encerrada.
```

## 📊 Estrutura do Banco de Dados

### Tabela: `produtos`
```
id_produto      → INT (chave primária, auto-incremento)
nome_produto    → VARCHAR(100) ÚNICA
preco           → DECIMAL(10,2) > 0
unidade         → VARCHAR(20) (padrão: 'unidade')
ativo           → TINYINT(1) (1=ativo, 0=inativo)
data_criacao    → TIMESTAMP (automático)
```

### Tabela: `estoque`
```
id_produto      → INT (chave primária + FK)
quantidade      → INT >= 0
```

### Tabela: `movimentacoes`
```
id_movimento    → INT (chave primária, auto-incremento)
id_produto      → INT (FK)
tipo            → ENUM('ENTRADA', 'SAIDA')
quantidade      → INT > 0
data_movimento  → TIMESTAMP (automático)
observacoes     → VARCHAR(255) (opcional)
```

## 🔒 Segurança

- **SQL Injection Prevention**: Uso de parâmetros no lugar de concatenação
- **Transações ACID**: Garante consistência dos dados
- **Validação de Entrada**: Loops até entrada válida
- **Constraints de BD**: CHECK, UNIQUE, FOREIGN KEY
- **Locks Transacionais**: SELECT FOR UPDATE evita race conditions

## 🐛 Resolução de Problemas

### "Conexão recusada"
```
✓ Verificar se MySQL está rodando
✓ Verificar host, user, password, database
✓ Verificar permissões do usuário
```

### "Base de dados não existe"
```
✓ O script cria automaticamente na primeira execução
✓ Ou execute setup_database.sql manualmente
```

### "Nome do produto duplicado"
```
✓ Cada produto deve ter nome único
✓ Use nomes diferentes
```

### "Estoque insuficiente"
```
✓ Não pode fazer saída maior que quantidade disponível
✓ Verifique o saldo antes
```

## 📁 Arquivos do Projeto

```
erp_python/
├── completo.py              # 🔧 Programa principal
├── setup_database.sql       # 📊 Script de configuração do BD
├── GUIA_COMPLETO.md         # 📖 Documentação detalhada
├── README.md                # 📄 Este arquivo
├── CORRECOES_REALIZADAS.md  # ✅ Histórico de correções
├── app.py                   # (legado)
├── conection_bd.py          # (legado)
├── conexao.py               # (legado)
└── reports/                 # Pasta para relatórios futuros
```

## 💾 Backup e Dados

### Exportar Dados
```bash
mysqldump -u erp_user -p mercado > backup.sql
```

### Importar Dados
```bash
mysql -u erp_user -p mercado < backup.sql
```

## 🚀 Próximas Melhorias

- [ ] Edição de produtos
- [ ] Deletar produtos (soft delete)
- [ ] Relatórios em PDF
- [ ] Exportar para Excel
- [ ] Interface gráfica (Tkinter/PyQt)
- [ ] API REST (Flask/FastAPI)
- [ ] Autenticação de usuários
- [ ] Log de operações

## 📝 Licença

Sistema desenvolvido para fins educacionais.

## 🤝 Suporte

Em caso de dúvidas, consulte:
1. `GUIA_COMPLETO.md` - Documentação detalhada
2. `setup_database.sql` - Queries SQL disponíveis
3. Comentários no código de `completo.py`

---

**Versão 1.0 - 15/11/2025** ✨
