# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://docs.python.org/3/

import argparse
import csv
from decimal import Decimal
from datetime import datetime
import env


def get_date(record):
    return datetime.strptime(record[0], "%Y-%m-%d")


IDIR = env.DIR + "TopCard/"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="csv IFILE from Topcard (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + FILE
print("Nom du fichier en entrée:", IFILE)

try:
    with open(IFILE, 'r', newline='', encoding='latin1') as IFILE:
        next(IFILE)  # supprime la première ligne ('sep=;',)
        reader = csv.DictReader(IFILE, delimiter=';')
        transactions = []   # résultat à écrire sur fichier
        Source = 'Topcard'
        Solde = ''  # le solde sera calculé après le tri des transactions
        for row in reader:
            # pprint(row)
            date = row["Ecriture"]
            if date is None:
                date = row["Date d'achat"]
            Date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
            Categorie = 'todo'
            Destinataire: str = row['Texte comptable'][:25].rstrip(' ')
            Destinataire = Destinataire.replace('CHE', '')
            Titre = row['Secteur']
            Usage = row['Titulaire du compte / de la carte']
            r = row['Débit']
            if r and r != ' ':  # r est soit vide ou égal à un espace
                value = '-' + r  # mettre le signe moins pour nombre négatif
            r = row['Crédit']
            if r and r != ' ':
                value = r
            if value:
                Montant = '{:.2f}'.format(Decimal(value))  # 2 chiffres après la virgule
            if Destinataire == 'Report de solde':
                Titre = 'Transfert, report de solde'
                Destinataire = 'TOPCARD SERVICE AG'
                Usage = 'Report de solde ' + Montant
                Solde = Montant  # le solde est calculé dans la prochaine boucle
                solde = Solde
                Montant = '0'
                Categorie = ''
            if Usage == 'GEORG MARFURT':
                Usage = 'Carte Yogi ' + row["Date d'achat"]
            if Usage == 'MARIE MARFURT':
                Usage = 'Carte Marie ' + row["Date d'achat"]

            Titre, Categorie = env.set_titre_categorie(Destinataire, Montant)

            transaction = [Date, Source, Titre, Destinataire, Usage, Montant, Solde, Categorie]
            transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)

#  trier les transactions par date et calculer le solde pas transaction et formatte décimale avec virgule
transactions.sort(key=get_date, reverse=False)
Solde = solde  # c'est le solde extrait de la boucle du reader
for transaction in transactions:
    if transaction[5] != '':  # Montant existe
        Solde = Decimal(Solde) + Decimal(transaction[5])
        transaction[6] = str(Solde).replace(".", ",")
        transaction[5] = transaction[5].replace(".", ",")

#  écrire les transactions normalisées sur fichier
OFILE = env.ODIR + FILE.replace('Topcard ', 'TC_').replace('.csv', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
