import serial
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import openpyxl
import pandas as pd
import configparser
import pyfirmata

#L'imprimante stocke les ordres et les exécute au fur et à mesure. Ainsi, afin de synchroniser
#l'envoi d'ordre et leur synchronisation, il est nécessaire d'attendre la fin du mouvement de 
#l'imprimante pour envoyer le prochain ordre.
def attendre_fin_mouvement():
    command='M400 \n'
    ser.write(command.encode())
    print(f">> {command.strip()}")
    while True:
        line = ser.readline().decode().strip()
        print(f">> {line}")
        if "ok" in line.lower():
            break

#Lorsque nous en sommes à l'étape du désassemblage, en plus d'attendre la fin du mouvement de l'imprimante,
# nous souhaitons également mesurer le temps écoulé entre le début de la descente du pistolet depuis la hauteur de sécu
# et le moment où ce dernier vient au contact avec un EC libérant le capteur de fin de course. Ainsi, le temps est mesuré
# entre l'envoi de la commande de descente du pistolet et le moment où le capteur de fin de course devient libre.
def attendre_fin_mouv_recup_ec():
    command='M400 \n'
    ser.write(command.encode())
    print(f">> {command.strip()}")
    end=0
    try:
        while end==0:
            line = ser.readline().decode().strip()
            print(f">> {line}")
            value = endstop_pin.read()  # Renvoie True, False ou None
            if value is False:
                print("⚪ Capteur LIBRE (non pressé)")
                end=1
                return time.time()
            else:
                print("⚠️ En attente du signal...")
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("Fin du programme.")
        board.exit()

#La fonction "envoi_commande" permet d'envoyer un ordre à l'imprimante, puis d'attendre que cette dernière ait fini son mouvement.
#Dans certain cas il est nécessaire d'attendre deux fois la fin du mouvement pour ne pas perdre la synchronisation 
def envoi_commande(commande,opt):
    command=commande+' \n'
    ser.write(command.encode())
    print(f">> {command.strip()}")
    time.sleep(1)  # Pause entre les commandes (ajustable)
    
    
    # Lecture de la réponse éventuelle de l'imprimante
    while True:
        response = ser.readline().decode().strip()
        if response:
            print(f"<< boucle1 {response}")
        if "ok" in response.lower():
            if "G28" in commande:
                attendre_fin_mouvement()
                time.sleep(0.5)
                break
            elif opt==0:
                return attendre_fin_mouv_recup_ec()
                time.sleep(0.5)
                break
            else:
                attendre_fin_mouvement()
                time.sleep(0.5)
                attendre_fin_mouvement()
                time.sleep(0.5)
                break
            
#Cette fonction permet de retourner la position de l'imprimante. Néanmoins, cette position 
#n'est pas la position réelle, mais plutôt la future position de cette dernière une fois le mouvement accompli.
def pos_actuel():
    command='M114 \n'
    ser.write(command.encode())
    print(f">> {command.strip()}")
    time.sleep(0.5)  # Pause entre les commandes (ajustable)
    while True:
        line = ser.readline().decode().strip()
        print(f">> {line}")
        if "x:" in line.lower():
            coords = [0, 0, 0]
            i=0
            
            # Ne garder que la partie avant "Count"
            part = line.split("E")[0].strip()
            print(part)
            trash, part = part.split('X:')
            coords[0], part = part.split('Y:')
            coords[1], coords[2] = part.split('Z:')
            return coords
            break

# Cette fonction permet de générer une fenêtre pop-up avec le message transmis en entrée.        
def popUp_information(message):
    win = tk.Tk()
    win.title("Information")
    win.attributes('-topmost', True)
    win.geometry("450x150")
    
    tk.Label(win, text=message, pady=10).pack()
    tk.Button(win, text="OK", command=win.destroy).pack()
    
    win.mainloop()

