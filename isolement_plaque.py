import cv2
import numpy as np
import os
import easyocr

# Charger l'image
image_path = "image/voiture 2.jpg"  # Nom de l'image téléchargée
if not os.path.exists(image_path):
    print(f"L'image {image_path} n'existe pas.")
    exit()

image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Appliquer un flou pour réduire le bruit
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Détecter les contours avec Canny
edges = cv2.Canny(blurred, 50, 150)

# Trouver les contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Créer une copie de l'image originale pour dessiner tous les contours
all_contours_image = image.copy()
cv2.drawContours(all_contours_image, contours, -1, (255, 0, 0), 2)  # Contours en bleu

# Parcourir les contours pour trouver des zones potentielles de plaques
potential_plates = []
plate_images = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    
    # Vérifier les dimensions de la zone (à modifier en fonction de l'angle et de la distance de la caméra)
    if w >= 200 and w <= 500 and h >= 40 and h <= 80 :  

        plate_region = image[y:y+h, x:x+w]
        
        # Convertir en espace HSV pour détecter les pixels rouges
        hsv_plate = cv2.cvtColor(plate_region, cv2.COLOR_BGR2HSV)
        

        lower_red1 = np.array([0, 100, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([100, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        

        mask_red1 = cv2.inRange(hsv_plate, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv_plate, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        
        # Compter les pixels rouges
        red_pixel_count = cv2.countNonZero(mask_red)
        print(f"red:{red_pixel_count}")
        
        # Vérifier si la zone contient au moins X pixels rouges (à modifier en fonction de la distance)
        if 1000 >= red_pixel_count >= 100:
            potential_plates.append((x, y, w, h))
            plate_images.append(plate_region)

# Dessiner les plaques potentielles sur une copie de l'image
potential_plates_image = image.copy()
for (x, y, w, h) in potential_plates:
    cv2.rectangle(potential_plates_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

selected_plate_image = None
sharpened_gray = None

if potential_plates:
    # Trouver la plaque la plus en bas (plus grande valeur de y)
    lowest_plate = None
    max_y = -1

    for (x, y, w, h) in potential_plates:
        if y > max_y:
            max_y = y
            lowest_plate = (x, y, w, h)

    # Sélectionner la plaque la plus en bas
    if lowest_plate:
        selected_plate_image = image[lowest_plate[1]:lowest_plate[1]+lowest_plate[3], lowest_plate[0]:lowest_plate[0]+lowest_plate[2]]

        # Appliquer un filtre en niveaux de gris
        gray_plate_image = cv2.cvtColor(selected_plate_image, cv2.COLOR_BGR2GRAY)

        # Appliquer un filtre de netteté (unsharp mask)
        blurred_gray = cv2.GaussianBlur(gray_plate_image, (5, 5), 0)
        sharpened_gray = cv2.addWeighted(gray_plate_image, 2, blurred_gray, -1, 0)

        # Sauvegarder l'image en niveaux de gris améliorée
        cv2.imwrite("imClean.png", sharpened_gray)
        print("L'image sélectionnée et améliorée a été enregistrée sous 'imClean.png'.")
    else:
        print("Aucune plaque trouvée en bas.")

# Lecteur OCR
reader = easyocr.Reader(['fr', 'en'])

# Lire l'image pour extraire le texte
resultats = reader.readtext('imClean.png')

texte_complet = ""

# Caractères indésirables
caracteres_a_supprimer = ["-", ".", " ", "!", "[", "]", "&", "*", "(", ")" , "$", "\'", "|", ","]

for resultat in resultats:
    boite, texte, confiance = resultat
    for char in caracteres_a_supprimer:
        texte = texte.replace(char, "")
    texte_complet += texte

# Rajout manuel de tiret dû au fait qu'ils sont mal détectés
texte_complet_modifie = ""
lettres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Liste des lettres

i = 0
ajouter_tiret_complet = texte_complet[0] in ['1', '2']  # Vérifier si le premier caractère est "1" ou "2"

while i < len(texte_complet):
    # Chercher un groupe de 3 lettres consécutives
    if i + 2 < len(texte_complet) and all(c in lettres for c in texte_complet[i:i+3]):
        if ajouter_tiret_complet:
            texte_complet_modifie += "-" + texte_complet[i:i+3] + "-"  # Ajouter des tirets avant et après les lettres
        else:
            texte_complet_modifie += texte_complet[i:i+3] + "-"  # Ajouter un tiret seulement après les lettres
        i += 3  # Avancer de 3 caractères
    else:
        texte_complet_modifie += texte_complet[i]  # Ajouter le caractère tel quel
        i += 1  # Avancer d'un caractère

# Afficher tout le texte extrait avec les tirets ajoutés
print("Texte détecté : ", texte_complet_modifie)
