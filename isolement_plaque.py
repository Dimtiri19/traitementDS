import cv2
import numpy as np
import os

# Charger l'image
image_path = "v4.jpg"  # Nom de l'image téléchargée
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

# Parcourir les contours pour trouver des zones potentielles de plaques
potential_plates = []
plate_images = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / h
    if 2 < aspect_ratio < 5 and w > 100 and h > 30:  # Critères de dimension
        potential_plates.append((x, y, w, h))
        plate_images.append(image[y:y+h, x:x+w])

# Filtrage basé sur la couleur rouge
def filter_red_color(region):
    """Filtre les pixels rouges dans une région donnée."""
    hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

    # Plage de teintes pour le rouge (en HSV, le rouge est dans la plage 0-10 et 170-180)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([150, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Appliquer un masque pour les deux plages de rouge
    mask1 = cv2.inRange(hsv_region, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_region, lower_red2, upper_red2)
    
    # Combiner les masques pour obtenir la zone rouge totale
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    return red_mask

selected_plate_image = None
sharpened_gray = None
filtered_plates_image = image.copy()  # Image pour dessiner les zones restantes
filtered_plates = []  # Zones qui respectent la couleur rouge

if potential_plates:
    max_red_index = -1
    max_red_value = 0
    for i, plate in enumerate(plate_images):
        red_mask = filter_red_color(plate)
        
        # Calculer l'intensité du rouge (zone rouge)
        red_intensity = np.sum(red_mask)  # Somme des pixels rouges
        
        # Si la zone contient suffisamment de rouge, on la garde
        if red_intensity > 5000:  # Seuil d'intensité du rouge à ajuster
            filtered_plates.append(potential_plates[i])
            # Vérifier si c'est la meilleure zone jusqu'à présent
            if red_intensity > max_red_value:
                max_red_value = red_intensity
                max_red_index = i

    # Si plusieurs zones sont détectées, choisir celle qui est la plus centrale
    if len(filtered_plates) > 1:
        # Calculer le centre de l'image
        image_center_x = image.shape[1] // 2
        image_center_y = image.shape[0] // 2

        min_distance = float('inf')
        central_plate = None

        for (x, y, w, h) in filtered_plates:
            # Calculer le centre de la plaque
            plate_center_x = x + w // 2
            plate_center_y = y + h // 2

            # Calculer la distance euclidienne entre le centre de la plaque et le centre de l'image
            distance = np.sqrt((plate_center_x - image_center_x) ** 2 + (plate_center_y - image_center_y) ** 2)

            # Garder la plaque la plus proche du centre de l'image
            if distance < min_distance:
                min_distance = distance
                central_plate = (x, y, w, h)

        # Sélectionner la plaque centrale
        if central_plate:
            selected_plate_image = image[central_plate[1]:central_plate[1]+central_plate[3], central_plate[0]:central_plate[0]+central_plate[2]]

            # Appliquer un filtre en niveaux de gris
            gray_plate_image = cv2.cvtColor(selected_plate_image, cv2.COLOR_BGR2GRAY)

            # Appliquer un filtre de netteté (unsharp mask)
            blurred_gray = cv2.GaussianBlur(gray_plate_image, (5, 5), 0)
            sharpened_gray = cv2.addWeighted(gray_plate_image, 2, blurred_gray, -1, 0)

            # Sauvegarder l'image en niveaux de gris améliorée
            cv2.imwrite("imClean.png", sharpened_gray)
        else:
            print("Aucune plaque centrale n'a été trouvée.")
    elif len(filtered_plates) == 1:
        # Si une seule plaque reste, la sélectionner directement
        selected_plate_image = image[filtered_plates[0][1]:filtered_plates[0][1]+filtered_plates[0][3], filtered_plates[0][0]:filtered_plates[0][0]+filtered_plates[0][2]]
        
        # Appliquer un filtre en niveaux de gris
        gray_plate_image = cv2.cvtColor(selected_plate_image, cv2.COLOR_BGR2GRAY)

        # Appliquer un filtre de netteté (unsharp mask)
        blurred_gray = cv2.GaussianBlur(gray_plate_image, (5, 5), 0)
        sharpened_gray = cv2.addWeighted(gray_plate_image, 2, blurred_gray, -1, 0)

        # Sauvegarder l'image en niveaux de gris améliorée
        cv2.imwrite("imClean.png", sharpened_gray)
    else:
        print("Aucune plaque détectée après le filtrage de couleur rouge.")
else:
    print("Aucune plaque détectée dans l'image.")
