import sys
import nmap
import requests
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient

if len(sys.argv) != 3:
    print("Usage: python3 script.py <start_port> <end_port>")
    sys.exit(1)

# Paramètres de la cible
target_host = "localhost"
start_port = sys.argv[1]
end_port = sys.argv[2]
target_ports = f"{start_port}-{end_port}"

# Connexion à MongoDB
client = MongoClient("mongodb://217.182.168.137:2717/")
db = client["monitoring"]
collection = db["service_faille"]

# Créer un nouvel objet de scan Nmap
nm = nmap.PortScanner()

# Scanner la cible pour les ports ouverts et leurs versions
nm.scan(target_host, target_ports, arguments="-sV")

# Liste pour stocker les vulnérabilités
vulnerabilities_list = []

# Itérer sur chaque port ouvert et vérifier les vulnérabilités connues
for host in nm.all_hosts():
    for port in nm[host]['tcp']:
        port_state = nm[host]['tcp'][port]['state']
        if port_state == 'open':
            service_name = nm[host]['tcp'][port]['name']
            service_version = nm[host]['tcp'][port]['version']
            print(f"Le service '{service_name}' sur le port {port} est ouvert et fonctionne avec la version {service_version}")

            # Rechercher les vulnérabilités connues pour la version du service
            cve_list = []
            search_url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=%7Bservice_name%7D+%7Bservice_version%7D"
            search_page = requests.get(search_url)
            search_soup = BeautifulSoup(search_page.content, 'html.parser')
            for cve_id in search_soup.find_all('a', href=True):
                if 'CVE-' in cve_id.text:
                    cve_list.append(cve_id.text)
            if cve_list:
                total_cve = len(cve_list)
                print(f"  - Total des vulnérabilités trouvées: {total_cve}")

                # Ajouter les vulnérabilités à la liste des résultats
                for cve in cve_list:
                    vulnerabilities_list.append({"service_name": service_name, "service_version": service_version, "cve": cve})
            else:
                print(f"  - Aucune vulnérabilité connue trouvée pour {service_name} {service_version}")


# Insérer la liste des vulnérabilités dans la base de données MongoDB
if vulnerabilities_list:
    collection.insert_many(vulnerabilities_list)
    print("Les vulnérabilités ont été ajoutées à la base de données MongoDB.")
else:
    print("Aucune vulnérabilité n'a été trouvée.")