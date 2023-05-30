from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient

# Connect to the MongoDB Atlas database
client = MongoClient("mongodb+srv://root:projectnfc@cluster0.601pr9k.mongodb.net/?retryWrites=true&w=majority")
db = client.users
collection = db.infos

def adicionar_dado():
    name_aluno = entry_name_aluno.get()
    name_resp = entry_name_resp.get()
    contact_resp = entry_contact_resp.get()
    turma = entry_turma.get()
    avatar = entry_avatar.get()

    novo_dado = {
        "name_aluno": name_aluno,
        "name_resp": name_resp,
        "contact_resp": contact_resp,
        "turma": turma,
        "avatar": avatar
    }

    collection.insert_one(novo_dado)

    messagebox.showinfo("Sucesso", "Dado adicionado com sucesso!")

def excluir_dado():
    name_aluno = entry_name_aluno.get()

    collection.delete_one({"name_aluno": name_aluno})

    messagebox.showinfo("Sucesso", "Dado excluído com sucesso!")

def editar_dado():
    name_aluno = entry_name_aluno.get()
    name_resp = entry_name_resp.get()
    contact_resp = entry_contact_resp.get()
    turma = entry_turma.get()
    avatar = entry_avatar.get()

    novo_dado = {
        "name_aluno": name_aluno,
        "name_resp": name_resp,
        "contact_resp": contact_resp,
        "turma": turma,
        "avatar": avatar
    }

    collection.update_one({"name_aluno": name_aluno}, {"$set": novo_dado})

    messagebox.showinfo("Sucesso", "Dado atualizado com sucesso!")

def visualizar_dados():
    dados = collection.find()

    # Clear the table
    for row in treeview.get_children():
        treeview.delete(row)

    # Insert data into the table
    for dado in dados:
        nome_aluno = dado.get("name", "")
        nome_responsavel = dado.get("name_resp", "")
        telefone_responsavel = dado.get("contact_resp", "")
        turma = dado.get("turma", "")

        treeview.insert("", "end", values=(nome_aluno, nome_responsavel, telefone_responsavel, turma))



# Create the GUI using tkinter
root = Tk()
root.title("Cadastro de Alunos")

# Labels
label_name_aluno = Label(root, text="Nome do Aluno")
label_name_resp = Label(root, text="Nome do Responsável")
label_contact_resp = Label(root, text="Telefone do Responsável")
label_turma = Label(root, text="Turma")
label_avatar = Label(root, text="Avatar")

# Text Entries
entry_name_aluno = Entry(root)
entry_name_resp = Entry(root)
entry_contact_resp = Entry(root)
entry_turma = Entry(root)
entry_avatar = Entry(root)

# Buttons
button_adicionar = Button(root, text="Adicionar", command=adicionar_dado)
button_excluir = Button(root, text="Excluir", command=excluir_dado)
button_editar = Button(root, text="Editar", command=editar_dado)
button_visualizar = Button(root, text="Visualizar", command=visualizar_dados)

# Table
columns = ("Nome Aluno", "Nome Responsável", "Telefone Responsável", "Turma")
treeview = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    treeview.heading(col, text=col)

# Scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=treeview.yview)
treeview.configure(yscroll=scrollbar.set)

# Positioning the components
label_name_aluno.grid(row=0, column=0)
entry_name_aluno.grid(row=0, column=1)
label_name_resp.grid(row=1, column=0)
entry_name_resp.grid(row=1, column=1)
label_contact_resp.grid(row=2, column=0)
entry_contact_resp.grid(row=2, column=1)
label_turma.grid(row=3, column=0)
entry_turma.grid(row=3, column=1)
label_avatar.grid(row=4, column=0)
entry_avatar.grid(row=4, column=1)
button_adicionar.grid(row=5, column=0)
button_excluir.grid(row=5, column=1)
button_editar.grid(row=6, column=0)
button_visualizar.grid(row=6, column=1)
treeview.grid(row=7, columnspan=2, padx=5, pady=5)
scrollbar.grid(row=7, column=2, sticky="ns")

root.mainloop()

