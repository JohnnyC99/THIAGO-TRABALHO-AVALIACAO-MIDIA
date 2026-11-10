class Midia:
    def __init__(self, titulo):
            self.titulo = titulo
            self.reviews = []

    def adicionar_review(self, review):
        self.reviews.append(review)



class Filme(Midia):
    pass



class Livro(Midia):
    pass
    
class Jogo(Midia):
    pass
    
class Serie(Midia):
    pass

    
class Usuario:
    def __init__(self, nome):
        self.nome = nome
        self.reviews = []

    def criar_filme(self, titulo):
        filme = Filme(titulo)
        return filme

    def criar_jogo(self, titulo):
            jogo = Jogo(titulo)
            return jogo

    def criar_livro(self, titulo):
            livro = Livro(titulo)
            return livro

    def criar_serie(self, titulo):
            serie = Serie(titulo)
            return serie
    

    def avaliar_filme(self, filme, nota, comentario=""):
        if nota < 0.5 or nota > 5 or nota * 2 % 1 != 0:
            print("Nota invalida, use notas de 0.5 ate 5.0")
            return

        review = {
            "filme" : filme.titulo,
            "nota": nota,
            "comentario": comentario
        }

        self.reviews.append(review)
        filme.reviews.append(review)

    def mostrar_reviews(self):
        for review in self.reviews:
            print(
                f"{review['filme']} - "
                f"{review['nota']} estrelas"
            )

            print(f"Comentario : {review['comentario']}")
            print()

    def quantidade_reviews(self):
        return len(self.reviews)

filmes = []

usuario = Usuario("Joao")

while True:
    print("1 : Cadastrar filme")
    print("2 : Avaliar filme")
    print("3 : Ver filmes cadastrados")
    print("4 : Ver reviews")
    print("5 : Ver quantidade de reviews")
    print("0 : Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        titulo = input("Título do filme: ")

        titulo_novo = Filme(titulo)

        if titulo_novo.titulo in [filme.titulo for filme in filmes]:
            print("Esse filme já está cadastrado!")
        else:
            filmes.append(titulo_novo)
            print("Filme cadastrado!")

    elif opcao == "2":
        titulo = input("Qual filme você quer avaliar ")
        encontrado = False
    
        for filme in filmes:
            if filme.titulo == titulo:
                encontrado = True

                nota = float(input("Nota (0.5 a 5.0): "))
                comentario = input("Sua review: ")

                usuario.avaliar_filme(filme, nota, comentario)

        if encontrado == False:
            print("Filme não cadastrado!")

    elif opcao == "3":
        i = 0

        if len(filmes) == 0:
            print("Nenhum filme cadastrado")

        while i < len(filmes):
            print(filmes[i].titulo)
            i = i + 1

    elif opcao == "4":
        usuario.mostrar_reviews()

    elif opcao == "5":
        print("Total de reviews: ", usuario.quantidade_reviews())

    elif opcao == "0":
        print("Sessao finalizada")
        break

    else:
        print("Opcao invalida")





    
    
    
    


    
        
    




