from midias4 import *

usuario = Usuario("Joao")

midias = [
    usuario.criar_filme("Little Miss Sunshine"),
    usuario.criar_filme("Seven Samurai"),
    usuario.criar_filme("Blade Runner: 2049"),
    usuario.criar_livro("The Lord of the Rings"),
    usuario.criar_livro("Dune"),
    usuario.criar_livro("Crime and Punishment"),
    usuario.criar_serie("True Detective"),
    usuario.criar_serie("Better Call Saul"),
    usuario.criar_jogo("Disco Elysium"),
    usuario.criar_jogo("Red Dead Redemption 2"),
]

usuario.criar_lista("Complexo do humano", midias, "Disco Elysium", "Crime and Punishment", "Blade Runner: 2049", "True Detective")

print("Carregando mídias...")
for midia in midias:
    midia.buscar_dados()

while True:
    print("1 : Ver mídias cadastradas")
    print("2 : Ver detalhes de uma mídia")
    print("3 : Ver listas")
    print("4 : Ver mídias de uma lista")
    print("0 : Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        if len(midias) == 0:
            print("Nenhuma mídia cadastrada")

        for midia in midias:
            print(f"[{midia.__class__.__name__}] {midia.titulo}")

    elif opcao == "2":
        titulo = input("Qual mídia você quer ver ")
        encontrado = False

        for midia in midias:
            if midia.titulo.lower() == titulo.lower():
                encontrado = True
                midia.mostrar_detalhes()

        if encontrado == False:
            print("Mídia não cadastrada!")

    elif opcao == "3":
        if len(usuario.listas) == 0:
            print("Nenhuma lista criada")

        for lista in usuario.listas:
            print(f"{lista['nome']} ({len(lista['midias'])} mídias)")

    elif opcao == "4":
        usuario.mostrar_lista()

    elif opcao == "0":
        print("Sessao finalizada")
        break

    else:
        print("Opcao invalida")