import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from io import BytesIO

from PIL import Image, ImageTk

from midias5 import *

RESULTADOS = "Resultados da pesquisa"
BIBLIOTECA = "Minha biblioteca"

CAMPOS = {
    "Filme": ["Diretor", "Ator principal"],
    "Série": ["Número de temporadas"],
    "Livro": ["Autor"],
    "Jogo": ["Consoles (separe por vírgula)"],
}


class Aplicativo:
    def __init__(self):
        self.usuario = None
        self.visiveis = []
        self.capas = {}

        self.janela = tk.Tk()
        self.janela.title("Minhas Mídias")
        self.janela.geometry("1150x760")

        self.montar_login()
        self.janela.mainloop()

    def montar_login(self):
        self.tela_login = tk.Frame(self.janela)
        self.tela_login.pack(expand=True)

        tk.Label(self.tela_login, text="Minhas Mídias", font=("Arial", 24, "bold")).pack(pady=10)
        tk.Label(self.tela_login, text="Digite seu nome para entrar:").pack()

        self.entrada_nome = tk.Entry(self.tela_login, width=30, font=("Arial", 12))
        self.entrada_nome.pack(pady=10)
        self.entrada_nome.focus()
        self.entrada_nome.bind("<Return>", lambda evento: self.entrar())

        tk.Button(self.tela_login, text="Entrar", width=15, command=self.entrar).pack()

    def entrar(self):
        try:
            self.usuario = Usuario(self.entrada_nome.get())
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
            return

        self.tela_login.destroy()
        self.montar_principal()

    def montar_principal(self):
        tela = tk.Frame(self.janela)
        tela.pack(fill="both", expand=True, padx=10, pady=10)

        topo = tk.Frame(tela)
        topo.pack(fill="x")

        tk.Label(topo, text=f"Usuário: {self.usuario.nome}", font=("Arial", 11, "bold")).pack(side="left")
        tk.Button(topo, text="Pesquisar", command=self.pesquisar).pack(side="right")
        self.entrada_busca = tk.Entry(topo, width=40)
        self.entrada_busca.pack(side="right", padx=5)
        self.entrada_busca.bind("<Return>", lambda evento: self.pesquisar())
        tk.Label(topo, text="Pesquisar mídia:").pack(side="right")

        self.status = tk.Label(tela, text="Pesquise uma mídia para começar", anchor="w")
        self.status.pack(fill="x", pady=5)

        corpo = tk.Frame(tela)
        corpo.pack(fill="both", expand=True)

        esquerda = tk.Frame(corpo)
        esquerda.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(esquerda, text="Mostrar:").pack(anchor="w")
        self.combo = ttk.Combobox(esquerda, state="readonly", width=40)
        self.combo.pack(pady=(0, 5))
        self.combo.bind("<<ComboboxSelected>>", self.atualizar_lista)
        self.atualizar_opcoes(RESULTADOS)

        self.caixa = tk.Listbox(esquerda, width=46, exportselection=False)
        self.caixa.pack(fill="y", expand=True)
        self.caixa.bind("<<ListboxSelect>>", self.mostrar_midia)

        tk.Button(esquerda, text="Nova lista", command=self.nova_lista).pack(fill="x", pady=1)
        tk.Button(esquerda, text="Renomear lista", command=self.renomear_lista).pack(fill="x", pady=1)
        tk.Button(esquerda, text="Remover da lista", command=self.remover_da_lista).pack(fill="x", pady=1)
        tk.Button(esquerda, text="Criar mídia manualmente", command=self.criar_manual).pack(fill="x", pady=(8, 0))

        direita = tk.Frame(corpo)
        direita.pack(side="left", fill="both", expand=True)

        topo_direita = tk.Frame(direita)
        topo_direita.pack(fill="x")

        frame_capa = tk.Frame(topo_direita, width=260, height=380)
        frame_capa.pack(side="left", padx=(0, 10))
        frame_capa.pack_propagate(False)

        self.label_capa = tk.Label(frame_capa, text="Sem capa")
        self.label_capa.pack(expand=True)

        self.texto_info = tk.Text(topo_direita, width=60, height=22, wrap="word", state="disabled")
        self.texto_info.pack(side="left", fill="both", expand=True)

        botoes = tk.Frame(direita)
        botoes.pack(fill="x", pady=5)
        tk.Button(botoes, text="Cadastrar na biblioteca", command=self.cadastrar).pack(side="left", padx=(0, 5))
        tk.Button(botoes, text="Adicionar à lista", command=self.adicionar_a_lista).pack(side="left")

        frame_reviews = tk.LabelFrame(direita, text="Reviews")
        frame_reviews.pack(fill="x", pady=5)
        self.texto_reviews = tk.Text(frame_reviews, height=6, wrap="word", state="disabled")
        self.texto_reviews.pack(fill="x", padx=5, pady=5)

        frame_form = tk.LabelFrame(direita, text="Sua avaliação")
        frame_form.pack(fill="x")

        tk.Label(frame_form, text="Nota (0.5 a 5.0):").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entrada_nota = tk.Entry(frame_form, width=8)
        self.entrada_nota.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        tk.Label(frame_form, text="Comentário:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.entrada_comentario = tk.Entry(frame_form, width=70)
        self.entrada_comentario.grid(row=1, column=1, padx=5, pady=3, sticky="w")

        linha_botoes = tk.Frame(frame_form)
        linha_botoes.grid(row=2, column=1, sticky="w", pady=3)
        tk.Button(linha_botoes, text="Avaliar", command=self.avaliar).pack(side="left", padx=5)
        tk.Button(linha_botoes, text="Editar minha review", command=self.editar_review).pack(side="left", padx=5)
        tk.Button(linha_botoes, text="Remover minha review", command=self.remover_review).pack(side="left", padx=5)

        self.atualizar_lista()

    def escrever(self, caixa_texto, texto):
        caixa_texto.config(state="normal")
        caixa_texto.delete("1.0", tk.END)
        caixa_texto.insert(tk.END, texto)
        caixa_texto.config(state="disabled")

    def atualizar_opcoes(self, escolha):
        self.combo["values"] = [RESULTADOS, BIBLIOTECA] + [lista.nome for lista in self.usuario.listas]
        self.combo.set(escolha)

    def atualizar_lista(self, evento=None):
        escolha = self.combo.get()

        try:
            if escolha == RESULTADOS:
                self.visiveis = list(self.usuario.resultados)
            elif escolha == BIBLIOTECA:
                self.visiveis = list(self.usuario.midias)
            else:
                self.visiveis = list(self.usuario.lista_por_nome(escolha).midias)
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            self.visiveis = []

        self.caixa.delete(0, tk.END)
        for midia in self.visiveis:
            self.caixa.insert(tk.END, midia.resumo())

        if len(self.visiveis) == 0:
            self.label_capa.config(image="", text="Sem capa")
            self.escrever(self.texto_info, "Nenhuma mídia para mostrar")
            self.escrever(self.texto_reviews, "")
            return

        self.caixa.selection_set(0)
        self.mostrar_midia()

    def midia_selecionada(self):
        selecao = self.caixa.curselection()
        if not selecao:
            raise ValueError("Escolha uma mídia na lista")
        return self.visiveis[selecao[0]]

    def lista_atual(self):
        escolha = self.combo.get()
        if escolha == RESULTADOS or escolha == BIBLIOTECA:
            raise ValueError("Escolha uma lista na caixa Mostrar")
        return self.usuario.lista_por_nome(escolha)

    def mostrar_midia(self, evento=None):
        selecao = self.caixa.curselection()
        if not selecao:
            return

        midia = self.visiveis[selecao[0]]

        if not midia.detalhes_carregados:
            self.status.config(text="Carregando detalhes...")
            self.janela.update()
            try:
                midia.carregar_detalhes()
            except Exception:
                self.status.config(text="Não foi possível carregar todos os detalhes")
            else:
                self.status.config(text="")

        self.mostrar_capa(midia)
        self.escrever(self.texto_info, midia.detalhes())

        if len(midia.reviews) == 0:
            self.escrever(self.texto_reviews, "Nenhuma review ainda")
        else:
            self.escrever(self.texto_reviews, "\n\n".join(review.texto() for review in midia.reviews))

    def mostrar_capa(self, midia):
        chave = (midia.tipo, midia.titulo)

        if chave not in self.capas:
            try:
                imagem = Image.open(BytesIO(midia.baixar_capa()))
                imagem.thumbnail((250, 370))
                self.capas[chave] = ImageTk.PhotoImage(imagem)
            except Exception:
                self.capas[chave] = None

        foto = self.capas[chave]
        if foto is None:
            self.label_capa.config(image="", text="Sem capa")
        else:
            self.label_capa.config(image=foto, text="")
            self.label_capa.image = foto

    def pesquisar(self):
        self.status.config(text="Pesquisando nas APIs...")
        self.janela.update()

        try:
            falhas = self.usuario.pesquisar(self.entrada_busca.get())
        except ValueError as erro:
            self.status.config(text="")
            messagebox.showwarning("Atenção", str(erro))
            return

        self.atualizar_opcoes(RESULTADOS)
        self.atualizar_lista()

        if len(falhas) > 0:
            self.status.config(text="Sem resposta de: " + ", ".join(falhas))
        elif len(self.usuario.resultados) == 0:
            self.status.config(text="Nada encontrado. Use Criar mídia manualmente para cadastrar.")
        else:
            self.status.config(text="")

    def cadastrar(self):
        try:
            midia = self.midia_selecionada()
            self.usuario.cadastrar_midia(midia)
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        else:
            self.status.config(text=f"{midia.titulo} cadastrado(a) na sua biblioteca")
            self.mostrar_midia()

    def escolher_lista(self):
        janela = tk.Toplevel(self.janela)
        janela.title("Adicionar à lista")
        janela.transient(self.janela)
        janela.grab_set()

        tk.Label(janela, text="Escolha a lista:").pack(padx=10, pady=5)
        escolha = ttk.Combobox(janela, values=[lista.nome for lista in self.usuario.listas], state="readonly")
        escolha.current(0)
        escolha.pack(padx=10, pady=5)

        resultado = []

        def confirmar():
            resultado.append(escolha.get())
            janela.destroy()

        tk.Button(janela, text="OK", command=confirmar).pack(pady=10)
        self.janela.wait_window(janela)

        if len(resultado) == 0:
            return None
        return resultado[0]

    def adicionar_a_lista(self):
        try:
            midia = self.midia_selecionada()

            if len(self.usuario.listas) == 0:
                raise ValueError("Você ainda não tem listas. Clique em Nova lista")

            nome = self.escolher_lista()
            if nome is None:
                return

            self.usuario.lista_por_nome(nome).adicionar(midia)
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        else:
            self.status.config(text=f"{midia.titulo} adicionado(a) à lista {nome}")
            self.mostrar_midia()

    def nova_lista(self):
        nome = simpledialog.askstring("Nova lista", "Nome da lista:", parent=self.janela)
        if nome is None:
            return

        try:
            lista = self.usuario.criar_lista(nome)
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        else:
            self.atualizar_opcoes(lista.nome)
            self.atualizar_lista()

    def renomear_lista(self):
        try:
            lista = self.lista_atual()
            novo_nome = simpledialog.askstring(
                "Renomear lista", "Novo nome:", initialvalue=lista.nome, parent=self.janela
            )
            if novo_nome is None:
                return

            lista.renomear(novo_nome)
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        else:
            self.atualizar_opcoes(lista.nome)

    def remover_da_lista(self):
        try:
            lista = self.lista_atual()
            lista.remover(self.midia_selecionada())
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
        else:
            self.atualizar_lista()

    def limpar_formulario(self):
        self.entrada_nota.delete(0, tk.END)
        self.entrada_comentario.delete(0, tk.END)

    def nota_digitada(self):
        return self.entrada_nota.get().replace(",", ".")

    def avaliar(self):
        try:
            midia = self.midia_selecionada()
            self.usuario.avaliar(midia, self.nota_digitada(), self.entrada_comentario.get())
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        else:
            self.limpar_formulario()
            self.mostrar_midia()

    def editar_review(self):
        try:
            midia = self.midia_selecionada()
            review = self.usuario.review_de(midia)
            review.editar(self.nota_digitada(), self.entrada_comentario.get())
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        else:
            self.limpar_formulario()
            self.mostrar_midia()

    def remover_review(self):
        try:
            midia = self.midia_selecionada()
            self.usuario.review_de(midia).remover()
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        else:
            self.mostrar_midia()

    def campo(self, pai, texto, linha):
        rotulo = tk.Label(pai, text=texto)
        rotulo.grid(row=linha, column=0, sticky="w", padx=5, pady=3)
        entrada = tk.Entry(pai, width=45)
        entrada.grid(row=linha, column=1, padx=5, pady=3)
        return rotulo, entrada

    def criar_manual(self):
        janela = tk.Toplevel(self.janela)
        janela.title("Criar mídia manualmente")
        janela.transient(self.janela)
        janela.grab_set()

        tk.Label(janela, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        tipo = ttk.Combobox(janela, values=list(CAMPOS), state="readonly", width=42)
        tipo.current(0)
        tipo.grid(row=0, column=1, padx=5, pady=3)

        _, titulo = self.campo(janela, "Título:", 1)
        _, ano = self.campo(janela, "Ano:", 2)
        _, generos = self.campo(janela, "Gêneros (separe por vírgula):", 3)
        _, capa = self.campo(janela, "Link da capa (opcional):", 4)
        _, descricao = self.campo(janela, "Descrição:", 5)
        rotulo_a, campo_a = self.campo(janela, "", 6)
        rotulo_b, campo_b = self.campo(janela, "", 7)

        def atualizar_campos(evento=None):
            nomes = CAMPOS[tipo.get()]
            rotulo_a.config(text=nomes[0] + ":")

            if len(nomes) > 1:
                rotulo_b.config(text=nomes[1] + ":")
                rotulo_b.grid()
                campo_b.grid()
            else:
                rotulo_b.grid_remove()
                campo_b.grid_remove()

        def salvar():
            ano_texto = ano.get().strip()
            capa_texto = capa.get().strip()
            descricao_texto = descricao.get().strip()
            lista_generos = [g.strip() for g in generos.get().split(",") if g.strip()]
            escolhido = tipo.get()

            try:
                if escolhido == "Filme":
                    midia = self.usuario.criar_filme(titulo.get(), campo_a.get(), campo_b.get(),
                                                     ano_texto, capa_texto, descricao_texto, lista_generos)
                elif escolhido == "Série":
                    midia = self.usuario.criar_serie(titulo.get(), campo_a.get() or 0,
                                                     ano_texto, capa_texto, descricao_texto, lista_generos)
                elif escolhido == "Livro":
                    midia = self.usuario.criar_livro(titulo.get(), campo_a.get(),
                                                     ano_texto, capa_texto, descricao_texto, lista_generos)
                else:
                    consoles = [c.strip() for c in campo_a.get().split(",") if c.strip()]
                    midia = self.usuario.criar_jogo(titulo.get(), consoles,
                                                    ano_texto, capa_texto, descricao_texto, lista_generos)
            except ValueError as erro:
                messagebox.showwarning("Atenção", str(erro), parent=janela)
                return

            janela.destroy()
            self.atualizar_opcoes(BIBLIOTECA)
            self.atualizar_lista()

            ultimo = len(self.visiveis) - 1
            self.caixa.selection_clear(0, tk.END)
            self.caixa.selection_set(ultimo)
            self.caixa.see(ultimo)
            self.mostrar_midia()
            self.status.config(text=f"{midia.titulo} criado(a) e cadastrado(a)")

        tipo.bind("<<ComboboxSelected>>", atualizar_campos)
        atualizar_campos()

        tk.Button(janela, text="Salvar", command=salvar).grid(row=8, column=1, sticky="e", padx=5, pady=10)


if __name__ == "__main__":
    Aplicativo()