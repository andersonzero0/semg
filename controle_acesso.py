import nfc
from pymongo import MongoClient
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import binascii
from twilio.rest import Client
from PIL import Image, ImageTk, ImageDraw, ImageOps
import urllib.request
import io
import logging

# Configurar o registro de logs
logging.basicConfig(level=logging.INFO, filename='nfc_reader.log', format='%(asctime)s - %(levelname)s - %(message)s')

# Conexão com o MongoDB Atlas
try:
    client = MongoClient('mongodb+srv://root:projectnfc@cluster0.601pr9k.mongodb.net/?retryWrites=true&w=majority')
    db = client['users']
    collection = db['infos']
except Exception as e:
    logging.error("Erro ao conectar ao MongoDB: %s", e)

# Configuração do Twilio
account_sid = 'AC55d0f44906c38c5599002a6a090643d1'
auth_token = 'd25a46f9e39284954bd8dcbbe2381e27'
try:
    twilio_client = Client(account_sid, auth_token)
except Exception as e:
    logging.error("Erro ao conectar ao Twilio: %s", e)

# Variáveis para controle de status e último UID lido
status_atual = None
last_uid = None

def create_circle_mask(image, size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

def on_connect(tag):
    global is_reading, last_uid, status_atual

    if not is_reading:
        return

    try:
        progress_bar['value'] = 30
        root.update_idletasks()

        uid = binascii.hexlify(tag.identifier).decode("utf-8")

        # Verifique se o UID atual é igual ao último UID lido
        if uid == last_uid:
            return

        last_uid = uid

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
            image = image.resize((100, 100))

            # Criação da máscara circular para a imagem
            rounded_image = create_circle_mask(image, (100, 100))

            photo = ImageTk.PhotoImage(rounded_image)

            info_label.config(text=f"Nome: {nome}\nTurma: {turma}\nNome do Responsável: {nome_responsavel}\nContato do Responsável: {contato_responsavel}")
            avatar_label.config(image=photo)
            avatar_label.image = photo

            progress_bar['value'] = 90
            root.update_idletasks()

            mensagem = ""

            # Verifique o status atual e defina a mensagem apropriada
            if status_atual.get() == "Entrada":
                mensagem = f"Olá, {nome_responsavel}! Seu(a) filho(a) {nome} da turma {turma} entrou na escola."
                data["status"] = "green"  # Update 'status' to 'green' for entrada
            elif status_atual.get() == "Saída":
                mensagem = f"Olá, {nome_responsavel}! Seu(a) filho(a) {nome} da turma {turma} saiu da escola."
                data["status"] = "red"  # Update 'status' to 'red' for saida

            # Atualize o documento no MongoDB
            collection.update_one(query, {"$set": data})

            # Envio da mensagem pelo Twilio
            if mensagem:
                try:
                    message = twilio_client.messages.create(
                        from_='whatsapp:+14155238886',
                        body=mensagem,
                        to='whatsapp:{0}'.format(contato_responsavel)
                    )
                    logging.info("Mensagem enviada pelo Twilio: SID %s", message.sid)
                except Exception as e:
                    logging.error("Erro ao enviar mensagem pelo Twilio: %s", e)

            # Contagem de frequência de entrada
            if status_atual.get() == "Entrada":
                now = datetime.now()
                if now.hour == 18 and 00 <= now.minute <= 59 or now.hour == 20 and now.minute <= 00:
                    frequency_collection = db['frequencia_entrada']
                    today = datetime.now().strftime("%Y-%m-%d")
                    query = {"data": today}
                    frequency_data = frequency_collection.find_one(query)
                    if frequency_data:
                        count = frequency_data.get("quantidade")
                        frequency_collection.update_one(query, {"$set": {"quantidade": count + 1}})
                    else:
                        frequency_collection.insert_one({"data": today, "quantidade": 1})

        else:
            info_label.config(text="Tag Lida!\n\nDados não encontrados para o UID da tag.")

        progress_bar['value'] = 100
        root.update_idletasks()

        # Continue lendo tags NFC
        clf.connect(rdwr={'on-connect': on_connect})

    except Exception as e:
        logging.error("Erro durante a leitura da tag NFC: %s", e)


def iniciar_leitura():
    global is_reading

    if 'is_reading' not in locals():
        is_reading = False

    if is_reading:
        return

    is_reading = True

    progress_bar['value'] = 0
    root.update_idletasks()

    try:
        # Iniciar leitura de tags NFC
        clf.connect(rdwr={'on-connect': on_connect})

        # Inicialização da coleção de frequência de entrada
        frequency_collection = db['frequencia_entrada']
        today = datetime.now().strftime("%Y-%m-%d")
        frequency_collection.update_one({"data": today}, {"$setOnInsert": {"quantidade": 0}}, upsert=True)

        # Continue esperando novas tags NFC
        iniciar_leitura()

    except Exception as e:
        logging.error("Erro durante a leitura da tag NFC: %s", e)


def fechar_programa():
    try:
        clf.close()
        root.destroy()
    except Exception as e:
        logging.error("Erro ao fechar o programa: %s", e)

def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)

# Cria um objeto de leitor NFC
try:
    clf = nfc.ContactlessFrontend('ttyUSB0')
except Exception as e:
    logging.error("Erro ao conectar ao leitor NFC: %s", e)

# Configuração da interface gráfica
root = ThemedTk(theme="breeze")
root.title("SEMG")
root.geometry("800x600")

is_fullscreen = False
root.bind("<F11>", toggle_fullscreen)

# Frame para informações da tag
tag_frame = ttk.Frame(root, padding=20, relief='raised')
tag_frame.pack(pady=20)

# Label para exibir o avatar
avatar_label = ttk.Label(tag_frame)
avatar_label.pack(side='left', padx=20)

# Frame para informações textuais
info_frame = ttk.Frame(tag_frame)
info_frame.pack(side='left')

# Label para exibir as informações
info_label = ttk.Label(info_frame, text="", font=('Arial', 12), anchor='w')
info_label.pack(pady=10)

# Variável para armazenar o status selecionado
status_atual = tk.StringVar()

# Frame para os radio buttons
status_frame = ttk.Frame(root)
status_frame.pack()

# Radio button para o status de "Entrada"
entrada_radio = ttk.Radiobutton(status_frame, text="Entrada", variable=status_atual, value="Entrada")
entrada_radio.pack(side='left', padx=10)

# Radio button para o status de "Saída"
saida_radio = ttk.Radiobutton(status_frame, text="Saída", variable=status_atual, value="Saída")
saida_radio.pack(side='left')

# Barra de progresso
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=20)

# Botão para iniciar a leitura
start_button = ttk.Button(root, text="Iniciar Leitura", command=iniciar_leitura)
start_button.pack(pady=10)

# Botão para fechar o programa
close_button = ttk.Button(root, text="Fechar", command=fechar_programa)
close_button.pack(pady=10)

# Iniciar o loop da interface gráfica
root.mainloop()

