import easyocr

# Créer un lecteur OCR
reader = easyocr.Reader(['fr', 'en'])

# Lire l'image pour extraire le texte
resultats = reader.readtext('imClean.png')

# Afficher uniquement le texte extrait
for resultat in resultats:
    boite, texte, confiance = resultat
    print(f"Texte détecté : {texte}")
