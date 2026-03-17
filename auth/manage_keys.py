import argparse
import sys
import os

# Add parent directory to path to allow importing from security module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.api_keys import create_api_key, list_api_keys, delete_api_key, delete_all_api_keys

def main():
    parser = argparse.ArgumentParser(description="Gerenciador de Chaves de API")
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')

    # Comando create
    create_parser = subparsers.add_parser('create', help='Criar nova chave')
    create_parser.add_argument('name', help='Nome do cliente/usuário')
    create_parser.add_argument('date', nargs='?', help='Data de validade (YYYY-MM-DD ou DD-MM-YYYY)')

    # Comando list
    subparsers.add_parser('list', help='Listar todas as chaves')

    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Deletar uma chave pelo ID')
    delete_parser.add_argument('id', type=int, help='ID da chave a ser deletada')

    # Comando delete-all
    subparsers.add_parser('delete-all', help='Deletar TODAS as chaves (com confirmação)')

    args = parser.parse_args()

    if args.command == 'create':
        try:
            key = create_api_key(args.name, args.date)
            print(f"\n✅ Chave criada com sucesso para '{args.name}'!")
            print(f"🔑 Chave: {key}")
            print("⚠️  ATENÇÃO: Copie esta chave agora. Ela não será mostrada novamente.\n")
            if args.date:
                print(f"📅 Validade até: {args.date}")
        except Exception as e:
            print(f"❌ Erro ao criar chave: {e}")
            sys.exit(1)

    elif args.command == 'list':
        keys = list_api_keys()
        if not keys:
            print("Nenhuma chave encontrada.")
        else:
            print(f"{'ID':<5} {'NOME':<20} {'PREFIXO':<10} {'CRIADA EM':<20} {'VALIDADE':<20}")
            print("-" * 80)
            for k in keys:
                valid = k['valid_until'] if k['valid_until'] else "Nunca"
                created = k['created_at'].split('.')[0] if k['created_at'] else "?"
                print(f"{k['id']:<5} {k['name']:<20} {k['prefix']:<10} {created:<20} {valid:<20}")

    elif args.command == 'delete':
        if delete_api_key(args.id):
            print(f"✅ Chave ID {args.id} deletada com sucesso.")
        else:
            print(f"❌ Chave ID {args.id} não encontrada.")
            sys.exit(1)

    elif args.command == 'delete-all':
        keys = list_api_keys()
        if not keys:
            print("Nenhuma chave encontrada para deletar.")
        else:
            print(f"⚠️  ATENÇÃO: Você está prestes a deletar {len(keys)} chave(s)!")
            print("Esta ação é IRREVERSÍVEL.")
            confirm = input("Digite 'DELETAR TUDO' para confirmar: ")
            if confirm == 'DELETAR TUDO':
                deleted_count = delete_all_api_keys()
                print(f"✅ {deleted_count} chave(s) deletada(s) com sucesso.")
            else:
                print("❌ Operação cancelada.")
                sys.exit(1)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
