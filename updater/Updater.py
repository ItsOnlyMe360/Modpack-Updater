import tkinter as tk
from tkinter import ttk, messagebox
import requests
import zipfile
import os
import shutil
from PIL import Image, ImageTk
import sys
import threading
from pathlib import Path

# --- FUNÇÕES AUXILIARES ---

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para o executável PyInstaller/Nuitka. """
    try:
        # PyInstaller/Nuitka cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def start_update_thread():
    """ Inicia a atualização em uma nova thread para não congelar a GUI. """
    button_label.config(state="disabled", cursor="")
    button_label.unbind("<Button-1>")
    update_thread = threading.Thread(target=baixar_e_descompactar)
    update_thread.daemon = True
    update_thread.start()

# --- FUNÇÕES DE ATUALIZAÇÃO DA INTERFACE (GUI) ---

def update_status(text):
    label_status.config(text=text)

def update_progress(value):
    progress_bar['value'] = value

def show_error(message):
    messagebox.showerror("Erro na Atualização", message)
    reset_ui_to_initial_state()

def show_success():
    messagebox.showinfo("Sucesso", "Modpack atualizado com sucesso!")
    reset_ui_to_initial_state()

def reset_ui_to_initial_state():
    label_status.config(text="Pronto para atualizar.")
    progress_bar['value'] = 0
    button_label.config(state="normal", cursor="hand2")
    button_label.bind("<Button-1>", lambda event: start_update_thread())

# --- LÓGICA PRINCIPAL DA ATUALIZAÇÃO ---

def baixar_e_descompactar():
    url_redirect = "https://raw.githubusercontent.com/ItsOnlyMe360/Modpack-Updater/main/redirect.txt"
    url_folders_list = "https://raw.githubusercontent.com/ItsOnlyMe360/Modpack-Updater/main/folders.txt"
    
    try:
        root.after(0, update_status, "Obtendo configurações...")
        root.after(0, update_progress, 0)
        
        response_url = requests.get(url_redirect)
        response_url.raise_for_status()
        download_url = response_url.text.strip()

        response_folders = requests.get(url_folders_list)
        response_folders.raise_for_status()
        pastas_para_deletar = [folder.strip() for folder in response_folders.text.strip().split(',') if folder]

        root.after(0, update_status, "Baixando o modpack...")
        zip_filename = "mods_temp.zip"
        
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(zip_filename, 'wb') as f:
                downloaded_size = 0
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        root.after(0, update_progress, percent)

        root.after(0, update_status, "Extraindo arquivos...")
        root.after(0, update_progress, 0)
        temp_dir = Path("temp_modpack_extraction")
        
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            for i, file in enumerate(file_list, 1):
                zip_ref.extract(file, temp_dir)
                percent = (i / total_files) * 100
                root.after(0, update_progress, percent)

        root.after(0, update_status, "Instalando a atualização...")
        minecraft_path = Path.cwd() / "minecraft"
        minecraft_path.mkdir(exist_ok=True)

        for folder_name in pastas_para_deletar:
            folder_to_delete = minecraft_path / folder_name
            if folder_to_delete.is_dir():
                shutil.rmtree(folder_to_delete)
        
        shutil.copytree(temp_dir, minecraft_path, dirs_exist_ok=True)
        
        root.after(0, update_status, "Finalizando...")
        os.remove(zip_filename)
        shutil.rmtree(temp_dir)
        
        root.after(0, update_status, "Atualização concluída!")
        root.after(0, show_success)

    except requests.exceptions.RequestException as e:
        root.after(0, show_error, f"Não foi possível baixar a atualização. Verifique sua conexão com a internet.\n\nDetalhes: {e}")
    except zipfile.BadZipFile:
        root.after(0, show_error, "O arquivo baixado está corrompido e não é um arquivo ZIP válido.")
    except Exception as e:
        root.after(0, show_error, f"Ocorreu um erro inesperado durante a atualização:\n\n{e}")

# --- CONFIGURAÇÃO DA INTERFACE GRÁFICA ---

def on_enter(event):
    if button_label['state'] == 'normal':
        button_label.config(image=button_hover)

def on_leave(event):
    button_label.config(image=button_image)

root = tk.Tk()
root.title("Modpack Updater")
root.resizable(False, False)
root.geometry("854x480")

try:
    # MODIFICADO: Adicionado 'assets' ao caminho do ícone
    icon_path = resource_path(os.path.join("assets", "icon2.ico"))
    if os.path.exists(icon_path):
        root.iconbitmap(default=icon_path)
except tk.TclError:
    print("Ícone 'assets/icon2.ico' não encontrado ou corrompido.")

try:
    # MODIFICADO: Adicionado 'assets' ao caminho da imagem de fundo
    bg_image_pil = Image.open(resource_path(os.path.join("assets", "bg.png")))
    bg_photo = ImageTk.PhotoImage(bg_image_pil)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
except FileNotFoundError:
    print("Imagem de fundo 'assets/bg.png' não encontrada.")
    root.config(bg="#1f1f1f")

try:
    # MODIFICADO: Adicionado 'assets' aos caminhos das imagens do botão
    button_image_pil = Image.open(resource_path(os.path.join("assets", "botao.png")))
    button_hover_pil = Image.open(resource_path(os.path.join("assets", "botaohover.png")))
    button_image = ImageTk.PhotoImage(button_image_pil)
    button_hover = ImageTk.PhotoImage(button_hover_pil)
    
    button_label = tk.Label(root, image=button_image, bd=0, relief="flat", cursor="hand2", bg="#1f1f1f")
    button_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    button_label.bind("<Enter>", on_enter)
    button_label.bind("<Leave>", on_leave)
    button_label.bind("<Button-1>", lambda event: start_update_thread())
except FileNotFoundError:
    print("Imagens do botão ('assets/botao.png', 'assets/botaohover.png') não encontradas.")
    button_label = tk.Button(root, text="Atualizar", command=start_update_thread)
    button_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

label_status = tk.Label(root, text="Pronto para atualizar.", foreground="white", font=('Helvetica', 10), anchor='center', bg='#1f1f1f')
label_status.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

style = ttk.Style(root)
style.theme_use('clam')
style.configure("red.Horizontal.TProgressbar", foreground='#c80000', background='#c80000', troughcolor='#1f1f1f', bordercolor="#1f1f1f", lightcolor="#c80000", darkcolor="#c80000")
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", style="red.Horizontal.TProgressbar")
progress_bar.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

root.mainloop()
