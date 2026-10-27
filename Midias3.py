from abc import ABC, abstractmethod
import requests

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