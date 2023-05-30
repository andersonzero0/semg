import nfc
from pymongo import MongoClient
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import binascii
from twilio.rest import Client
from PIL import Image, ImageTk
import urllib.request
import io

# Conexão com o MongoDB Atlas
client = MongoClient('mongodb+srv://root:projectnfc@cluster0.601pr9k.mongodb.net/?retryWrites=true&w=majority')
db = client['users']
collection = db['infos']

# Configuração do Twilio
account_sid = 'AC55d0f44906c38c5599002a6a090643d1'
auth_token = 'd25a46f9e39284954bd8dcbbe2381e27'
twilio_client = Client(account_sid, auth_token)

def on_connect(tag):
    global is_reading

    if not is_reading:
        return

    progress_bar['value'] = 30
    root.update_idletasks()

    tag_lida = True

    uid = binascii.hexlify(tag.identifier).decode("utf-8")

    query = {"uid": uid}
    data = collection.find_one(query)

    if data:
        progress_bar['value'] = 60
        root.update_idletasks()

        nome = data.get("name")
        turma = data.get("turma")
        nome_responsavel = data.get("name_resp")
        contato_responsavel = data.get("contact_resp")
        avatar_url = data.get("avatar")

        # Renderização da imagem
        image_data = urllib.request.urlopen(avatar_url).read()
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((100, 100))  # Ajuste o tamanho da imagem conforme necessário
        photo = ImageTk.PhotoImage(image)

        info_label.config(text=f"Tag Lida!\n\nNome: {nome}\nTurma: {turma}\nNome do Responsável: {nome_responsavel}\nContato do Responsável: {contato_responsavel}")
        avatar_label.config(image=photo)
        avatar_label.image = photo

        progress_bar['value'] = 90
        root.update_idletasks()

        mensagem = f"Olá, {nome_responsavel}! Seu(a) filho(a) {nome} da turma {turma} utilizou a tag NFC."
        
        # Envio da mensagem pelo Twilio
        message = twilio_client.messages.create(
            from_='whatsapp:+14155238886',
            body=mensagem,
            to='whatsapp:{0}'.format(contato_responsavel)
        )

        print(message.sid)

    else:
        info_label.config(text="Tag Lida!\n\nDados não encontrados para o UID da tag.")

    progress_bar['value'] = 100
    root.update_idletasks()

    is_reading = False

def iniciar_leitura():
    global is_reading

    if 'is_reading' not in locals():
        is_reading = False

    if is_reading:
        return

    is_reading = True

    progress_bar['value'] = 0
    root.update_idletasks()

    while is_reading:
        clf.connect(rdwr={'on-connect': on_connect})

def fechar_programa():
    clf.close()
    root.destroy()

# Cria um objeto de leitor NFC
clf = nfc.ContactlessFrontend('ttyUSB0')

# Configuração da interface gráfica
root = tk.Tk()
root.title("Leitor de Tags NFC")
root.geometry("600x500")

# Label para exibir as informações
info_label = tk.Label(root, text="")
info_label.pack()

# Label para exibir o avatar
avatar_label = tk.Label(root)
avatar_label.pack(pady=10)

# Barra de progresso
progress_bar = ttk.Progressbar(root, orient='horizontal', length=200, mode='determinate')
progress_bar.pack(pady=10)

# Botão para iniciar a leitura da tag
btn_iniciar = tk.Button(root, text="Iniciar Leitura", command=iniciar_leitura)
btn_iniciar.pack(pady=10)

# Botão para fechar o programa
btn_fechar = tk.Button(root, text="Fechar Programa", command=fechar_programa)
btn_fechar.pack()

# Loop principal da interface gráfica
root.mainloop()

