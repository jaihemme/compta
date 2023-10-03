# https://stackoverflow.com/questions/24662571/python-import-csv-to-list
# https://python.doctor/page-apprendre-listes-list-tableaux-tableaux-liste-array-python-cours-debutant
# https://docs.python.org/3/

import argparse
import csv
import locale
import datetime
import pytz

import env


IDIR = env.DIR + "Revolut/"
# print(IDIR)

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
        # Définir les fuseaux horaires GMT et CET/CEST
        gmt = pytz.timezone('GMT')
        cet = pytz.timezone('CET')
        # Type,Product,Started Date,Completed Date,Description,Amount,Fee,Currency,State,Balance
        # les heures dans date sont locale GB
        # trié par date mais pas forcéement par heure!
        # balance(=solde) repris tel quel, peut sembler faux si on trie
        for row in reader:
            date_gmt = row['Started Date']
            # Convertir la date en objet datetime
            date_obj = datetime.datetime.strptime(date_gmt, '%Y-%m-%d %H:%M:%S')
            # Convertir la date en heure locale CET/CEST
            Date = gmt.localize(date_obj).astimezone(cet).strftime('%Y-%m-%d %H:%M:%S %z')
            Source = 'Revolut'
            Destinataire = row['Description']
            fee = row['Fee']
            # montant = float(row['Amount'].replace(',', '.')) - float(fee.replace(',', '.'))
            # laisser le montant tel quel, même s'il faut tenir compte des frais  pour le solde
            montant = float(row['Amount'].replace(',', '.'))
            Montant = str(montant).replace('.', ',')
            Currency = row['Currency']
            Solde = row['Balance'].replace('.', ',')
            Titre, Categorie = env.set_titre_categorie(Destinataire, Montant)
            Usage = row['Type']
            if Usage == 'EXCHANGE' and Destinataire == 'Exchanged to EUR':
                Titre = 'Transfert, Revolut, Achat de EUR avec CHF'
                Destinataire = 'Revolut EUR'
                Categorie = 'Transfert'
            if Usage == 'EXCHANGE' and Destinataire == 'Exchanged to CHF':
                Titre = 'Transfert, Revolut, Achat de CHF avrc EUR'
                Destinataire = 'Revolut CHF'
                Categorie = 'Transfert'
            if Usage == 'TOPUP' and Destinataire == 'Payment from Marfurt G. Et Marfurt-noel M.':
                Titre = 'Transfert, Revolut, virement de VZ'
                Categorie = 'Transfert'
            if fee != '0.00':
                Usage += ', frais=' + row['Fee'].replace('.', ',')

            transaction = [Date, Source, Titre, Destinataire, Usage, Montant, Solde, Categorie]
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
