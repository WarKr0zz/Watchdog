
import pymongo #python3 -m pip install pymongo
import subprocess
import nmap
import requests
import paramiko
from bs4 import BeautifulSoup



#Fonction compare auth.log avec un tampon.txt puis envoie les data sur logextract.txt PUIS mets à jour le tmapon.txt avec le auth.log
def compare_files(file1, file2, differences):
    with open(file1) as f1, open(file2) as f2, open(differences, "w") as diff:
        lines1 = set(f1.readlines())
        lines2 = set(f2.readlines())
        new_lines = sorted(lines1.difference(lines2))
        diff.writelines(new_lines)

        with open(file2, "w") as f2:
            f2.writelines(lines1)

#Fonction tri sur le logextract.txt
def filtering(file1, file2, texttofind):
    with open(file1) as f1, open(file2, "w") as f2:
        for line in f1:
            if texttofind in line:
                f2.write(line)
#Fonction Tri spécialement pour avoir les lignes contenant des IP et ecriture dans ipwtach.txt
def filteringIP(file1, file2, texttofind2):
    with open(file1) as f1, open(file2, "w") as f2:
        for line in f1:
            if texttofind2 in line and "." in line:
                f2.write(line)

#Fonction envoie BDD MongoDB pour accept/failroot/ipwatch.txt
def send_to_mongoAF(file_path, db_name, collection_name):
    client = pymongo.MongoClient("mongodb://217.182.168.137:2717/")
    db = client[db_name]
    collection = db[collection_name]

    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            if "192.168.1.16" in line or "192.168.1.35" in line :#or 
                collection.insert_one({"log_entry": line.strip(), "priority": "1"})
            elif "192.168.1.19" in line:
                collection.insert_one({"log_entry": line.strip(), "priority": "6"})

#Fonction pour envoie logextract.txt dans col general sans tri de priority
def send_to_mongo(file_path, db_name, collection_name):
    client = pymongo.MongoClient("mongodb://217.182.168.137:2717/")
    db = client[db_name]
    collection = db[collection_name]

    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            collection.insert_one({"log_entry": line.strip(), "priority": "3"})
            
#---Execute la commande dockers logs 'id' et ecrit la sortie dans output_file
def save_docker_logs(container_id, output_file):
    output = subprocess.check_output(['docker', 'logs', container_id])

    with open(output_file, 'w') as f:
        f.write(output.decode('utf-8'))

def filteringbdd(file1, file2, texttofind, texttofind2):
    with open(file1) as f1, open(file2, "w") as f2:
        for line in f1:
            if texttofind in line or texttofind2 in line:
                f2.write(line)

def filteringmiss (file1, file2, texttofind):
    with open(file1) as f1, open(file2, "w") as f2:
        for line in f1:
            if texttofind not in line:
                f2.write(line)


#Compare auth.log et tampon.txt puis envoie les différence sur logextract.txt PUIS mets à jour le tampon.txt en se basant sur le auth.log
compare_files("/var/log/auth.log", "./tampon.txt", "./logextract.txt")

#Travail de filtre en local sur le ./logetract.txt téléchargé sur le docker victim
filtering("./logextract.txt", "./failroot.txt", "Failed")
filtering("./logextract.txt", "./accept.txt", "Accepted password")
filteringIP("./logextract.txt", "./ipwatch.txt", "from")

#Appelle fonction Envoie MongoDB
send_to_mongo("./logextract.txt", "log", "general")
#Meme fonction mais trie les IP
send_to_mongoAF("./accept.txt", "log", "accepted")
send_to_mongoAF("./failroot.txt", "log", "failed")
#Envoie ipwatch.txt avec tri de priorité dans la bdd dans la col ipwatch
send_to_mongoAF("./ipwatch.txt", "log", "ipwatch")




