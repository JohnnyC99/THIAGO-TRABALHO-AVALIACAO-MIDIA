from midiaDudinha import Midia
from midiaDudinha import Filme
from midiaDudinha import Serie
from midiaDudinha import Jogo
from midiaDudinha import Livro
from typing import List

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
