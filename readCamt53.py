# https://docs.python.org/3/

# https://www.sepaforcorporates.com/swift-for-corporates/a-practical-guide-to-the-bank-statement-camt-053-format/
# XML Schema: https://github.com/genkgo/camt/

# utilisé:
# BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/Nm --> banque ('Banque Cantonale de Fribourg' ou 'VZ Depotbank AG')
# BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/BICFI --> bic ('BEFRCH22XXX' ou 'VZDBCHZZXXX')
# BkToCstmrStmt/Stmt/Acct/Id/IBAN  --> IBAN
# BkToCstmrStmt/Stmt/Acct/Ownr/Nm  --> Détenteur
# root.findall('.//Bal', ns):  # 2 soldes, début et fin des transactions du fichier
# . BkToCstmrStmt/Stmt/Bal/Amt --> solde
# . BkToCstmrStmt/Stmt/Bal/Dt --> date
# root.findall('.//Ntry', ns):
# . BookgDt/Dt --> Date (csv)
# . ValDt/Dt --> date
# . Amt --> Montant /csv)
# . CdtDbtInd = 'CRDT' ou 'DBIT' --> signe +/- de Montant
# . AddtlNtryInf --> Texte + Texte2 (csv)
# . NtryDtls/Btch/NbOfTxs --> nombre de transactions batch (none ou 1 et +)
# . if NbOfTxs>1: ntry.findall('NtryDtls/TxDtls', ns):
# . . Amt --> Montant
# . . CdtDbtInd = 'CRDT' ou 'DBIT' --> signe +/- de Montant
# . . RltdPties/Cdtr/Nm --> créancier --> Texte
# . . RmtInf/Ustrd --> commentaire --> Texte
# . . AddtlTxInf --> Texte + créancier + commentaire (csv)

import argparse
import csv
import env
from xml.etree.ElementTree import parse
from decimal import Decimal
import string
import re


def set_montant(element, solde):
    sign = ''
    montant: str = element.findtext('Amt', None, ns)  # montant, p.ex 12.3
    if element.findtext('CdtDbtInd', None, ns) == 'CRDT':
        sign = '+'  # crédit
    if element.findtext('CdtDbtInd', None, ns) == 'DBIT':
        sign = '-'  # débit
    montant = sign + montant  # ajoute le signe comme prefixe
    solde = solde + Decimal(montant)  # augmente le solde
    _solde = solde  # mise à jour de la variable globale

    # formattage, remplace le point décimal par une virgule
    montant = montant.replace('.', ',')
    solde = '{:.2f}'.format(solde).replace('.', ',')

    return [montant, solde, _solde]


def set_texte(element, tag):
    t: str = element.findtext(tag, None, ns)

    # corrige un BUG de données mal encodées
    if SOURCE == 'VZ':
        t = ''.join(filter(lambda x: x in string.printable, t))
        t = re.sub('Dbit', 'Débit', t)
        t = re.sub('Maracher', 'Maraîcher', t)

    # ajoute une précision
    if 'Wingo' in t:
        _ = Montant.split(sep=',')  # retour au point décimal
        if Decimal(_[0]) < -40:
            t = re.sub('Wingo', 'Wingo internet', t)
        else:
            t = re.sub('Wingo', 'Wingo mobile', t)

    # ajoute plus d'infos aux transaction
    if tag == 'AddtlTxInf':
        t = t + ' ' + element.findtext('RltdPties/Cdtr/Nm', None, ns)
        t = t + ', ' + element.findtext('RmtInf/Ustrd', None, ns)

    texte = env.set_texte(t)
    texte2 = env.set_texte2(t)
    texte2 = re.sub('#ValDt#', ValDt, texte2)

    return [texte, texte2]


parser = argparse.ArgumentParser()
parser.add_argument("source", help="nom de la banque (source)")
parser.add_argument("filename", help="nom du fichier camt53 (xml)")
args = parser.parse_args()
SOURCE = args.source
if not (SOURCE == 'BCF' or SOURCE == 'VZ'):
    print("La source doit être 'BCF' ou 'VZ' (", SOURCE, ").")
    exit(1)
print("Source des transactions: ", SOURCE)

FILE = args.filename
IDIR = env.DIR + SOURCE
IFILE = IDIR + "/" + FILE
print("Nom du fichier en entrée:", IFILE)

transactions = []  # résultat à écrire sur fichier

try:
    # Pass the path of the xml document
    tree = parse(IFILE)

    # get the parent tag
    root = tree.getroot()
    ns = {'': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}  # global namespace

    banque = root.findtext('BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/Nm', None, ns)
    bic = root.findtext('BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/BICFI', None, ns)
    print('Banque:   ', banque, '-', bic)
    iban = root.findtext('BkToCstmrStmt/Stmt/Acct/Id/IBAN', None, ns)
    print('IBAN:     ', iban)
    ownr = root.findtext('BkToCstmrStmt/Stmt/Acct/Ownr/Nm', None, ns)
    print('Détenteur:', ownr)

    # la source doit être connu avant ouverture du fichier pour situer le bon répertoire
    # Source = 'inconnu'
    # if BIC == 'BEFRCH22XXX':
    #     Source = 'BCF'
    # if BIC == 'VZDBCHZZXXX':
    #     Source = 'VZ'

    for bal in root.findall('.//Bal', ns):
        amt = Decimal(bal.findtext('Amt', None, ns))
        date = bal.findtext('Dt/', None, ns)
        print('Solde du', date, ':', amt)

    # le premier montant est le solde du début de la période
    SOLDE: Decimal = Decimal(root.findtext('BkToCstmrStmt/Stmt/Bal/Amt', None, ns))

    for ntry in root.findall('.//Ntry', ns):
        Date, Source, Texte, Texte2, Montant, Solde, Categorie = [' ', SOURCE, ' ', ' ', 0, 0, ' ']
        transaction = []

        Date = ntry.findtext('BookgDt/Dt', None, ns)  # format aaaa-mm-jj
        date = ntry.findtext('ValDt/Dt', None, ns)
        ValDt = date[8:]+'.'+date[5:7]+'.'+date[0:4]  # date valeur en format jj.mm.aaaa

        NbOfTxs = ntry.findtext('NtryDtls/Btch/NbOfTxs', None, ns)
        # traitement des batchs multiples
        if NbOfTxs is not None and NbOfTxs > '1':
            print('WARNING - NbOfTxs:', NbOfTxs, Date, ntry.findtext('AddtlNtryInf', None, ns))
            for txs in ntry.findall('NtryDtls/TxDtls', ns):
                Montant, Solde, SOLDE = set_montant(txs, SOLDE)
                Texte, Texte2 = set_texte(txs, 'AddtlTxInf')
                transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
                transactions.append(transaction)
        else:
            Montant, Solde, SOLDE = set_montant(ntry, SOLDE)
            Texte, Texte2 = set_texte(ntry, 'AddtlNtryInf')
            Categorie = env.set_categorie(Texte)
            transaction = [Date, Source, Texte, Texte2, Montant, Solde, Categorie]
            transactions.append(transaction)

except FileNotFoundError:
    print("Ce fichier n'existe pas:", IFILE)
    exit(1)

#  écrire les transactions normalisées sur fichier
OFILE = env.ODIR + SOURCE + "_" + FILE.replace('.xml', '-norm.csv')
with open(OFILE, 'w', newline='') as IFILE:
    writer = csv.writer(IFILE, delimiter=';')
    writer.writerow(env.HEADER)
    writer.writerows(transactions)

print("Fichier de sortie normalisé:", OFILE)
print("Nombre de transactions:", len(transactions))
