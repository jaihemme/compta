# https://stackoverflow.com/questions/24662571/python-import-csv-to-list
# https://python.doctor/page-apprendre-listes-list-tableaux-tableaux-liste-array-python-cours-debutant
# https://docs.python.org/3/

# XML Schema: https://github.com/genkgo/camt/blob/master/assets/camt.052.001.02.xsd

import argparse
import csv
# from pprint import pprint
import env
from xml.etree.ElementTree import parse
from decimal import Decimal
import string

IDIR = env.DIR + "VZ/"
print(IDIR)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="csv IFILE from VZ (path is fixed)")
args = parser.parse_args()
FILE = args.filename
IFILE = IDIR + FILE
print("Nom du fichier en entrée:", IFILE)

transactions = []  # résultat à écrire sur fichier

try:
    # Pass the path of the xml document
    tree = parse(IFILE)

    # get the parent tag
    root = tree.getroot()
    ns = {'': 'urn:iso:std:iso:20022:tech:xsd:camt.052.001.04'}  # global namespace

    for bal in root.findall('.//Bal', ns):
        solde = Decimal(bal.findtext('Amt', None, ns))
        date = bal.findtext('Dt/', None, ns)
        print('Solde du', date, ':', solde)

    # le premier montant est le solde du début de la période
    solde = Decimal(root.findtext('./BkToCstmrAcctRpt/Rpt/Bal/Amt', None, ns))

    for entry in root.findall('.//Ntry', ns):
        date = entry.findtext('ValDt/Dt', None, ns)
        Date = date[8:]+'.'+date[5:7]+'.'+date[0:4]
        # print('Date: ', date, Date)
        Categorie = 'todo'
        Source = 'VZ'
        Texte = ''
        Texte2 = ''
        Montant = 0
        Solde = 0
        for detail in entry.findall('NtryDtls', ns):
            Montant = detail.findtext('TxDtls/Amt', None, ns)
            Texte = detail.findtext('TxDtls/AddtlTxInf', None, ns)
            Texte = ''.join(filter(lambda x: x in string.printable, Texte))  # BUG données mal encodées
            if detail.findtext('TxDtls/CdtDbtInd', None, ns) == 'CRDT':
                Montant = '+' + Montant
            if detail.findtext('TxDtls/CdtDbtInd', None, ns) == 'DBIT':
                Montant = '-' + Montant
            solde = solde + Decimal(Montant)
            Solde = '{:.2f}'.format(solde).replace('.', ',')
            Montant = Montant.replace('.', ',')

            # print('Montant: ', Montant)
            # print('Solde: ', Solde)
            # print('Texte:', Texte)

            Texte2 = ''
            _ = Texte.replace('Dbit e-banking ', '')

            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'e-banking'

            _ = Texte.replace('Dbit LSV+ ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'LSV'

            _ = Texte.replace('Bonification ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'Bonification'

            _ = Texte.replace('Votre ordre de paiement ', '')
            if len(Texte) != len(_):
                Texte = _
                Texte2 = 'Ordre de paiement'

            Categorie = env.set_categorie(Texte)

        transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
        transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas: '" + IFILE + "'")
    exit(1)

#  écrire les transactions normalisées sur fichier
OFILE = env.ODIR + FILE.replace('.xml', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
