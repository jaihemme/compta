# https://stackoverflow.com/questions/24662571/python-import-csv-to-list
# https://python.doctor/page-apprendre-listes-list-tableaux-tableaux-liste-array-python-cours-debutant
# https://docs.python.org/3/
# https://docs.python.org/3.9/library/re.html

import argparse
import csv
# from pprint import pprint
import re
from datetime import datetime
import locale

import env


IDIR = env.DIR + "BCF/"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="csv IFILE from BCF (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + FILE
print("Nom du fichier en entrée:", IFILE)

try:
    with open(IFILE, 'r', newline='', encoding='latin1') as IFILE:
        reader = csv.DictReader(IFILE, delimiter=';')
        for _ in range(11):
            next(IFILE)  # ignore les 11 premières lignes
        transactions = []   # résultat à écrire sur fichier
        Solde = ''  # le solde sera calculé après le tri des transactions
        locale.setlocale(locale.LC_ALL, 'fr_CH.UTF-8')
        for row in reader:
            # pprint(row)
            Date = datetime.strptime(row['Date'], '%d.%m.%y').strftime('%d.%m.%Y')
            Categorie = 'todo'
            Source = 'BCF'
            text = row['Libellé']
            Texte = ''
            Texte2 = ''

            # Texte = re.sub(pattern[0], replace[1], pour chaque élément)
            # Texte2 = re.sub(pattern[2], replace[3], pour chaque élément)
            regex = (
                ['^Débit TWINT (.*) .*$', '\\1',
                 '^Débit (TWINT) .* (.*)$', '\\1 \\2'],
                ['^Crédit TWINT (.*) .*$', '\\1',
                 '^Crédit (TWINT) .* (.*)$', '\\1 \\2'],
                ['^Débit direct Maestro .{5} (.*) Numéro de carte: 70097416$', '\\1',
                 '^Débit direct (Maestro) (.{5}) .*: 70097416$', '\\1 Marie \\2'],
                ['^Débit direct Maestro .{5} (.*) Numéro de carte: 70097499$', '\\1',
                 '^Débit direct (Maestro) (.{5}) .*: 70097499$', '\\1 Yogi \\2'],
                ['Crédit (Caisse de prévoyance du personnel)', '\\1',
                 '(Crédit) Caisse de prévoyance du personnel', '\\1'],
                ['^(Prélèvement bancomat .*), Carte: 70097416$', '\\1',
                 '^Prélèvement bancomat .* Carte: 70097416$', 'Maestro Marie'],
                ['^(Prélèvement bancomat .*), Carte: 70097499$', '\\1',
                 '^Prélèvement bancomat .* Carte: 70097499$', 'Maestro Yogi'],
                ['^Retrait BM .{5} BM (.*) Numéro de carte: 70097416$', 'Retrait bancomat \\1',
                 '^Retrait BM (.{5}) .*', 'Maestro Marie \\1'],
                ['^Retrait BM .{5} BM (.*) Numéro de carte: 70097499$', 'Retrait bancomat \\1',
                 '^Retrait BM (.{5}) .*', 'Maestro Yogi \\1'],
                ['Ordre e-banking (.*)', '\\1', 'Ordre e-banking .*', 'e-banking']
            )

            for exp in regex:
                Texte = re.sub(exp[0], exp[1], text)
                # noinspection PyRedeclaration
                Texte2 = re.sub(exp[2], exp[3], text)
                if Texte != text:
                    break

            Texte2 = re.sub('(Maestro .*) (.*)', '\\1 '+row['Valeur']+' \\2', Texte2)

            Montant = row['Montant'].replace('.', ',')
            Solde = row['Solde'].replace('.', ',')
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
