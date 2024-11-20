import cv2
import numpy as np
import matplotlib.pyplot as plt
import os  # Importer le module os pour la suppression de fichiers

# Charger l'image
image = cv2.imread('bmw_plaque.jpg')

# Convertir en niveaux de gris
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Appliquer un flou gaussien pour réduire le bruit
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# Appliquer une détection de bords pour mieux voir les contours
edged = cv2.Canny(gray, 30, 200)

# Trouver les contours dans l'image
contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Trier les contours par zone pour garder les plus grandes
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
plaque_contour = None

# Boucle pour trouver le contour qui ressemble à un rectangle (la plaque)
for contour in contours:
    # Approximons le contour
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Si le contour a 4 points, il pourrait correspondre à la plaque
    if len(approx) == 4:
        plaque_contour = approx
        break

# Vérifier si la plaque a été détectée
if plaque_contour is not None:
    # Créer un masque de la même taille que l'image originale, initialisé à noir
    mask = np.zeros_like(image)

    # Dessiner le contour de la plaque sur le masque
    cv2.drawContours(mask, [plaque_contour], -1, (255, 255, 255), -1)

    # Appliquer le masque sur l'image originale pour isoler la plaque
    result = cv2.bitwise_and(image, mask)

    # Extraire les coordonnées du rectangle englobant
    x, y, w, h = cv2.boundingRect(plaque_contour)

    # Enregistrer l'image résultante (plaque isolée)
    cv2.imwrite('plaque_isolee.png', result)

    # Créer une image avec fond noir
    black_background = np.zeros_like(image)

    # Garder la plaque sur le fond noir
    black_background[y:y+h, x:x+w] = result[y:y+h, x:x+w]

    # Afficher l'image avec la plaque sur un fond noir
    plt.imshow(cv2.cvtColor(black_background, cv2.COLOR_BGR2RGB))
    plt.title("Plaque isolée avec fond noir")
    plt.axis('off')
    plt.show()

    # Charger l'image isolée à partir du fichier
plaque_isolee = cv2.imread('plaque_isolee.png')

# Redécouper la région de la plaque à partir de l'image isolée
plaque_region = plaque_isolee[y:y+h, x:x+w]

# Convertir la région de la plaque en niveaux de gris
plaque_region_gray = cv2.cvtColor(plaque_region, cv2.COLOR_BGR2GRAY)

# Appliquer un seuillage pour rendre en noir total les pixels en dessous de 200
_, plaque_region_gray = cv2.threshold(plaque_region_gray, 200, 255, cv2.THRESH_BINARY_INV)

# Afficher la région de la plaque découpée à partir de l'image isolée en niveaux de gris
plt.imshow(plaque_region_gray, cmap='gray')
plt.title("Région de la plaque à partir de l'image isolée (Niveaux de gris)")
plt.axis('off')
plt.show()

# Enregistrer l'image finale en tant que imClean.png
cv2.imwrite('imClean.png', plaque_region_gray)

# Supprimer le fichier plaque_isolee.png
os.remove('plaque_isolee.png')
