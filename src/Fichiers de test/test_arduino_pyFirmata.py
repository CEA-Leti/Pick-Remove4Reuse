import pyfirmata # Importer pyFirmata
import time # Importer le temps

port = 'COM7'# Windows
#port = '/dev/ttyACM3' # Linux
#port = '/dev/tty.usbmodem11401'# Mac

HIGH = True# Crée un état haut qui correspond à la led allumée
LOW = False # Crée un état bas qui correspond à la led éteinte
board = pyfirmata.Arduino(port) # Initialise la communication avec la carte
LED_pin = board.get_pin('d:13:o') # Initialise la broche (d => digital, 13 => N° broche, o => output)

for i in range(10): # Permet de faire clignoter la micro-led dix fois
    LED_pin.write(HIGH) # Allume la led
    time.sleep(1) # Pause de 0.5 seconde
    LED_pin.write(LOW) # Eteint la led
    time.sleep(1) # Nouvelle pause de 0.5 seconde

board.exit() # Clôture la communication avec la carte