# https://stackoverflow.com/questions/24662571/python-import-csv-to-list
# https://python.doctor/page-apprendre-listes-list-tableaux-tableaux-liste-array-python-cours-debutant
# https://docs.python.org/3/

import argparse
import csv
# from pprint import pprint
import env


IDIR = env.DIR + "VZ/"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="csv IFILE from VZ (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + FILE
print("Nom du fichier en entrée: " + IFILE)

try:
    with open(IFILE, 'r', newline='', encoding='utf8') as IFILE:
        reader = csv.DictReader(IFILE, delimiter=';')
        transactions = []   # résultat à écrire sur fichier
        Solde = ''  # le solde sera calculé après le tri des transactions
        for row in reader:
            # pprint(row)
            Date = row['Date de valeur']
            Categorie = 'todo'
            Source = 'VZ'
            Texte = row['Texte comptable']
            Texte2 = ''
            _ = Texte.replace('Débit e-banking ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'e-banking'

            _ = Texte.replace('Débit LSV+ ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'LSV'

            _ = Texte.replace('Bonification ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'Bonification'

            Montant = row['Valeur'].replace(".", ",").replace("'", " ") # virgule et séparateur
            Solde = row['Solde'].replace(".", ",").replace("'", " ")
            Categorie = env.set_categorie(Texte)

            transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
            transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)

#  écrire les transactions normalisées sur fichier
OFILE = env.ODIR + FILE.replace('.csv', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé: ", OFILE)
