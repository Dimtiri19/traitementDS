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

# Parcourir les contours pour trouver des zones potentielles de plaques
potential_plates = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)

    # Vérifier les dimensions de la zone
    if 200 <= w <= 400 and 50 <= h <= 80:
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
        
        # Vérifier si la zone contient au moins X pixels rouges
        if 2000 <= red_pixel_count <= 8000:
            potential_plates.append((x, y, w, h))

selected_plate_image = None

if potential_plates:
    # Si plusieurs zones sont détectées, choisir celle qui est la plus centrale
    if len(potential_plates) > 1:
        # Calculer le centre de l'image
        image_center_x = image.shape[1] // 2
        image_center_y = image.shape[0] // 2

        min_distance = float('inf')
        central_plate = None

        for (x, y, w, h) in potential_plates: 
            plate_center_x = x + w // 2
            plate_center_y = y + h // 2

            distance = np.sqrt((plate_center_x - image_center_x) ** 2 + (plate_center_y - image_center_y) ** 2)

            if distance < min_distance:
                min_distance = distance
                central_plate = (x, y, w, h)

        # Sélectionner la plaque centrale
        if central_plate:
            selected_plate_image = image[central_plate[1]:central_plate[1]+central_plate[3], central_plate[0]:central_plate[0]+central_plate[2]]
    else:
        # Si une seule plaque reste, la sélectionner directement
        x, y, w, h = potential_plates[0]
        selected_plate_image = image[y:y+h, x:x+w]

    if selected_plate_image is not None:
        # Appliquer un filtre en niveaux de gris
        gray_plate_image = cv2.cvtColor(selected_plate_image, cv2.COLOR_BGR2GRAY)

        # Appliquer un filtre de netteté (unsharp mask)
        blurred_gray = cv2.GaussianBlur(gray_plate_image, (5, 5), 0)
        sharpened_gray = cv2.addWeighted(gray_plate_image, 2, blurred_gray, -1, 0)

        # Sauvegarder l'image en niveaux de gris améliorée
        cv2.imwrite("imClean.png", sharpened_gray)
        print("L'image sélectionnée et améliorée a été enregistrée sous 'imClean.png'.")
else:
    print("Aucune plaque potentielle trouvée.")
