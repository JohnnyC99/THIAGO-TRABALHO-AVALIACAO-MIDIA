
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests

OMDB_KEY = "c5b6e934"
TWITCH_CLIENT_ID = "k96b9lflblbx10bejfh8vsyvcxfnk3"
TWITCH_CLIENT_SECRET = "10mzpqce3gfvco8999146099f00xg7"

TIMEOUT = 10
LIMITE = 6


class Midia(ABC):
    tipo = "Mídia"

    def __init__(self, titulo, ano="", capa="", descricao="", generos=None, id_api=None):
        if titulo == "":
            raise ValueError("O título não pode ficar vazio")

        if generos is None:
            generos = []

        self.titulo = titulo
        self.ano = ano
        self.capa = capa
        self.descricao = descricao
        self.generos = generos
        self.id_api = id_api
        self.detalhes_carregados = id_api is None
       
        self.reviews: List['Review'] = []
        self.usuarios: List['Usuario'] = []

    @abstractmethod
    def dados_especificos(self):
        pass

    def resumo(self):
        if self.ano:
            return f"[{self.tipo}] {self.titulo} ({self.ano})"
        return f"[{self.tipo}] {self.titulo}"

    def igual_a(self, outra):
        return self.tipo == outra.tipo and self.titulo.lower() == outra.titulo.lower()

    def adicionar_review(self, review):
        self.reviews.append(review)

    def nota_media(self):
        if len(self.reviews) == 0:
            return None

        total = 0
        for review in self.reviews:
            total = total + review.nota
        return total / len(self.reviews)

    def baixar_capa(self):
        if not self.capa.startswith("http"):
            raise ValueError("Essa mídia não tem capa")
        return requests.get(self.capa, timeout=TIMEOUT).content

    def detalhes(self):
        media = self.nota_media()
        if media is None:
            texto_media = "Sem avaliações"
        else:
            texto_media = f"{media:.1f} estrelas ({len(self.reviews)} review(s))"

        nomes = ""
        for usuario in self.usuarios:
            nomes = nomes + usuario.nome + " "

        linhas = [
            self.titulo,
            "",
            f"Tipo: {self.tipo}",
            f"Ano: {self.ano or 'Desconhecido'}",
            f"Gêneros: {', '.join(self.generos) or 'Desconhecido'}",
        ]
        linhas.extend(self.dados_especificos())
        linhas.append(f"Nota média: {texto_media}")
        linhas.append(f"Cadastrada por: {nomes or 'ninguém ainda'}")
        linhas.append("")
        linhas.append(f"Descrição: {self.descricao or 'Sem descrição'}")
        return "\n".join(linhas)

class Filme(Midia):
    tipo = "Filme"

    def __init__(self, titulo, diretor="", ator_principal="", ano="", capa="", descricao="", generos=None, id_api=None):
        super().__init__(titulo, ano, capa, descricao, generos, id_api)
        self.diretor = diretor
        self.ator_principal = ator_principal

    @classmethod
    def buscar(cls, termo):
        dados = requests.get(
            "https://www.omdbapi.com/",
            params={"s": termo, "type": "movie", "apikey": OMDB_KEY},
            timeout=TIMEOUT,
        ).json()

        if dados["Response"] == "False":
            if dados["Error"] in ("Movie not found!", "Too many results."):
                return []
            raise ValueError("OMDb: " + dados["Error"])

        filmes = []
        for item in dados["Search"][:LIMITE]:
            filmes.append(cls(item["Title"], ano=item["Year"], capa=item["Poster"], id_api=item["imdbID"]))
        return filmes

    def carregar_detalhes(self):
        dados = requests.get(
            "https://www.omdbapi.com/",
            params={"i": self.id_api, "plot": "full", "apikey": OMDB_KEY},
            timeout=TIMEOUT,
        ).json()

        self.diretor = dados["Director"]
        self.ator_principal = dados["Actors"].split(",")[0]
        self.descricao = dados["Plot"]
        self.generos = dados["Genre"].split(", ")
        self.detalhes_carregados = True

    def dados_especificos(self):
        return [
            f"Diretor: {self.diretor or 'Desconhecido'}",
            f"Ator principal: {self.ator_principal or 'Desconhecido'}",
        ]


