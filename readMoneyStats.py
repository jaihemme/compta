# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://docs.python.org/3/

import argparse
import csv
from decimal import Decimal
from datetime import datetime
import env


def get_date(record):
    return datetime.strptime(record[0], "%Y-%m-%d")


IDIR = "/Users/yogi/Library/Mobile Documents/iCloud~com~ttdeveloped~moneystatistics/Documents/_backups"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="exploded backup file from Moneystats (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + "/" + FILE
print("Nom du fichier en entrée:", IFILE)

AFILE = IFILE.replace('transactions.csv', 'accounts.csv')
print("Nom du fichier des comptes:", AFILE)

GFILE = IFILE.replace('transactions.csv', 'groups.csv')
print("Nom du fichier des catégories:", GFILE)

TFILE = IFILE.replace('transactions.csv', 'tags.csv')
print("Nom du fichier des hashtags:", TFILE)

try:
    with open(AFILE, 'r', newline='', encoding='utf8') as AFILE:
        reader = csv.reader(AFILE, delimiter=';')
        comptes = {}  # liste des comptes
        for row in reader:
            comptes[row[0]] = row[1]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + AFILE + "'")
    exit(1)

try:
    with open(GFILE, 'r', newline='', encoding='utf8') as GFILE:
        reader = csv.reader(GFILE, delimiter=';')
        groups = {}  # liste des catégories
        for row in reader:
            groups[row[0]] = row[1]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + GFILE + "'")
    exit(1)

try:
    with open(TFILE, 'r', newline='', encoding='utf8') as TFILE:
        reader = csv.reader(TFILE, delimiter=';')
        tags = {}  # liste des hashtags
        for row in reader:
            tags[row[0]] = row[1]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + TFILE + "'")
    exit(1)

try:
    with open(IFILE, 'r', newline='', encoding='utf8') as IFILE:
        reader = csv.reader(IFILE, delimiter=';')
        transactions = []   # résultat à écrire sur fichier
        Solde = ''  # le solde sera calculé après le tri des transactions
        for row in reader:
            Date = row[1][:19]
            Source = comptes[row[0]]
            Texte = row[5]
            Texte2 = row[7]
            Montant = row[2].replace('.', ',')
            Solde = row[3].replace('.', ',')
            Categorie = ''
            if row[8] and row[8] != "0":
                Categorie = groups[row[8]]
            t = row[11]
            t = t[:t.find('?')]  # ne prend que le premier tag, il peut en avoir plusieurs
            if t:
                Categorie = Categorie + " - " + tags.get(t, '')

            transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
            transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)

#  écrire les transactions normalisées sur fichier
OFILE = IDIR + "/" + FILE.replace('.csv', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
