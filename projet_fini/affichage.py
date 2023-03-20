import tkinter as tk
import subprocess
import schedule
import time
import webbrowser
from crontab import CronTab

# Définition des fonctions à exécuter lorsque les boutons sont cliqués
def run_script_1():
    nb1 = int(entry1.get())
    nb2 = int(entry2.get())
    subprocess.run(["python3", "service.py", str(nb1), str(nb2)])

def add_script_to_cron():
    script_to_run = "./logssh.py"
    cron = CronTab(user=True)
    
    # Supprime les anciennes entrées du même script pour éviter les doublons
    cron.remove_all(command=f'python3 {script_to_run}')

    job = cron.new(command=f'sudo python3 {script_to_run}')
    job.setall('*/5 * * * *')

    cron.write()



def run_script_2():
    subprocess.run(["sudo","python3", "surveillance_pc.py"])

def run_script_3():
    subprocess.run(["python3", "prerequis.py"])

def open_ggoogoe():
    url = "217.182.168.137:3000/analyse_perf"
    webbrowser.get('firefox').open_new_tab(url)

def open_url():
    url = "217.182.168.137:3000/analyse_url"
    webbrowser.get('firefox').open_new_tab(url)

def open_fichier():
    url = "217.182.168.137:3000/analyse_fichier"
    webbrowser.get('firefox').open_new_tab(url)

def open_help_window():
    help_window = tk.Toplevel(window)
    help_window.title("Help")
    
    help_text1 = tk.Label(help_window, text="Analyse des services", font=("Arial", 14, "bold"), fg="red")
    help_text1.pack(padx=10, pady=10)
    help_text2 = tk.Label(help_window, text=" c'est un scanner de vulnérabilités de services et de ports utilisant la bibliothèque Nmap et la base de données CVE (Common Vulnerabilities and Exposures).\n\n")
    help_text2.pack(padx=10, pady=10)
    
    help_text3 = tk.Label(help_window, text="Monitoring PC", font=("Arial", 14, "bold"), fg="red")
    help_text3.pack(padx=10, pady=10)
    help_text4 = tk.Label(help_window, text=" Ce script est un programme de surveillance réseau et de ressources système. Il combine la surveillance des adresses IP connectées au réseau, \n la vérification des connexions SSH, l'envoi d'alertes par e-mail et la surveillance des ressources système (CPU, RAM, stockage et réseau).\n\n")
    help_text4.pack(padx=10, pady=10)
    
    help_text5 = tk.Label(help_window, text="Installation des packages", font=("Arial", 14, "bold"), fg="red")
    help_text5.pack(padx=10, pady=10)
    help_text6 = tk.Label(help_window, text=" Cela va installer les modules, je sais que personne ne lis les aides mais on est la mon fréro 39-45 nous revoila")
    help_text6.pack(padx=10, pady=10)
# Création de la fenêtre et des boutons
window = tk.Tk()
window.title("Watchdog")
window.geometry("800x460")  # Largeur x Hauteur
window.resizable(width=False, height=False)

image = tk.PhotoImage(file="IMG_5626.gif")
image_label = tk.Label(window, image=image)
image_label.pack(side="left", anchor="nw")

title = tk.Label(window, text="ESTIAM ANTIVIRUS", font=("Arial", 20, "bold"))
title.pack(pady=10)




button1 = tk.Button(window, text="Analyse des services", command=run_script_1, bg="lightblue")
button2 = tk.Button(window, text="Monitoring PC", command=run_script_2, bg="lightgreen")
button3 = tk.Button(window, text="Installation des packages", command=run_script_3, bg="lightsalmon")
button4 = tk.Button(window, text="Site Details", command=open_ggoogoe, bg="lightyellow")
button5 = tk.Button(window, text="Analyse URL", command=open_url, bg="pink")
button6 = tk.Button(window, text="Analyse Fichier", command=open_fichier, bg="pink")
button_help = tk.Button(window, text="HELP", command=open_help_window, bg="orange")

# Placement des boutons dans la fenêtre
button1.pack(padx=0, pady=0, side="left")  # Ajout de 'side="left"' pour le bouton1
entry1 = tk.Entry(window, width=10)  # Modification de la largeur
entry1.pack(padx=0, pady=0, side="left")  # Ajout de 'side="left"' pour entry1

entry2 = tk.Entry(window, width=10)  # Modification de la largeur
entry2.pack(padx=0, pady=0, side="left")  # Ajout de 'side="left"' pour entry2

button2.pack(padx=10, pady=10)
button3.pack(padx=10, pady=10)
button4.pack(padx=10, pady=10)
button5.pack(padx=10, pady=10)
button6.pack(padx=10, pady=10)
button_help.pack(padx=10, pady=10)
button7 = tk.Button(window, text="Ajouter le script à la crontab", command=add_script_to_cron, bg="lightgray")
button7.pack(padx=10, pady=10)

copyright = tk.Label(window, text="© Louis, Kevin, Enzo", font=("Arial", 12))
copyright.pack(side="bottom", anchor="sw")

# Lancement de la boucle d'événements pour afficher la fenêtre
window.mainloop()