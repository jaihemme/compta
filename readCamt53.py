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
# . ValDt/Dt --> ValDt --> Usage, précision pour opérations banquaires
# . Amt --> Montant (csv)
# . CdtDbtInd = 'CRDT' ou 'DBIT' --> signe +/- de Montant
# . AddtlNtryInf --> Destinataire + Usage
# . NtryDtls/Btch/NbOfTxs --> nombre de transactions batch (none ou 1+)
# . if NbOfTxs>0: ntry.findall('NtryDtls/TxDtls', ns):
# . . Amt --> Montant
# . . CdtDbtInd = 'CRDT' ou 'DBIT' --> signe +/- de Montant
# . . AddtlTxInf --> Destinataire + Usage
# . . RltdPties/Cdtr/Nm --> créancier --> Destinataire (si e-banking)

import argparse
import csv
import env
from xml.etree.ElementTree import parse
from decimal import Decimal
import re


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
    ns = env.ns  # global namespace

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
        transaction = []
        Date = ntry.findtext('BookgDt/Dt', None, ns)  # format aaaa-mm-jj
        date = ntry.findtext('ValDt/Dt', None, ns)
        ValDt = date[8:]+'.'+date[5:7]+'.'+date[0:4]  # date valeur en format jj.mm.aaaa

        NbOfTxs = ntry.findtext('NtryDtls/Btch/NbOfTxs', None, ns)
        print('WARNING - NbOfTxs:', NbOfTxs, Date, ntry.findtext('AddtlNtryInf', None, ns))
        # traitement des batchs multiples
        if NbOfTxs is not None:
            for txs in ntry.findall('NtryDtls/TxDtls', ns):
                Montant, Solde, SOLDE = env.set_montant(txs, SOLDE)
                Destinataire, Usage = env.set_destinataire_usage(txs)
                Usage = re.sub('#ValDt#', ValDt, Usage)
                Titre, Categorie = env.set_titre_categorie(Destinataire, Montant)
                transaction = [Date, SOURCE, Titre, Destinataire, Usage, Montant, Solde, Categorie]
                transactions.append(transaction)
        else:
            Montant, Solde, SOLDE = env.set_montant(ntry, SOLDE)
            Destinataire, Usage = env.set_destinataire_usage(ntry)
            Usage = re.sub('#ValDt#', ValDt, Usage)
            Titre, Categorie = env.set_titre_categorie(Destinataire, Montant)
            transaction = [Date, SOURCE, Titre, Destinataire, Usage, Montant, Solde, Categorie]
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
