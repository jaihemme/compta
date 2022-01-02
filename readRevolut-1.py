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

PaidOutHeader = 'Paid Out (CHF)'
PaidInHeader = 'Paid In (CHF)'
BalanceHeader = ' Balance (CHF)'  # l'en-tête contient un espace au début
if 'EUR' in FILE:
    PaidOutHeader = PaidOutHeader.replace('CHF', 'EUR')
    PaidInHeader = PaidInHeader.replace('CHF', 'EUR')
    BalanceHeader = BalanceHeader.replace('CHF', 'EUR')

try:
    with open(IFILE, 'r', newline='', encoding='utf8') as IFILE:
        reader = csv.DictReader(IFILE, delimiter=';')
        transactions = []   # résultat à écrire sur fichier
        Solde = ''  # le solde sera calculé après le tri des transactions
        locale.setlocale(locale.LC_ALL, 'fr_CH.UTF-8')
        for row in reader:
            # pprint(row)
            date = row['Completed Date']
            Date = env.correct_date(date)
            Categorie = 'todo'
            Source = 'Revolut'
            Texte = row['Reference']
            ExRate = row['Exchange Rate'].replace(u"\u00A0", " ")
            if ExRate != ' ':
                Texte = Texte + ', ' + ExRate
            Texte2 = row['Category']
            if row[PaidOutHeader].strip() != '':
                Montant = '-' + row[PaidOutHeader].strip()
            if row[PaidInHeader].strip() != '':
                Montant = '+' + row[PaidInHeader].strip()
            Solde = row[BalanceHeader].strip()
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

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
