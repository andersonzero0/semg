from tkinter import *
from tkinter import messagebox
from pymongo import MongoClient

# Conecta-se ao banco de dados MongoDB Atlas
client = MongoClient("mongodb+srv://root:projectnfc@cluster0.mqvfesd.mongodb.net/?retryWrites=true&w=majority")
db = client.users
collection = db.infos

def adicionar_dado():
    nome_aluno = entry_nome_aluno.get()
    nome_responsavel = entry_nome_responsavel.get()
    telefone_responsavel = entry_telefone_responsavel.get()
    turma_aluno = entry_turma_aluno.get()

    novo_dado = {
        "nome_aluno": nome_aluno,
        "nome_responsavel": nome_responsavel,
        "telefone_responsavel": telefone_responsavel,
        "turma_aluno": turma_aluno
    }

    collection.insert_one(novo_dado)

    messagebox.showinfo("Sucesso", "Dado adicionado com sucesso!")

def excluir_dado():
    nome_aluno = entry_nome_aluno.get()

    collection.delete_one({"nome_aluno": nome_aluno})

    messagebox.showinfo("Sucesso", "Dado excluído com sucesso!")

def editar_dado():
    nome_aluno = entry_nome_aluno.get()
    nome_responsavel = entry_nome_responsavel.get()
    telefone_responsavel = entry_telefone_responsavel.get()
    turma_aluno = entry_turma_aluno.get()

    novo_dado = {
        "nome_aluno": nome_aluno,
        "nome_responsavel": nome_responsavel,
        "telefone_responsavel": telefone_responsavel,
        "turma_aluno": turma_aluno
    }

    collection.update_one({"nome_aluno": nome_aluno}, {"$set": novo_dado})

    messagebox.showinfo("Sucesso", "Dado atualizado com sucesso!")

def visualizar_dados():
    dados = collection.find()

    for dado in dados:
        print(dado)

# Cria a interface gráfica usando tkinter
root = Tk()
root.title("Cadastro de Alunos")

# Labels
label_nome_aluno = Label(root, text="Nome do Aluno")
label_nome_responsavel = Label(root, text="Nome do Responsável")
label_telefone_responsavel = Label(root, text="Telefone do Responsável")
label_turma_aluno = Label(root, text="Turma do Aluno")

# Entradas de texto
entry_nome_aluno = Entry(root)
entry_nome_responsavel = Entry(root)
entry_telefone_responsavel = Entry(root)
entry_turma_aluno = Entry(root)

# Botões
button_adicionar = Button(root, text="Adicionar", command=adicionar_dado)
button_excluir = Button(root, text="Excluir", command=excluir_dado)
button_editar = Button(root, text="Editar", command=editar_dado)
button_visualizar = Button(root, text="Visualizar", command=visualizar_dados)

# Posicionamento dos componentes
label_nome_aluno.grid(row=0, column=0)
entry_nome_aluno.grid(row=0, column=1)
label_nome_responsavel.grid(row=1, column=0)
entry_nome_responsavel.grid(row=1, column=1)
label_telefone_responsavel.grid(row=2, column=0)
entry_telefone_responsavel.grid(row=2, column=1)
label_turma_aluno.grid(row=3, column=0)
entry_turma_aluno.grid(row=3, column=1)
button_adicionar.grid(row=4, column=0)
button_excluir.grid(row=4, column=1)
button_editar.grid(row=5, column=0)
button_visualizar.grid(row=5, column=1)

root.mainloop()
