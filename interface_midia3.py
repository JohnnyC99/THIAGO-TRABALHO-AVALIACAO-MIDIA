import tkinter as tk
from tkinter import messagebox, ttk
from io import BytesIO

import requests
from PIL import Image, ImageTk

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

capas = {}
visiveis = list(midias)


def carregar_capa(midia):
    if midia.titulo in capas:
        return capas[midia.titulo]

    if not midia.capa or not midia.capa.startswith("http"):
        return None

    try:
        dados = requests.get(midia.capa).content
        imagem = Image.open(BytesIO(dados))
        imagem.thumbnail((250, 370))
        foto = ImageTk.PhotoImage(imagem)
    except Exception:
        return None

    capas[midia.titulo] = foto
    return foto


def montar_info(midia):
    texto = f"{midia.titulo}\n\n"
    texto += f"Ano: {midia.ano or 'Desconhecido'}\n"
    texto += f"Gêneros: {', '.join(midia.generos)}\n"

    if isinstance(midia, Filme):
        texto += f"Diretor: {midia.diretor}\n"
        texto += f"Ator principal: {midia.ator_principal}\n"
    elif isinstance(midia, Livro):
        texto += f"Autor: {midia.autor}\n"
    elif isinstance(midia, Serie):
        texto += f"Temporadas: {midia.qtd_temporadas}\n"
    elif isinstance(midia, Jogo):
        texto += f"Consoles: {', '.join(midia.consoles)}\n"

    texto += f"\nDescrição: {midia.descricao or 'Sem descrição'}"
    return texto


def mostrar_reviews(midia):
    if len(midia.reviews) == 0:
        texto = "Nenhuma review ainda"
    else:
        texto = ""
        for review in midia.reviews:
            texto += f"Nota: {review['nota']} estrelas\n"
            texto += f"Comentário: {review['comentario']}\n\n"

    label_reviews.config(text=texto)


def mostrar_midia(event=None):
    selecao = caixa.curselection()
    if not selecao:
        return

    midia = visiveis[selecao[0]]

    foto = carregar_capa(midia)
    if foto:
        label_capa.config(image=foto, text="")
        label_capa.image = foto
    else:
        label_capa.config(image="", text="Sem capa")

    label_info.config(text=montar_info(midia))
    mostrar_reviews(midia)


def trocar_lista(event=None):
    visiveis[:] = midias

    for lista in usuario.listas:
        if lista["nome"] == combo.get():
            visiveis[:] = lista["midias"]

    caixa.delete(0, tk.END)
    for midia in visiveis:
        caixa.insert(tk.END, f"[{midia.__class__.__name__}] {midia.titulo}")

    if len(visiveis) == 0:
        label_capa.config(image="", text="Sem capa")
        label_info.config(text="Nenhuma mídia nessa lista")
        label_reviews.config(text="")
        return

    caixa.selection_set(0)
    mostrar_midia()


def avaliar():
    selecao = caixa.curselection()
    if not selecao:
        messagebox.showinfo("Aviso", "Escolha uma mídia na lista")
        return

    midia = visiveis[selecao[0]]

    try:
        nota = float(entrada_nota.get().replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Digite uma nota válida")
        return

    antes = len(midia.reviews)
    usuario.avaliar_midia(midia, nota, entrada_comentario.get())

    if len(midia.reviews) == antes:
        messagebox.showerror("Nota inválida", "Use notas de 0.5 até 5.0")
        return

    entrada_nota.delete(0, tk.END)
    entrada_comentario.delete(0, tk.END)
    mostrar_reviews(midia)


janela = tk.Tk()
janela.title("Minhas Mídias")
janela.geometry("950x700")

frame_esquerda = tk.Frame(janela)
frame_esquerda.pack(side="left", fill="y", padx=10, pady=10)

tk.Label(frame_esquerda, text="Mostrar:").pack(anchor="w")

nomes = ["Todas as mídias"] + [lista["nome"] for lista in usuario.listas]
combo = ttk.Combobox(frame_esquerda, values=nomes, state="readonly", width=30)
combo.set(nomes[0])
combo.pack(pady=(0, 10))
combo.bind("<<ComboboxSelected>>", trocar_lista)

caixa = tk.Listbox(frame_esquerda, width=32, exportselection=False)
caixa.pack(fill="y", expand=True)
caixa.bind("<<ListboxSelect>>", mostrar_midia)

frame_direita = tk.Frame(janela)
frame_direita.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_topo = tk.Frame(frame_direita)
frame_topo.pack(fill="x")

frame_capa = tk.Frame(frame_topo, width=260, height=380)
frame_capa.pack(side="left", padx=(0, 10))
frame_capa.pack_propagate(False)

label_capa = tk.Label(frame_capa, text="Sem capa")
label_capa.pack(expand=True)

label_info = tk.Label(frame_topo, text="", justify="left", anchor="nw", wraplength=450)
label_info.pack(side="left", fill="both", expand=True)

frame_reviews = tk.LabelFrame(frame_direita, text="Sua review")
frame_reviews.pack(fill="x", pady=10)

label_reviews = tk.Label(frame_reviews, text="", justify="left", anchor="w", wraplength=600)
label_reviews.pack(fill="x", padx=5, pady=5)

frame_form = tk.LabelFrame(frame_direita, text="Avaliar")
frame_form.pack(fill="x")

tk.Label(frame_form, text="Nota (0.5 a 5.0):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entrada_nota = tk.Entry(frame_form, width=8)
entrada_nota.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_form, text="Comentário:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entrada_comentario = tk.Entry(frame_form, width=60)
entrada_comentario.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Button(frame_form, text="Avaliar", command=avaliar).grid(row=2, column=1, padx=5, pady=5, sticky="w")

trocar_lista()

janela.mainloop()