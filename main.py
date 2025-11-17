from conexao import criar_conexao
from criar_bd import inicializar_banco 

from cadastrar import adicionar_categoria
from cadastrar import cadastrar_produto
from listar import listar_produtos_com_estoque
from excluir import excluir_produto_por_id


from movimentacoes import registrar_movimentacao


from definir_verificar_estoque import definir_e_verificar_estoque_seguranca
from giro_estoque import analisar_giro_estoque
from tempo_medio_reposicao import analisar_tempo_medio_reposicao

from graficos import gerar_relatorios_graficos


def menu_principal():

    conexao = criar_conexao()
    if not conexao:
        print(" Não foi possível conectar ao banco de dados.")
        return

    try:
        inicializar_banco(conexao)
        
        while True:
            print("\n" + "="*50)
            print(" SISTEMA ERP - MENU PRINCIPAL")
            print("="*50)
            print ("1- Adicionar nova categoria")
            print("2- Cadastrar Novo Produto")
            print("3- Listar Produtos e Estoque ") 
            print("4- Registrar Movimentação (Entrada/Saída)")
            print("5- Gerar Relatórios e Gráficos")
            print("6- Analisar Giro de Estoque") 
            print("7- Tempo Médio de Reposição") 
            print("8- Definir/Verificar Estoque de Segurança") 
            print("9- Excluir Produto") 
            print("10- Sair") 
            print("="*50)
            
            escolha = input("Escolha uma opção (1-10): ").strip()
            
            if escolha == '1':
                adicionar_categoria(conexao)

            elif escolha == '2':
                cadastrar_produto(conexao)    
                
            elif escolha == '3':
                listar_produtos_com_estoque(conexao) 
                
            elif escolha == '4':
                registrar_movimentacao(conexao)
                
            elif escolha == '5':
                gerar_relatorios_graficos(conexao)
            
            elif escolha == '6':
                analisar_giro_estoque(conexao)

            elif escolha == '7':
                analisar_tempo_medio_reposicao(conexao)

            elif escolha == '8':
                definir_e_verificar_estoque_seguranca(conexao)
                
            elif escolha == '9':
                excluir_produto_por_id(conexao) 
                
            elif escolha == '10':
                print("\n Saindo do sistema. Até logo!\n")
                break
                
            else:
                print(" Opção inválida. Tente novamente (1-10).") 

    except KeyboardInterrupt:
        print("\n\n Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"\n Erro inesperado: {e}")
    finally:
        if conexao and conexao.is_connected():
            conexao.close()
            print(" Conexão com o banco de dados encerrada.\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("    BEM-VINDO AO SISTEMA ERP DE ESTOQUE")
    print("="*50)
    menu_principal()