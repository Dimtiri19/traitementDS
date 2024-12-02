import easyocr

# lecteur OCR
reader = easyocr.Reader(['fr', 'en'])

# Lire image pour extraire le texte
resultats = reader.readtext('imClean.png')

texte_complet = ""

#caractère indésirable
caracteres_a_supprimer = ["-", ".", " ", "!", "[", "]", "&", "*", "(", ")" , "$", "\'", "|", ","]

for resultat in resultats:
    boite, texte, confiance = resultat
    for char in caracteres_a_supprimer:
        texte = texte.replace(char, "")
    texte_complet += texte


# rajout manuel de tiret dû au fait qu'ils sont mal détecté
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
