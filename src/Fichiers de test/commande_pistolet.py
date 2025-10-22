import pyfirmata
import time

# Définir le port série correspondant à ton Arduino
port = 'COM7'  # à adapter selon ton système
board = pyfirmata.ArduinoMega(port)

# Initialiser la broche PWM D4 (broche digitale 4, en sortie)
pwm_pin = board.get_pin('d:4:p')  # 'p' = PWM (0.0 à 1.0)

# Attendre que la communication s’établisse
time.sleep(2)

# Calcul du rapport cyclique pour obtenir 2V moyen (2V / 5V = 0.4)
duty_cycle = 5 / 5  # soit 0.4 ou 40%

print(f"Écriture d'un signal PWM de {duty_cycle * 100:.0f}% duty cycle (~2V moyen)")

# Appliquer le signal PWM
print("5V")
pwm_pin.write(duty_cycle)

# Maintenir la sortie pendant un moment pour test
time.sleep(2)

# Appliquer le signal PWM
print("0V")
pwm_pin.write(0)
time.sleep(10)

# Appliquer le signal PWM
print("5V")
pwm_pin.write(duty_cycle)

# Maintenir la sortie pendant un moment pour test
time.sleep(2)

# Appliquer le signal PWM
print("0V")
pwm_pin.write(0)
time.sleep(2)

# Nettoyer et fermer
board.exit()
print("Terminé.")
