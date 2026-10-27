from Midias3 import *

usuario = Usuario("Joao")

midias = [
    usuario.criar_filme("Little Miss Sunshine"),
    usuario.criar_filme("Seven Samurai"),
    usuario.criar_filme("Interstellar"),
    usuario.criar_livro("The Lord of the Rings"),
    usuario.criar_livro("Dune"),
    usuario.criar_serie("Game of Thrones"),
    usuario.criar_serie("Better Call Saul"),
    usuario.criar_jogo("Disco Elysium"),
    usuario.criar_jogo("Red Dead Redemption 2"),
]

print("Carregando mídias...")
for midia in midias:
    midia.buscar_dados()

while True:
    print("1 : Ver mídias cadastradas")
    print("2 : Ver detalhes de uma mídia")
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

    elif opcao == "0":
        print("Sessao finalizada")
        break

    else:
        print("Opcao invalida")