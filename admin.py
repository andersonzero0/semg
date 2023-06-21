from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
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
frequencia_collection = db.frequencia_entrada  # New collection: frequencia_entrada

def adicionar_dado():
    name_aluno = entry_name_aluno.get()
    name_resp = entry_name_resp.get()
    contact_resp = entry_contact_resp.get()
    turma = entry_turma.get()
    avatar = entry_avatar.get()
    uid = entry_tag_uid.get()  # New field: 'uid'

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
        "uid": uid,
        "status": "red"
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

def visualizar_frequencia():
    frequencia = frequencia_collection.find()

    # Clear the table
    for row in frequencia_treeview.get_children():
        frequencia_treeview.delete(row)

    # Insert data into the table
    for entrada in frequencia:
        data = entrada.get("data", "")
        quantidade = entrada.get("quantidade", "")

        frequencia_treeview.insert("", "end", values=(data, quantidade))

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

def renderizar_imagem():
    # Get the image URL from Imgur
    image_url = "https://i.ibb.co/nmKRMwN/Captura-de-tela-de-2023-06-03-17-13-34.png"  # Replace with your image URL

    try:
        # Fetch the image data
        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()

        # Create an Image object from the data
        image = Image.open(io.BytesIO(image_data))

        # Resize the image if necessary
        max_width = 400
        if image.width > max_width:
            ratio = max_width / image.width
            new_width = int(image.width * ratio * 2)
            new_height = int(image.height * ratio * 2)
            image = image.resize((new_width, new_height))

        # Create a PhotoImage object from the Image
        photo = ImageTk.PhotoImage(image)

        # Display the image on a Label
        label_image.configure(image=photo)
        label_image.image = photo  # Keep a reference to avoid garbage collection
    except urllib.error.URLError:
        messagebox.showerror("Erro", "Erro ao carregar a imagem.")
    except OSError:
        messagebox.showerror("Erro", "Erro ao processar a imagem.")

# Create the main window
root = ThemedTk(theme="breeze")
root.title("Cadastro NFC")
root.geometry("1024x600")

# Create the notebook
notebook = ttk.Notebook(root, height=800, width=950)
notebook.pack(pady=10)

# Create the tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)  # New tab

tab1.pack(fill="both", expand=1)
tab2.pack(fill="both", expand=1)
tab3.pack(fill="both", expand=1)
tab4.pack(fill="both", expand=1)  # New tab

# Add the tabs to the notebook
notebook.add(tab1, text="Cadastro")
notebook.add(tab2, text="Visualização")
notebook.add(tab3, text="Imagem")
notebook.add(tab4, text="Frequência")  # New tab

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

label_avatar = Label(tab1, text="Avatar (URL):")
label_avatar.grid(row=4, column=0, padx=10, pady=10, sticky="e")
entry_avatar = Entry(tab1)
entry_avatar.grid(row=4, column=1, padx=10, pady=10)

entry_uid = Entry(tab1, state="readonly")
entry_uid.grid(row=6, column=1, padx=10, pady=10)

button_add = Button(tab1, text="Adicionar", command=adicionar_dado)
button_add.grid(row=8, column=0, padx=10, pady=10)

# Create a treeview for the Visualização tab
treeview = ttk.Treeview(tab2, columns=("Nome Aluno", "Nome Responsável", "Telefone Responsável", "Turma", "UID"))
treeview.heading("#0", text="ID")
treeview.heading("Nome Aluno", text="Nome Aluno")
treeview.heading("Nome Responsável", text="Nome Responsável")
treeview.heading("Telefone Responsável", text="Telefone Responsável")
treeview.heading("Turma", text="Turma")
treeview.heading("UID", text="UID")

treeview.column("#0", width=50)
treeview.column("Nome Aluno", width=150)
treeview.column("Nome Responsável", width=150)
treeview.column("Telefone Responsável", width=150)
treeview.column("Turma", width=100)
treeview.column("UID", width=200)

treeview.pack(pady=10)

# Create a treeview for the Frequência tab
frequencia_treeview = ttk.Treeview(tab4, columns=("Data", "Quantidade"))
frequencia_treeview.heading("#0", text="ID")
frequencia_treeview.heading("Data", text="Data")
frequencia_treeview.heading("Quantidade", text="Quantidade")

frequencia_treeview.column("#0", width=50)
frequencia_treeview.column("Data", width=200)
frequencia_treeview.column("Quantidade", width=100)

frequencia_treeview.pack(pady=10)

# Create a button for the Visualização tab to refresh the data
button_refresh = Button(tab2, text="Atualizar", command=visualizar_dados)
button_refresh.pack(pady=10)

# Create a button for the Frequência tab to refresh the data
button_frequencia_refresh = Button(tab4, text="Atualizar", command=visualizar_frequencia)
button_frequencia_refresh.pack(pady=10)

# Create a label and an image widget for the Imagem tab
label_image = Label(tab3)
label_image.pack(pady=10)

# Create a button for the Imagem tab to render the image
button_render_image = Button(tab3, text="Renderizar Imagem", command=renderizar_imagem)
button_render_image.pack(pady=10)

# Create a label and an entry field for reading the NFC tag
label_tag_uid = Label(tab1, text="UID da Tag NFC:")
label_tag_uid.grid(row=6, column=0, padx=10, pady=10, sticky="e")

tag_uid_value = StringVar()
entry_tag_uid = Entry(tab1, textvariable=tag_uid_value, state="readonly")
entry_tag_uid.grid(row=6, column=1, padx=10, pady=10)

button_read_nfc_tag = Button(tab1, text="Ler Tag NFC", command=read_nfc_tag)
button_read_nfc_tag.grid(row=8, column=1, padx=10, pady=10)

# Load data into the table when the application starts
visualizar_dados()
visualizar_frequencia()

root.mainloop()

