import sys
print(sys.executable)

from abc import ABC, abstractmethod
import requests, tkinter

OMDB_KEY = "c5b6e934"
RAWG_KEY = "5d4f3c0d35424cab88c3fe8202785c20"


class Midia(ABC):
    def __init__(self, titulo):
        self.titulo = titulo
        self.reviews = []
        self.ano = None
        self.capa = ""
        self.descricao = None
        self.generos = []

    def adicionar_review(self, review):
        self.reviews.append(review)

    @abstractmethod
    def buscar_dados(self):
        pass

    def mostrar_detalhes(self):
        print(f"Título: {self.titulo}")
        print(f"Ano: {self.ano}")
        print(f"Gêneros: {', '.join(self.generos)}")
        print(f"Capa: {self.capa}")
        print(f"Descrição: {self.descricao}")


class Filme(Midia):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.ator_principal = ""
        self.diretor = ""

    def buscar_dados(self):
        dados = requests.get(
            "http://www.omdbapi.com/",
            params={"t": self.titulo, "plot": "full", "apikey": OMDB_KEY},
        ).json()

        if dados["Response"] == "False":
            return False

        self.titulo = dados["Title"]
        self.ano = dados["Year"]
        self.diretor = dados["Director"]
        self.ator_principal = dados["Actors"].split(",")[0]
        self.descricao = dados["Plot"]
        self.generos = dados["Genre"].split(", ")
        self.capa = dados["Poster"]
        return True

    def mostrar_detalhes(self):
        super().mostrar_detalhes()
        print(f"Diretor: {self.diretor}")
        print(f"Ator principal: {self.ator_principal}")


class Livro(Midia):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.autor = ""

    def buscar_dados(self):
        dados = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": self.titulo,
                "limit": 1,
                "fields": "title,author_name,first_publish_year,cover_i,subject",
            },
        ).json()

        if len(dados["docs"]) == 0:
            return False

        livro = dados["docs"][0]
        self.titulo = livro["title"]
        self.autor = ", ".join(livro.get("author_name", []))
        self.ano = livro.get("first_publish_year")
        self.generos = livro.get("subject", [])[:5]
        if "cover_i" in livro:
            self.capa = f"https://covers.openlibrary.org/b/id/{livro['cover_i']}-L.jpg"
        return True

    def mostrar_detalhes(self):
        super().mostrar_detalhes()
        print(f"Autor: {self.autor}")


class Serie(Midia):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.qtd_temporadas = ""

    def buscar_dados(self):
        resposta = requests.get(
            "https://api.tvmaze.com/singlesearch/shows",
            params={"q": self.titulo, "embed": "seasons"},
        )

        if resposta.status_code != 200:
            return False

        dados = resposta.json()
        self.titulo = dados["name"]
        if dados["premiered"]:
            self.ano = dados["premiered"][:4]
        self.generos = dados["genres"]
        self.descricao = dados["summary"]
        if dados["image"]:
            self.capa = dados["image"]["original"]
        self.qtd_temporadas = len(dados["_embedded"]["seasons"])
        return True

    def mostrar_detalhes(self):
        super().mostrar_detalhes()
        print(f"Temporadas: {self.qtd_temporadas}")


class Jogo(Midia):
    def __init__(self, titulo):
        super().__init__(titulo)
        self.consoles = []

    def buscar_dados(self):
        dados = requests.get(
            "https://api.rawg.io/api/games",
            params={"key": RAWG_KEY, "search": self.titulo, "page_size": 1},
        ).json()

        if "results" not in dados or len(dados["results"]) == 0:
            return False

        jogo = dados["results"][0]
        self.titulo = jogo["name"]
        if jogo["released"]:
            self.ano = jogo["released"][:4]
        self.capa = jogo["background_image"]
        self.generos = [g["name"] for g in jogo["genres"]]
        self.consoles = [p["platform"]["name"] for p in jogo["platforms"]]
        return True

    def mostrar_detalhes(self):
        super().mostrar_detalhes()
        print(f"Consoles: {', '.join(self.consoles)}")



