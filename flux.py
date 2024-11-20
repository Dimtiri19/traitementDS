import cv2
import time

# Initialisation de la caméra
camera = cv2.VideoCapture(0)

# Vérification que la caméra est bien connectée
if not camera.isOpened():
    print("Impossible d'accéder à la caméra")
    exit()

# Compteur pour les noms de fichiers
counter = 0

def read_signal():
    """Lit le fichier 'inout.txt' pour vérifier le signal (1 ou 0)."""
    try:
        with open('inout.txt', 'r') as file:
            signal = file.read().strip()
            return int(signal)
    except (FileNotFoundError, ValueError):
        # Si le fichier n'existe pas ou contient une erreur, on renvoie 0 par défaut
        return 0

try:
    while True:
        # Lire le signal depuis le fichier
        signal = read_signal()

        if signal == 1:
            # Si signal == 1, capture d'une image
            ret, frame = camera.read()

            if not ret:
                print("Erreur lors de la capture de l'image")
                break

            # Nom du fichier basé sur le compteur
            filename = f'image_{counter}.jpg'

            # Enregistrement de l'image capturée
            cv2.imwrite(filename, frame)
            print(f"Image enregistrée sous {filename}")

            # Incrémentation du compteur
            counter += 1

            # Attendre 5 secondes avant la prochaine capture
            time.sleep(5)
        else:
            # Si signal == 0, attendre 1 seconde avant de vérifier à nouveau
            print("En attente d'un signal...")
            time.sleep(1)

finally:
    # Libération de la caméra
    camera.release()
    cv2.destroyAllWindows()
