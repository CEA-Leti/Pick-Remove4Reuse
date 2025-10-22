from tkinter import messagebox
from tkinter import filedialog
import tkinter as tk

def show_info():
    messagebox.showinfo("Information", "Ceci est un message d'information")
    
def show_warning():
    messagebox.showwarning("Avertissement", "Ceci est un message d'avertissement")
    
def show_error():
    messagebox.showerror("Erreur", "Une erreur s'est produite !")

def select_directory():
    directory_path = filedialog.askdirectory(title="Choisir un dossier")
    if directory_path:
        return directory_path
        
show_info()
directory_path= select_directory()
print(directory_path)


# Fonction pour ouvrir une fenêtre pop-up
def open_popup():
    popup = tk.Toplevel(root)
    popup.title("Fenêtre pop-up")
    popup.geometry("300x200")

    label = tk.Label(popup, text="Entrez votre nom :")
    label.pack(pady=10)

    entry = tk.Entry(popup)
    entry.pack(pady=5)

    # Bouton pour fermer la fenêtre
    close_button = tk.Button(popup, text="Fermer", command=popup.destroy)
    close_button.pack(pady=10)

def open_file():
    file_path = filedialog.askopenfilename(title="Ouvrir un fichier", filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")])
    if file_path:
        messagebox.showinfo("Fichier sélectionné", file_path)
open_file()

# Fenêtre principale
root = tk.Tk()
root.title("Fenêtre principale")
root.geometry("400x300")

# Bouton pour ouvrir la fenêtre pop-up
open_button = tk.Button(root, text="Ouvrir une fenêtre pop-up", command=open_popup)
open_button.pack(pady=50)

root.mainloop()