class Usuario:
    def __init__(self, nome):
        self.nome = nome
        self.reviews = []
        self.listas = []

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

    def avaliar_midia(self, midia, nota, comentario=""):
        if nota < 0.5 or nota > 5 or nota * 2 % 1 != 0:
            print("Nota invalida, use notas de 0.5 ate 5.0")
            return

        review = {
            "midia": midia.titulo,
            "nota": nota,
            "comentario": comentario
        }

        self.reviews.append(review)
        midia.reviews.append(review)

    def mostrar_reviews(self):
        for review in self.reviews:
            print(
                f"{review['midia']} - "
                f"{review['nota']} estrelas"
            )

            print(f"Comentario : {review['comentario']}")
            print()

    def quantidade_reviews(self):
        return len(self.reviews)

    def criar_lista(self, lista_nome=None, midias_lista=None, *titulos):
        if lista_nome is not None:
            lista = []

            for titulo in titulos:
                for midia in midias_lista:
                    if midia.titulo.lower() == titulo.lower():
                        lista.append(midia)
                        break

            self.listas.append({
                "nome": lista_nome,
                "midias": lista
            })
            return

        lista_nome = input("Qual o nome da lista: ")
        lista = []

        while True:
            titulo = input("Digite a midia que deseja adicionar ou digite 0 pra sair: ")

            if titulo == "0":
                break

            encontrado = False

            for midia in midias:
                if midia.titulo == titulo:
                    lista.append(midia)
                    encontrado = True
                    print("Midia adicionada")
                    break
        self.listas.append({
            "nome": lista_nome,
            "midias": lista
        })

    



    def editar_review(self):
        review_novo = input("Qual review você deseja editar? ")

        for review in self.reviews:
            if review["midia"] == review_novo:
                nova_review_nota = float(input("Diga a nota nova que você deseja dar, de 0 a 5: "))

                if 0.5 <= nova_review_nota <= 5 and nova_review_nota * 2 % 1 == 0:
                    review["nota"] = nova_review_nota
                    print("Review editada")
                else:
                    print("Nota invalida")
                return

            
            
            

    def remover_review(self):
        review_apagar = input("Qual review voce deseja apagar? ")

        for review in self.reviews:
            if review["midia"] == review_apagar:
                self.reviews.remove(review)

                for midia in midias:
                    if midia.titulo == review_apagar:
                        midia.reviews.remove(review)
                        break

                print("Review removida")
                break
    
    def mostrar_lista(self):
        nome = input("Qual lista voce deseja visualizar? ")

        for lista in self.listas:
            if lista["nome"] == nome:
                print(f"Lista: {lista['nome']}")

                for midia in lista["midias"]:
                    print(midia.titulo)

                return

        print("Lista nao encontrada")



        
    






midias = []

usuario = Usuario("Joao")

while True:
    print("1 : Cadastrar mídia")
    print("2 : Avaliar mídia")
    print("3 : Ver mídias cadastradas")
    print("4 : Ver detalhes de uma mídia")
    print("5 : Ver reviews")
    print("6 : Ver quantidade de reviews")
    print("7 : Criar lista")
    print("8 : Editar review")
    print("9 : Remover review")
    print("10 : Ver Lista")
    
    print("0 : Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        tipo = input("Tipo (1 Filme, 2 Livro, 3 Série, 4 Jogo): ")
        titulo = input("Título: ")

        if tipo == "1":
            nova = usuario.criar_filme(titulo)
        elif tipo == "2":
            nova = usuario.criar_livro(titulo)
        elif tipo == "3":
            nova = usuario.criar_serie(titulo)
        elif tipo == "4":
            nova = usuario.criar_jogo(titulo)
        else:
            print("Tipo invalido")
            continue

        if nova.buscar_dados() == False:
            print("Não encontrado na API, cadastrado só com o título")

        if nova.titulo in [midia.titulo for midia in midias]:
            print("Essa mídia já está cadastrada!")
        else:
            midias.append(nova)
            print("Mídia cadastrada!")

    elif opcao == "2":
        titulo = input("Qual mídia você quer avaliar ")
        encontrado = False

        for midia in midias:
            if midia.titulo == titulo:
                encontrado = True

                nota = float(input("Nota (0.5 a 5.0): "))
                comentario = input("Sua review: ")

                usuario.avaliar_midia(midia, nota, comentario)

        if encontrado == False:
            print("Mídia não cadastrada!")

    elif opcao == "3":
        if len(midias) == 0:
            print("Nenhuma mídia cadastrada")

        for midia in midias:
            print(midia.titulo)

    elif opcao == "4":
        titulo = input("Qual mídia você quer ver ")
        encontrado = False

        for midia in midias:
            if midia.titulo == titulo:
                encontrado = True
                midia.mostrar_detalhes()

        if encontrado == False:
            print("Mídia não cadastrada!")

    elif opcao == "5":
        usuario.mostrar_reviews()

    elif opcao == "6":
        print("Total de reviews: ", usuario.quantidade_reviews())

    elif opcao == "7":
        usuario.criar_lista()

    elif opcao == "8":
        usuario.editar_review()

    elif opcao == "9":
        usuario.remover_review()

    elif opcao == "10":
        usuario.mostrar_lista()

    elif opcao == "0":
        print("Sessao finalizada")
        break

    else:
        print("Opcao invalida")
