# https://docs.python.org/3/
# reporte les modifications (transations-norm.modifié.csv) dans transaction.csv

import argparse
import csv
from datetime import datetime


def get_date(record):
    return datetime.strptime(record[0], "%Y-%m-%d")


IDIR = "/Users/yogi/Library/Mobile Documents/iCloud~com~ttdeveloped~moneystatistics/Documents/_backups"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="transaction file from exploded backup Moneystats (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + "/" + FILE
print("Nom du fichier en entrée:", IFILE)

MFILE = IFILE.replace('transactions.csv', 'transactions-norm.modifié.csv')
print("Nom du fichier des comptes:", MFILE)

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
            # clé: compte texte, valeur: compte num.
            comptes[row[1]] = row[0]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + AFILE + "'")
    exit(1)

try:
    with open(GFILE, 'r', newline='', encoding='utf8') as GFILE:
        reader = csv.reader(GFILE, delimiter=';')
        groups = {}  # liste des catégories
        for row in reader:
            groups[row[1]] = row[0]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + GFILE + "'")
    exit(1)

try:
    with open(TFILE, 'r', newline='', encoding='utf8') as TFILE:
        reader = csv.reader(TFILE, delimiter=';')
        tags = {}  # liste des hashtags
        for row in reader:
            tags[row[1]] = row[0]

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + TFILE + "'")
    exit(1)

try:
    with open(MFILE, 'r', newline='', encoding='utf8') as MFILE:
        reader = csv.reader(MFILE, delimiter=';')
        next(MFILE)  # saute ligne en-têtes
        modifs = {}  # liste des transactions modifiées
        for row in reader:
            # clé: source + date
            date = row[0].replace(' 0:', ' 00:').replace(' 1:', ' 01:')
            if date < '2021-03-30 00:00:00':
                date = date + ' +0100'
            else:
                date = date + ' +0200'
            source = comptes[row[1]]
            cat = groups.get(row[7], '0')  # prend le code de la catégorie
            tag = ''
            t1 = row[6].find(' - ')
            if t1 > 1:
                t2 = row[6][t1 + 3:]
                tag = tags[t2] + '?A!'
            modifs[source + date] = row[2] + ';' + row[3] + ';' + cat + ';' + tag

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + AFILE + "'")
    exit(1)

try:
    with open(IFILE, 'r', newline='', encoding='utf8') as IFILE:
        reader = csv.reader(IFILE, delimiter=';')
        transactions = []   # résultat à écrire sur fichier
        Solde = ''  # le solde sera calculé après le tri des transactions
        for row in reader:
            mod = modifs[row[0] + row[1]].split(';')
            if row[5] != mod[0]:  # Texte
                print(row[1], row[0], '1', row[5], '>', mod[0])
                row[5] = mod[0]
            if row[7] != mod[1]:  # Texte2
                print(row[1], row[0], '2', row[7], '>', mod[1])
                row[7] = mod[1]
            if row[8] != mod[2]:  # Catégorie
                print(row[1], row[0], '3', row[8], '>', mod[2])
                row[8] = mod[2]
            if row[11] != mod[3]:  # Tag
                print(row[1], row[0], '4', row[11], '>', mod[3])
                row[11] = mod[3]

            transactions.append(row)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)

#  écrire les transactions normalisées sur fichier
OFILE = IDIR + "/" + FILE.replace('.csv', '.modifié.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerows(transactions)

print("Fichier de sortie modifié:", OFILE)
print("Nombre de transactions:", len(transactions))
