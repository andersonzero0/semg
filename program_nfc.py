from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient
from PIL import Image, ImageTk
import urllib.request
import io
import re
import nfc
import nfc.clf
import clipboard

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
    uid = entry_uid.get()  # New field: 'uid'

    # Validate input fields
    if not validate_name(name_aluno):
        messagebox.showerror("Erro", "Nome do Aluno inválido. Insira apenas letras.")
        return
    if not validate_name(name_resp):
        messagebox.showerror("Erro", "Nome do Responsável inválido. Insira apenas letras.")
        return
    if not validate_contact(contact_resp):
        messagebox.showerror("Erro", "Telefone do Responsável inválido. Insira apenas números.")
        return

    novo_dado = {
        "name": name_aluno,
        "name_resp": name_resp,
        "contact_resp": contact_resp,
        "turma": turma,
        "avatar": avatar,
        "uid": uid  # Add 'uid' field to the data
    }

    collection.insert_one(novo_dado)

    messagebox.showinfo("Sucesso", "Dado adicionado com sucesso!")
    visualizar_dados()

def validate_name(name):
    pattern = r'^[a-zA-Z\s\S]+$'
    return re.match(pattern, name)

def validate_contact(contact):
    pattern = r'^[a-zA-Z0-9\s\S]+$'
    return re.match(pattern, contact)

def visualizar_dados():
    dados = collection.find()

    # Clear the table
    for row in treeview.get_children():
        treeview.delete(row)

    # Insert data into the table
    for dado in dados:
        nome_aluno = dado.get("name", "")  # Update field name
        nome_responsavel = dado.get("name_resp", "")  # Update field name
        telefone_responsavel = dado.get("contact_resp", "")  # Update field name
        turma = dado.get("turma", "")
        uid = dado.get("uid", "")  # New field: 'uid'

        treeview.insert("", "end", values=(nome_aluno, nome_responsavel, telefone_responsavel, turma, uid))  # Add 'uid' to values

def atualizar_dados():
    visualizar_dados()

def read_nfc_tag():
    clf = nfc.ContactlessFrontend()

    try:
        clf.open('ttyUSB0')  # Specify the FTDI TTL port
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        uid = tag.identifier.hex()
        tag_uid_value.set(uid)
        messagebox.showinfo("Tag NFC Lida", "UID da Tag: {}".format(uid))
    except nfc.exceptions.NFCDeviceNotFoundError:
        messagebox.showerror("Erro", "Nenhum dispositivo NFC encontrado.")
    except nfc.exceptions.TimeoutError:
        messagebox.showerror("Erro", "Tempo limite de leitura excedido.")
    finally:
        clf.close()

def copy_to_clipboard(uid):
    clipboard.copy(uid)
    messagebox.showinfo("Sucesso", "UID da Tag copiado para a área de transferência.")

# Create the main window
root = Tk()
root.title("Cadastro NFC")
root.geometry("600x400")

# Create the notebook
notebook = ttk.Notebook(root)
notebook.pack(pady=10)

# Create the tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

tab1.pack(fill="both", expand=1)
tab2.pack(fill="both", expand=1)

# Add the tabs to the notebook
notebook.add(tab1, text="Cadastro")
notebook.add(tab2, text="Visualização")

# Create labels and entry fields for the Cadastro tab
label_name_aluno = Label(tab1, text="Nome do Aluno:")
label_name_aluno.grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_name_aluno = Entry(tab1)
entry_name_aluno.grid(row=0, column=1, padx=10, pady=10)

label_name_resp = Label(tab1, text="Nome do Responsável:")
label_name_resp.grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_name_resp = Entry(tab1)
entry_name_resp.grid(row=1, column=1, padx=10, pady=10)

label_contact_resp = Label(tab1, text="Telefone do Responsável:")
label_contact_resp.grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_contact_resp = Entry(tab1)
entry_contact_resp.grid(row=2, column=1, padx=10, pady=10)

label_turma = Label(tab1, text="Turma:")
label_turma.grid(row=3, column=0, padx=10, pady=10, sticky="e")
entry_turma = Entry(tab1)
entry_turma.grid(row=3, column=1, padx=10, pady=10)

label_avatar = Label(tab1, text="Avatar:")
label_avatar.grid(row=4, column=0, padx=10, pady=10, sticky="e")
entry_avatar = Entry(tab1)
entry_avatar.grid(row=4, column=1, padx=10, pady=10)

label_uid = Label(tab1, text="UID da Tag:")
label_uid.grid(row=5, column=0, padx=10, pady=10, sticky="e")
entry_uid = Entry(tab1, state="readonly")
entry_uid.grid(row=5, column=1, padx=10, pady=10)

button_read_tag = Button(tab1, text="Ler Tag NFC", command=read_nfc_tag)
button_read_tag.grid(row=6, column=0, padx=10, pady=10)

button_add = Button(tab1, text="Adicionar", command=adicionar_dado)
button_add.grid(row=6, column=1, padx=10, pady=10)

# Create a frame for the Visualização tab
frame_visualizar = Frame(tab2)
frame_visualizar.pack(pady=20)

# Create a treeview inside the frame
treeview = ttk.Treeview(frame_visualizar, columns=("Nome Aluno", "Nome Responsável", "Telefone Responsável", "Turma", "UID"))
treeview.pack(side=LEFT)

# Configure the treeview columns
treeview.column("#0", width=0, stretch=NO)
treeview.column("Nome Aluno", anchor=W, width=100)
treeview.column("Nome Responsável", anchor=W, width=100)
treeview.column("Telefone Responsável", anchor=W, width=100)
treeview.column("Turma", anchor=W, width=100)
treeview.column("UID", anchor=W, width=100)  # Add 'UID' column

# Create treeview headings
treeview.heading("#0", text="", anchor=W)
treeview.heading("Nome Aluno", text="Nome Aluno", anchor=W)
treeview.heading("Nome Responsável", text="Nome Responsável", anchor=W)
treeview.heading("Telefone Responsável", text="Telefone Responsável", anchor=W)
treeview.heading("Turma", text="Turma", anchor=W)
treeview.heading("UID", text="UID")  # Add 'UID' heading

# Add a vertical scrollbar to the treeview
scrollbar = ttk.Scrollbar(frame_visualizar)
scrollbar.pack(side=RIGHT, fill=Y)
treeview.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=treeview.yview)

# Create a StringVar to hold the tag UID value
tag_uid_value = StringVar()
entry_uid.config(textvariable=tag_uid_value)

# Initialize the visualização dos dados
visualizar_dados()

# Run the main loop
root.mainloop()