#Cette fonction permet la récupération du fichier Excel permettant la récupération des composants.
# Elle permet la génération d'une fenêtre pop-upp ainsi qu'une fenêtre de sélection du fichier cible
def open_file():
    popUp_information("Veuillez sélectionner le fichier excel organisé comme suis:\n"
                      "Nom composant     Position X     Position Y\n"
                      "R1                         12.5                 24.8\n"
                      "C3                         45.0                 10.2\n"
                      "U1                         30.0                 35.0\n"
                      "(avec la case Nom composant correspondant à la cellule excel A1)")
    file_path = filedialog.askopenfilename(title="Ouvrir un fichier", filetypes=[("Fichiers excel", "*.xlsx")])
    print(file_path)
    try:
        df = pd.read_excel(file_path)

    except FileNotFoundError:
        print(f"Fichier non trouvé : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
    return df, file_path

# Cette fonction permet d'extraire les données du fichier de configuration
def recup_donnee_config():
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        default = config['DEFAULT']
        constante = config['Constante']
        portImprimante=default['portImprimante']
        portArduino=default['portArduino']
        baudrate=default['baudrate']
        pin_finDeCourse=default['pin_finDeCourse']
        pin_buzzer=default['pin_buzzer']
        pin_relaiCycleChauffe=default['pin_relaiCycleChauffe']
        pos_x_min_depose_ec=float(constante['pos_x_min_depose_ec'])
        pos_x_max_depose_ec=float(constante['pos_x_max_depose_ec'])
        espacement_ec_depose_x = float(constante['espacement_ec_depose_x'])
        pos_y_min_depose_ec=float(constante['pos_y_min_depose_ec'])
        pos_y_max_depose_ec=float(constante['pos_y_max_depose_ec'])
        espacement_ec_depose_y = float(constante['espacement_ec_depose_y'])
        vitesse_deplacement=int(constante['Vitesse_deplacement'])
        hauteur_secu_z=int(constante['hauteur_secu_z'])
        delta_z_posDesassemblage=int(constante['delta_z_posDesassemblage'])
    except FileNotFoundError:
        print(f"Fichier non trouvé : {config.ini}")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
    return portImprimante, portArduino,baudrate, pin_finDeCourse, pin_buzzer, pin_relaiCycleChauffe, pos_x_max_depose_ec, pos_x_min_depose_ec, espacement_ec_depose_x, pos_y_max_depose_ec, pos_y_min_depose_ec,espacement_ec_depose_y,vitesse_deplacement,hauteur_secu_z, delta_z_posDesassemblage
        
# Charger le fichier Excel
fichier_excel, file_path= open_file()
print ("Fichier excel récupéré")

# Recupération des conctante issu du fichier de configuration
portImprimante, portArduino,baudrate, pin_finDeCourse, pin_buzzer, pin_relaiCycleChauffe, pos_x_max_depose_ec, pos_x_min_depose_ec, espacement_ec_depose_x, pos_y_max_depose_ec, pos_y_min_depose_ec,espacement_ec_depose_y,vitesse_deplacement,hauteur_secu_z, delta_z_posDesassemblage=recup_donnee_config()

# Initialisation de l'Arduino avec pyFirmata pour communiquer en port série depuis le script Python
board = pyfirmata.ArduinoMega(portImprimante)

# Activation du reporting (lecture en entrée)
it = pyfirmata.util.Iterator(board)
it.start()
# Initialisation du capteur de fin de course connecté sur D7
endstop_pin = board.get_pin(f"d:{pin_finDeCourse}:i") 
# Initialisation du buzzer permettant d'avoir un retour sur l'étape du cycle de la station à air chaud
input_pin = board.get_pin(f"d:{pin_buzzer}:i")  # 'd:2:i' → digital 2 input
# Initialisation de la broche D4 (broche digitale 4, en sortie)
relaiCycleChauffe_pin = board.get_pin(f"d:{pin_relaiCycleChauffe}:o")

#Intialisation de la position actuel de dépose du composant (qui s'incrémente au court de la récupération)
pos_y_ligne_depose_ec=pos_y_min_depose_ec
pos_x_colonne_depose_ec=pos_x_min_depose_ec
try:
    with serial.Serial(portArduino, baudrate, timeout=1) as ser:
        print(f"Connexion à {portArduino} établie")
        #print(ser)

        # Attente pour que l'imprimante soit prête
        time.sleep(2)
        ser.flush()
        
        #On set le mode de positionement absolu
        envoi_commande('G90',1)
        #On set l'unité en mm
        envoi_commande('G21',1)
        #On relève le pistolet à la hauteur de sécurité afin d'éviter des potentiels collision avec la structure de l'imprimante etc...
        envoi_commande('G1 Z'+str(hauteur_secu_z)+' F'+str(vitesse_deplacement),1)
        #On fait le homing des axes X, Y et Z
        envoi_commande('G28',1)
        #On s'éloigne de la hauteur de scéurité selon Z pour éviter de percuter des obstacles
        envoi_commande('G1 Z'+str(hauteur_secu_z)+' F'+str(vitesse_deplacement),1)
        
        # Initialisation de la position de référence du premier composant de la récupération
        envoi_commande('M117 Set position EC 1',1)
        popUp_information("Afin de callibrer l'iprimante, déplacez vous au-dessus du 1er composant à récupérer \n"
                          "Pour vous déplacez, appuyer sur la mollette > prepare > Move axis \n \n"
                          "Appuyer sur ok une fois le dépacement effectué \n")
        posC1_Rsyst=pos_actuel()
        #popUp_information("Le premier composant se situe en position :"+posC1_Rsyst+"si votre positionement ne vous convient pas réajuster puis appuyé sur ok")
        
        posC1_Rcarte=[0, 0]
        # Lecture ligne par ligne du fichier Excel contenant la position des composants à récupérer
        for index, row in fichier_excel.iterrows():
            nom = row.iloc[0]
            if index==0:
                posC1_Rcarte=[row.iloc[1], row.iloc[2]]
                x = posC1_Rsyst[0]
                y = posC1_Rsyst[1]
            else:
                x = float(posC1_Rsyst[0])+float(row.iloc[1])-float(posC1_Rcarte[0])
                y = float(posC1_Rsyst[1])+float(row.iloc[2])-float(posC1_Rcarte[1])
            
            ## Début de la récupération du composant cible
            # Déplacement au dessus du composant à recup
            pos_composant = 'G1 X'+str(x)+' Y'+str(y)+'Z'+str(hauteur_secu_z)+' F'+str(vitesse_deplacement)
            print(pos_composant)
            envoi_commande('M117 Recup composant '+nom,1)
            envoi_commande(pos_composant,1)
            
            #Mise en contact du composant avec la buse aspirante
            start = time.time()
            end=envoi_commande('G1 Z1 F'+str(vitesse_deplacement),0)
            
            #Début du cycle de chauffe (vaccum on) (On envoi un signal au relai permettant le déclenchement du cycle de chauffe)
            print("5V")
            relaiCycleChauffe_pin.write(True)

            # Maintenir la signal le temps de l'activation du cycle
            time.sleep(2)

            # 'Relachement du bouton permettant l'activation du cycle'
            print("0V")
            relaiCycleChauffe_pin.write(False)
            time.sleep(10)
            
            #Calcul du temps écoulé entre la position du pistolet à la hauteur de sécu et 
            #le contact du pistolet avec le composant. Objectif : déduire la hauteur 
            #du composant cible afin d'y retourner pour charger le ressort participant au désassemblage 
            elapsed = end - start
            print(elapsed)
            dist=float(elapsed)*30/6.36
            #Déplacement à la position adéquate afin de charger le ressort. La constante 'delta_z_posDesassemblage' 
            # est modulable en fonction du chargement ciblé pour le ressort et du positionnement du capteur de fin de course.
            envoi_commande('G1 Z'+str(hauteur_secu_z-dist+delta_z_posDesassemblage)+' F'+str(3000),1)
            
            attendre_fin_mouvement()
            
            #Attente pour désassemblage
            # === Détection front montant ===
            previous_state = True  # High

            print("Détection du signal électrique permettant l'activation du buzzer et signalant le changement d'état du cycle de chauffe")
            detection_cycle=0;
            try:
                while detection_cycle < 3:
                    value = input_pin.read()
                    if value is True and previous_state is False:
                        print("Front montant détecté !")
                        detection_cycle=detection_cycle+1
                        time.sleep(5) #attente de la fin du bip
                    previous_state = value
                    time.sleep(0.01)  # Pause légère pour éviter suréchantillonnage
            except KeyboardInterrupt:
                print("Arrêt du programme.")
                board.exit()
            
            #Désassemblage
            envoi_commande('G1 Z'+str(hauteur_secu_z)+' F'+str(vitesse_deplacement),1)
            
            #Dépose du composant selon une position incrémentale en y et fixe en x
            if pos_y_ligne_depose_ec == pos_y_max_depose_ec:
                print("Dernier espace de dépose, prochaine depose au début de la ligne de dépose")
            if pos_y_ligne_depose_ec>pos_y_max_depose_ec:
                pos_y_ligne_depose_ec=pos_y_min_depose_ec
            if pos_x_colonne_depose_ec>pos_x_max_depose_ec:
                pos_x_colonne_depose_ec=pos_x_min_depose_ec
            
            envoi_commande('M117 Depose composant '+nom,1)
            envoi_commande('G1 X'+str(pos_x_colonne_depose_ec)+' Y'+str(pos_y_ligne_depose_ec-10)+' F'+str(vitesse_deplacement),1)
            envoi_commande('G1 Z1 F'+str(vitesse_deplacement),1)
            envoi_commande('G1 X'+str(pos_x_colonne_depose_ec)+' Y'+str(pos_y_ligne_depose_ec)+' F'+str(vitesse_deplacement),1)
            envoi_commande('G1 Z'+str(hauteur_secu_z)+' F'+str(vitesse_deplacement),1)
            attendre_fin_mouvement()
            
            ##Fin du cycle de chauffe
            # Envoi du signal permettant de stopper le cycle de chauffe
            print("5V")
            relaiCycleChauffe_pin.write(True)

            # Maintenir la signal le temps de l'activation du cycle
            time.sleep(2)

            # 'Relachement du bouton permettant l'activation du cycle'
            print("0V")
            relaiCycleChauffe_pin.write(False)
            time.sleep(2)
            
            # Incrément de la position de dépose
            pos_y_ligne_depose_ec=pos_y_ligne_depose_ec+espacement_ec_depose_y
            pos_x_colonne_depose_ec=pos_x_colonne_depose_ec+espacement_ec_depose_x
            
            #Ecriture de la position de dépose du composant dans le fichier Excel contenant les positions des composants sur la carte
            fichier_excel.loc[index, "pos_x_depot"] = pos_x_colonne_depose_ec
            fichier_excel.loc[index, "pos_y_depot"] = pos_y_ligne_depose_ec
        
        envoi_commande('M117 Recuperation terminee !',1)
        fichier_excel.to_excel(file_path, index=False)

except serial.SerialException as e:
    print(f"Erreur de communication série : {e}")