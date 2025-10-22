import serial
import time

# Paramètres à adapter
port = 'COM5'             # Exemple : COM3 (Windows) ou /dev/ttyUSB0 (Linux)
baudrate = 115200         # Vitesse typique pour les imprimantes 3D

# Fichier contenant les instructions G-code
gcode_file = 'test_instructions_gcode.gcode'

try:
    with serial.Serial(port, baudrate, timeout=1) as ser:
        print(f"Connexion à {port} établie")
        #print(ser)

        # Attente pour que l'imprimante soit prête
        time.sleep(2)
        ser.flush()

        # Lecture ligne par ligne du fichier
        with open(gcode_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith(';'):  # Ignore les lignes vides et commentaires
                    command = line + '\n'
                    ser.write(command.encode())
                    print(f">> {command.strip()}")
                    time.sleep(0.5)  # Pause entre les commandes (ajustable)
                    
                    # Lecture de la réponse éventuelle de l'imprimante
                    response = ser.readline().decode().strip()
                    if response:
                        print(f"<< {response}")

except serial.SerialException as e:
    print(f"Erreur de communication série : {e}")
except FileNotFoundError:
    print(f"Fichier {gcode_file} non trouvé")

