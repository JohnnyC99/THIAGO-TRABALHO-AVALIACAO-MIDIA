from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List
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


class Review:
    def __init__(self, usuario: 'Usuario', midia: 'Midia', nota, comentario=""):
        self.usuario: 'Usuario' = usuario
        self.midia: 'Midia' = midia
        self.nota = 0
        self.comentario = comentario
        self.definir_nota(nota)

    def definir_nota(self, nota):
        try:
            nota = float(nota)
        except ValueError:
            raise ValueError("Digite uma nota válida (um número)")

        if nota < 0.5 or nota > 5 or nota * 2 % 1 != 0:
            raise ValueError("Use notas de 0.5 até 5.0, de meio em meio ponto")

        self.nota = nota

    def editar(self, nota, comentario):
        self.definir_nota(nota)
        self.comentario = comentario

    def remover(self):
        self.usuario.reviews.remove(self)
        self.midia.reviews.remove(self)

    def texto(self):
        return f"{self.usuario.nome} - {self.nota} estrelas\n{self.comentario or '(sem comentário)'}"


class Lista:
    def __init__(self, nome, usuario: 'Usuario'):
        self.nome = nome
        self.usuario: 'Usuario' = usuario
        self.midias: List['Midia'] = []

    def adicionar(self, midia):
        if midia in self.midias:
            raise ValueError(f"{midia.titulo} já está na lista {self.nome}")

        if midia not in self.usuario.midias:
            self.usuario.cadastrar_midia(midia)

        self.midias.append(midia)

    def remover(self, midia):
        if midia not in self.midias:
            raise ValueError(f"{midia.titulo} não está na lista {self.nome}")

        self.midias.remove(midia)

    def renomear(self, novo_nome):
        self.nome = self.usuario.validar_nome_lista(novo_nome)


class Usuario:
    def __init__(self, nome):
        if nome == "":
            raise ValueError("Digite um nome para entrar")

        self.nome = nome
        self.midias: List['Midia'] = []
        self.reviews: List['Review'] = []
        self.listas: List['Lista'] = []
        self.resultados: List['Midia'] = []

    def pesquisar(self, termo):
        if termo == "":
            raise ValueError("Digite algo para pesquisar")

        encontrados = []
        falhas = []

        for classe in (Filme, Serie, Livro, Jogo):
            try:
                encontrados = encontrados + classe.buscar(termo)
            except Exception:
                falhas.append(classe.tipo)

        self.resultados = []
        for midia in encontrados:
            self.resultados.append(self.versao_cadastrada(midia))

        return falhas

    def versao_cadastrada(self, midia):
        for cadastrada in self.midias:
            if cadastrada.igual_a(midia):
                return cadastrada
        return midia

    def cadastrar_midia(self, midia):
        for cadastrada in self.midias:
            if cadastrada.igual_a(midia):
                raise ValueError(f"{midia.titulo} já está na sua biblioteca")

        self.midias.append(midia)
        midia.usuarios.append(self)

    def criar_filme(self, titulo, diretor="", ator_principal="", ano="", capa="", descricao="", generos=None):
        filme = Filme(titulo, diretor, ator_principal, ano, capa, descricao, generos)
        self.cadastrar_midia(filme)
        return filme

    def criar_serie(self, titulo, qtd_temporadas=0, ano="", capa="", descricao="", generos=None):
        serie = Serie(titulo, qtd_temporadas, ano, capa, descricao, generos)
        self.cadastrar_midia(serie)
        return serie

    def criar_livro(self, titulo, autor="", ano="", capa="", descricao="", generos=None):
        livro = Livro(titulo, autor, ano, capa, descricao, generos)
        self.cadastrar_midia(livro)
        return livro

    def criar_jogo(self, titulo, consoles=None, ano="", capa="", descricao="", generos=None):
        jogo = Jogo(titulo, consoles, ano, capa, descricao, generos)
        self.cadastrar_midia(jogo)
        return jogo

    def review_de(self, midia):
        for review in self.reviews:
            if review.midia is midia:
                return review
        raise ValueError("Você ainda não avaliou essa mídia")

    def avaliar(self, midia, nota, comentario=""):
        for review in self.reviews:
            if review.midia is midia:
                raise ValueError("Você já avaliou essa mídia. Use Editar review")

        review = Review(self, midia, nota, comentario)

        if midia not in self.midias:
            self.cadastrar_midia(midia)

        self.reviews.append(review)
        midia.adicionar_review(review)
        return review

    def validar_nome_lista(self, nome):
        if nome == "":
            raise ValueError("O nome da lista não pode ficar vazio")

        for lista in self.listas:
            if lista.nome.lower() == nome.lower():
                raise ValueError(f"Já existe uma lista chamada {nome}")

        return nome

    def criar_lista(self, nome):
        lista = Lista(self.validar_nome_lista(nome), self)
        self.listas.append(lista)
        return lista

    def lista_por_nome(self, nome):
        for lista in self.listas:
            if lista.nome == nome:
                return lista
        raise ValueError(f"Lista {nome} não encontrada")
