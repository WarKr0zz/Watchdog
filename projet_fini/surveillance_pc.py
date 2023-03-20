import smtplib
from scapy.all import srp, Ether, ARP
import time
from pymongo import MongoClient
import socket
import psutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from queue import Queue
import threading
from datetime import datetime
import os
import signal
import uuid
import sys


# Connexion à MongoDB
client = MongoClient("mongodb://217.182.168.137:2717/")
db = client["monitoring"]
collection = db["ressource"]
collection2 = db["processus"]


# Paramètres de l'e-mail
sender_email = "econte0108@gmail.com"
receiver_email = "econte0108@gmail.com"
password = "ixhtveyarvmcplrj"

# Domaine d'IP à surveiller
SUBNET = '192.168.1.0/24'

# Liste des adresses IP actuellement connectées
already_detected = set()


data_cpu = []
data_ram = []
data_network_sent = []
data_network_received = []
fig = plt.figure()
ax1 = fig.add_subplot(5, 1, 1)
ax2 = fig.add_subplot(5, 1, 2)
ax4 = fig.add_subplot(5, 1, 4)
ax5 = fig.add_subplot(5, 1, 5)

def insert_data_to_mongodb(cpu, ram, network_sent, network_received):
    data = {
        "adresse_mac":hex(uuid.getnode()),
        "timestamp": datetime.now(),
        "cpu": cpu,
        "ram": ram,
        "network_sent": network_sent,
        "network_received": network_received,
    }
    collection.insert_one(data)


def update_graph(i):
    global data_cpu, data_ram, data_network_sent, data_network_received

    surveiller_ressources()

    insert_data_to_mongodb(
        data_cpu[-1],
        data_ram[-1],
        data_network_sent[-1],
        data_network_received[-1],
    )

    ax1.clear()
    ax1.plot(data_cpu, label='Utilisation CPU (%)')
    ax1.set_title("Utilisation CPU (%)")
    ax1.legend()

    ax2.clear()
    ax2.plot(data_ram, label='Utilisation RAM (%)')
    ax2.set_title("Utilisation RAM (%)")
    ax2.legend()

    

    ax4.clear()
    ax4.plot(data_network_sent, label='Données envoyées (Mo)')
    ax4.set_title("Données envoyées (Mo)")
    ax4.legend()

    ax5.clear()
    ax5.plot(data_network_received, label='Données reçues (Mo)')
    ax5.set_title("Données reçues (Mo)")
    ax5.legend()


#fonction pour verif cpu,ram...
def surveiller_ressources():
    utilisation_cpu = psutil.cpu_percent()
    data_cpu.append(utilisation_cpu)

    # Obtenir l'utilisation de la RAM en pourcentage
    utilisation_ram = psutil.virtual_memory().percent
    data_ram.append(utilisation_ram)


    # Obtenir la vitesse du réseau (envoyé et reçu)
    stats_reseau = psutil.net_io_counters()
    envoye = stats_reseau.bytes_sent / (1024 * 1024)
    recu = stats_reseau.bytes_recv / (1024 * 1024)
    data_network_sent.append(envoye)
    data_network_received.append(recu)

# Fonction pour envoyer un e-mail
def send_email(subject, body):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, password)
        message = f"Subject: {subject}\n\n{body}"
        message = message.encode('utf-8') # Encodage UTF-8
        smtp.sendmail(sender_email, receiver_email, message)

# Fonction pour vérifier les connexions SSH
def check_ssh(ip, port=22, timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def network_monitor():
    # Surveillance des connexions réseau
    while True:
        # Envoi d'une requête ARP pour détecter les adresses IP disponibles
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=SUBNET), timeout=2, verbose=0)
        surveiller_ressources()
        # Traitement des réponses
        for pkt in ans:
            ip = pkt[1].psrc
            if ip not in already_detected:
                already_detected.add(ip)
                # Vérification de la connexion SSH
                ssh_connection = check_ssh(ip)

                # Envoi d'un e-mail pour signaler une nouvelle adresse IP
                send_email('Nouvelle adresse IP détectée', f"L'adresse IP {ip} a été détectée sur le réseau. Connexion SSH: {ssh_connection}")

                
        time.sleep(10)

def caca ():
    # Temps d'attente entre deux mesures de débit (en secondes)
    interval = 5

    # Récupère les connexions réseau actives
    connections = psutil.net_connections()

    # Itère sur les connexions et extrait les processus qui utilisent Internet
    internet_processes = {}
    for conn in connections:
        if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
            process = psutil.Process(conn.pid)
            if process.name() != "System":
                internet_processes[process.name()] = {"upload": 0, "download": 0}

    # Mesure le débit de chaque processus toutes les `interval` secondes    
    while True:
        os.system('clear')
        for proc_name in internet_processes:
            process = None
            for p in psutil.process_iter(attrs=['name']):
                if p.info['name'] == proc_name:
                    process = p
                    break

            if process is not None:
                net_io_counters = psutil.net_io_counters(pernic=False, nowrap=True)
                upload_bytes = net_io_counters.bytes_sent - internet_processes[proc_name]["upload"]
                download_bytes = net_io_counters.bytes_recv - internet_processes[proc_name]["download"]
                internet_processes[proc_name]["upload"] = net_io_counters.bytes_sent
                internet_processes[proc_name]["download"] = net_io_counters.bytes_recv

                upload_speed = upload_bytes / interval
                download_speed = download_bytes / interval
                collection2.insert_one({"process name": proc_name, "Upload": upload_speed, "Download": download_speed})
                print(f"{proc_name}: upload={upload_speed:.2f} B/s, download={download_speed:.2f} B/s")
    
        time.sleep(interval)

def signal_handler(sig, frame):
    print('Arrêt du script Python')
    sys.exit(0)


# Fonction principale pour exécuter les deux threads en parallèle
def main():
    network_monitor_thread = threading.Thread(target=network_monitor)
    network_monitor_thread.start()

    caca_thread = threading.Thread(target=caca)
    caca_thread.start()
    signal.signal(signal.SIGINT, signal_handler)

    ani1 = animation.FuncAnimation(fig, update_graph, interval=1000)  # Mise à jour du graphique toutes les 1000 ms
    plt.show()

if __name__ == "__main__":
    main()