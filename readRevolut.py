# https://stackoverflow.com/questions/24662571/python-import-csv-to-list
# https://python.doctor/page-apprendre-listes-list-tableaux-tableaux-liste-array-python-cours-debutant
# https://docs.python.org/3/

import argparse
import csv
import locale
import env


IDIR = env.DIR + "Revolut/"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="csv IFILE from Revolut (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + FILE
print("Nom du fichier en entrée:", IFILE)

try:
    with open(IFILE, 'r', newline='', encoding='utf8') as IFILE:
        reader = csv.DictReader(IFILE, delimiter=',')
        transactions = []   # résultat à écrire sur fichier
        locale.setlocale(locale.LC_ALL, 'fr_CH.UTF-8')
        # Type,Product,Started Date,Completed Date,Description,Amount,Fee,Currency,State,Balance
        # les heures dans date sont locale GB
        # trié par date mais pas forcéement par heure!
        # balance(=solde) repris tel quel, peut sembler faux si on trie
        for row in reader:
            date = row['Started Date']
            Date = date[:19] + ' +0100'
            Source = 'Revolut'
            Texte = row['Description']
            Texte2 = row['Type']
            Montant = row['Amount'].replace('.', ',')
            Currency = row['Currency']
            Solde = row['Balance'].replace('.', ',')
            Categorie = env.set_categorie(Texte)

            transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
            transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)


#  écrire les transactions normalisées sur fichier
OFILE = env.ODIR + FILE.replace('account-statement_', Source + '-' + Currency + '-').replace('.csv', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
