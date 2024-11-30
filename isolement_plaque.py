import cv2
import numpy as np
import os

# Charger l'image
image_path = "bmw_plaque.jpg"  # Nom de l'image téléchargée
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
    aspect_ratio = w / h
    if 2 < aspect_ratio < 5 and w > 100 and h > 30:  # Critères de dimension
        potential_plates.append((x, y, w, h))
        plate_images.append(image[y:y+h, x:x+w])

# Identifier la zone contenant le plus de rouge
def calculate_red_intensity(region):
    """Calcule l'intensité du rouge dans une région donnée."""
    red_channel = region[:, :, 2]  # Canal rouge
    return np.sum(red_channel)  # Somme des valeurs de rouge

if potential_plates:
    max_red_index = -1
    max_red_value = 0
    for i, plate in enumerate(plate_images):
        red_intensity = calculate_red_intensity(plate)
        if red_intensity > max_red_value:
            max_red_value = red_intensity
            max_red_index = i

    # Afficher la région contenant le plus de rouge
    if max_red_index != -1:
        selected_plate = potential_plates[max_red_index]
        x, y, w, h = selected_plate
        best_plate_image = image[y:y+h, x:x+w]

        # Appliquer un filtre en niveaux de gris
        gray_plate_image = cv2.cvtColor(best_plate_image, cv2.COLOR_BGR2GRAY)

        # Appliquer un filtre de netteté (unsharp mask)
        blurred_gray = cv2.GaussianBlur(gray_plate_image, (5, 5), 0)
        sharpened_gray = cv2.addWeighted(gray_plate_image, 2, blurred_gray, -1, 0)

        # Sauvegarder l'image en niveaux de gris améliorée dans un fichier PNG
        cv2.imwrite("imClean.png", sharpened_gray)
        print("L'image sélectionnée et améliorée a été enregistrée sous 'imClean.png'.")
else:
    print("Aucune plaque potentielle détectée.")