class Serie(Midia):
    tipo = "Série"

    def __init__(self, titulo, qtd_temporadas=0, ano="", capa="", descricao="", generos=None, id_api=None):
        super().__init__(titulo, ano, capa, descricao, generos, id_api)

        try:
            self.qtd_temporadas = int(qtd_temporadas)
        except ValueError:
            raise ValueError("O número de temporadas precisa ser um número inteiro")

    @classmethod
    def buscar(cls, termo):
        lista = requests.get(
            "https://api.tvmaze.com/search/shows",
            params={"q": termo},
            timeout=TIMEOUT,
        ).json()

        series = []
        for item in lista[:LIMITE]:
            show = item["show"]

            capa = ""
            if show["image"]:
                capa = show["image"]["original"]

            ano = ""
            if show["premiered"]:
                ano = show["premiered"][:4]

            descricao = show["summary"] or ""
            for tag in ["<p>", "</p>", "<b>", "</b>", "<i>", "</i>", "<br>"]:
                descricao = descricao.replace(tag, "")

            series.append(cls(show["name"], ano=ano, capa=capa, descricao=descricao,
                              generos=show["genres"], id_api=show["id"]))
        return series

    def carregar_detalhes(self):
        temporadas = requests.get(
            f"https://api.tvmaze.com/shows/{self.id_api}/seasons",
            timeout=TIMEOUT,
        ).json()

        self.qtd_temporadas = len(temporadas)
        self.detalhes_carregados = True

    def dados_especificos(self):
        if self.qtd_temporadas == 0:
            return ["Temporadas: Desconhecido"]
        return [f"Temporadas: {self.qtd_temporadas}"]


class Livro(Midia):
    tipo = "Livro"

    def __init__(self, titulo, autor="", ano="", capa="", descricao="", generos=None, id_api=None):
        super().__init__(titulo, ano, capa, descricao, generos, id_api)
        self.autor = autor

    @classmethod
    def buscar(cls, termo):
        dados = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "q": termo,
                "limit": LIMITE,
                "fields": "key,title,author_name,first_publish_year,cover_i,subject",
            },
            timeout=TIMEOUT,
        ).json()

        livros = []
        for doc in dados["docs"]:
            capa = ""
            if "cover_i" in doc:
                capa = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"

            livros.append(cls(
                doc["title"],
                autor=", ".join(doc.get("author_name", [])),
                ano=str(doc.get("first_publish_year", "")),
                capa=capa,
                generos=doc.get("subject", [])[:5],
                id_api=doc["key"],
            ))
        return livros

    def carregar_detalhes(self):
        obra = requests.get(f"https://openlibrary.org{self.id_api}.json", timeout=TIMEOUT).json()

        descricao = obra.get("description", "")
        if type(descricao) == dict:
            descricao = descricao["value"]

        self.descricao = descricao
        self.detalhes_carregados = True

    def dados_especificos(self):
        return [f"Autor: {self.autor or 'Desconhecido'}"]


class Jogo(Midia):
    tipo = "Jogo"

    def __init__(self, titulo, consoles=None, ano="", capa="", descricao="", generos=None, id_api=None):
        super().__init__(titulo, ano, capa, descricao, generos, id_api)

        if consoles is None:
            consoles = []
        self.consoles = consoles

    @classmethod
    def buscar(cls, termo):
        token = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": TWITCH_CLIENT_ID,
                "client_secret": TWITCH_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
            timeout=TIMEOUT,
        ).json()["access_token"]

        termo = termo.replace('"', " ")
        cabecalho = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": "Bearer " + token}
        corpo = (
            f'search "{termo}"; '
            "fields name,first_release_date,cover.url,genres.name,platforms.name,summary; "
            f"limit {LIMITE};"
        )

        lista = requests.post(
            "https://api.igdb.com/v4/games",
            headers=cabecalho,
            data=corpo,
            timeout=TIMEOUT,
        ).json()

        jogos = []
        for item in lista:
            ano = ""
            if "first_release_date" in item:
                data = datetime(1970, 1, 1) + timedelta(seconds=item["first_release_date"])
                ano = str(data.year)

            capa = ""
            if "cover" in item:
                capa = "https:" + item["cover"]["url"].replace("t_thumb", "t_cover_big")

            jogos.append(cls(
                item["name"],
                consoles=[plataforma["name"] for plataforma in item.get("platforms", [])],
                ano=ano,
                capa=capa,
                descricao=item.get("summary", ""),
                generos=[genero["name"] for genero in item.get("genres", [])],
            ))
        return jogos

    def dados_especificos(self):
        return [f"Consoles: {', '.join(self.consoles) or 'Desconhecido'}"]
