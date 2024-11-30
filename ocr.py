import easyocr

# Créer un lecteur OCR
reader = easyocr.Reader(['fr', 'en'])

# Lire l'image pour extraire le texte
resultats = reader.readtext('imClean.png')

# Initialiser une variable pour stocker le texte complet
texte_complet = ""

# Vérifier et ignorer le premier résultat si c'est un "B" seul
if resultats and resultats[0][1] == "B":
    resultats = resultats[1:]  # Ignorer le premier élément

# Ajouter chaque texte extrait à la variable texte_complet
for resultat in resultats:
    boite, texte, confiance = resultat
    texte = texte.replace("-", "")  # Supprimer les tirets
    texte = texte.replace(".", "") # Supprimer les points
    texte = texte.replace(" ", "") # Supprimer les espaces
    texte_complet += texte  # Ajouter sans espaces intermédiaires

# Ajouter un tiret avant et après chaque groupe de 3 lettres dans texte_complet
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
