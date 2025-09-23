import tkinter as tk
from tkinter import ttk
import requests
import zipfile
import os
import shutil
from PIL import Image, ImageTk
import sys

# Sim, eu gerei o código com auxilio do ChatGPT porque eu tenho nenhum conhecimento de Python.
# O código faz o seguinte, ele lê um link que coloquei num txt raw e esse link baixa o modpack
# Ao baixar ele descompacta, deleta as pastas e substitui pelas do arquivo compactado
# Se você tem sugestões abra um ticket e me fala, tudo que eu queria era arrumar esse código.

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def baixar_e_descompactar():
    url_raw = "https://raw.githubusercontent.com/ItsOnlyMe360/Modpack-Updater/main/redirect.txt"

    try:
        label_status.config(text="Baixando atualização...", bg='#1f1f1f')
        root.update()

        response = requests.get(url_raw)
        response.raise_for_status()
        raw_text = response.text.strip()

        url_file = raw_text

        response_file = requests.get(url_file, stream=True)
        response_file.raise_for_status()

        zip_filename = "mods.zip"
        total_size = int(response_file.headers.get('content-length', 0))
        block_size = 1024
        downloaded_size = 0
        last_percent = 0

        with open(zip_filename, 'wb') as zip_file:
            for data in response_file.iter_content(block_size):
                zip_file.write(data)
                downloaded_size += len(data)
                percent = int((downloaded_size / total_size) * 100)

                if percent > last_percent:
                    label_status.config(text=f"Baixando atualização... {percent}%", bg='#1f1f1f')
                    root.update()
                    last_percent = percent

        label_status.config(text="Descompactando arquivos...", bg='#1f1f1f')
        root.update()

        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            total_files = len(zip_ref.namelist())
            extracted_files = 0
            last_percent = 0

            for file in zip_ref.namelist():
                zip_ref.extract(file, "temp")
                extracted_files += 1
                percent = int((extracted_files / total_files) * 100)

                if percent > last_percent:
                    label_status.config(text=f"Descompactando arquivos... {percent}%", bg='#1f1f1f')
                    root.update()
                    last_percent = percent

        minecraft_path = os.path.join(os.getcwd(), ".minecraft")

        if os.path.exists(minecraft_path):
            for folder in ["mods", "resourcepacks", "shaderpacks", "config", "MenuLayout", "kubejs"]:
                folder_path = os.path.join(minecraft_path, folder)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)

            merge_folders("temp", minecraft_path)
        else:
            os.rename("temp", minecraft_path)

        os.remove(zip_filename)

        label_status.config(text="Atualização concluída!", bg='#1f1f1f')

    except requests.exceptions.RequestException as e:
        label_status.config(text=f"Erro durante a atualização: {str(e)}", bg='##1f1f1f')

def merge_folders(src, dest):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks=True)
        else:
            shutil.copy(s, d)

def on_enter(event):
    button_label.config(image=button_hover)

def on_leave(event):
    button_label.config(image=button_image)

root = tk.Tk()
root.title("Modpack Updater")
root.resizable(False, False)
root.geometry("854x480")

icon_path = resource_path("icon2.ico")
root.iconbitmap(default=icon_path)

bg_image = Image.open(resource_path("bg.png"))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Carregar imagens do botão
button_image = Image.open(resource_path("botao.png"))
button_hover_image = Image.open(resource_path("botaohover.png"))

# Configurar eventos de rato para o botão
button_image = ImageTk.PhotoImage(button_image)
button_hover = ImageTk.PhotoImage(button_hover_image)
button_label = tk.Label(root, image=button_image, bd=0, relief="flat", cursor="hand2")
button_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

button_label.bind("<Enter>", on_enter)
button_label.bind("<Leave>", on_leave)
button_label.bind("<Button-1>", lambda event: baixar_e_descompactar())

label_status = tk.Label(root, text="", foreground="white", font=('Helvetica', 10), anchor='center', bg='#1f1f1f', padx=10, pady=5)
label_status.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

root.mainloop()
