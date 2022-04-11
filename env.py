import re
import string
from datetime import datetime
from decimal import Decimal


DIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/'
ODIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/-Compta/'
# transaction normalisée (nouvelle version décembre 2021)
HEADER = ['Date', 'Source', 'Titre', 'Destinataire', 'Usage', 'Montant', 'Solde', 'Catégorie']
CATEGORIES = [
    ('Alimentation, Boucherie', 'boucherie'),
    ('Alimentation, Coop', 'coop'),
    ('Alimentation, Denner', 'denner'),
    ('Alimentation, Gfeller', 'gfeller'),
    ('Alimentation, Marchon', 'marchon'),
    ('Alimentation, Migros', 'migros'),
    ('Cadeaux, dons', 'greenpeace', 'randonnée', 'garde aérienne', 'croix rouge', 'rotes kreuz', 'caritas',
     'terre des hommes'),
    ('Divers, bancomat', 'bancomat'),
    ('Impôts, AVS', 'caisse de compensation'),
    ('Impôts, IFD', 'ifd'),
    ('Impôts, cantonaux', 'contributions'),
    ('Impôts, communaux', 'cottens'),
    ('Loisirs, cinéma', 'st-paul'),
    ('Loisirs, cinéma', 'cinéma', 'arena', 'rex'),
    ('Loisirs, exposition', 'expo', 'fondation'),
    ('Loisirs, hotel', 'hotel'),
    ('Loisirs, livres', 'payot', 'fnac'),
    ('Loisirs, musée', 'musée'),
    ('Loisirs, restaurant', 'restaurant', 'brasserie', 'auberge'),
    ('Loisirs, tea-room', 'tea-room', 'puccini', 'pause'),
    ('Loisirs, théâtre', 'théâtre', 'équilibre'),
    ('Loisirs, voyage', 'voyage'),
    ('Maison, assurances', 'etablissement cantonal', 'mobiliar'),
    ('Maison, hypothèques', 'hypothekenzentrum'),
    ('Maison, internet', 'internet', 'wingo'),
    ('Maison, internet, iCloud espace disque 200 G', 'apple.com/bill'),
    ('Maison, jardin', 'schilliger', 'landi', 'garden centre', 'bauhaus'),
    ('Maison, mobile', 'mobile', 'm-budget'),
    ('Maison, ménage', 'pfister', 'renevey', 'hpschweizgm'),
    ('Maison, électricité', 'groupe e'),
    ('Rentes, caisse de prévoyance du personnel', 'caisse de prévoyance du personnel'),
    ('Rentes, pensionskasse', 'pensionskasse'),
    ('Santé', 'coiffeuse'),
    ('Santé, KPT', 'kpt'),
    ('Santé, dentiste', 'laurent juvet', 'helvident'),
    ('Santé, médecin', 'boscacci', 'promed'),
    ('Santé, pharmacie', 'sunstor', 'pharmacie'),
    ('Transfert', 'report'),
    ('Transfert, Revolut', 'revolut'),
    ('Transfert, TOPCARD', 'topcard', 'compte vz'),
    ('Transfert, TWINT Yogi', '+41774504204'),
    ('Voiture, assurances', 'pool', 'assurances'),
    ('Voiture, benzine', 'station', 'migrol', 'bugnon', 'miniprix'),
    ('Voiture, impôts', 'office'),
    ('Voiture, parking', 'parking'),
    ('Voiture, pneus', 'pneus'),
    ('Voiture, service', 'limat'),
    ('Vêtements', 'pkz', 'decathlon', 'ochsner', 'h & m', 'angéloz', 'manor', 'esprit', 'benetton')
]

# Destinataire = re.sub(pattern[0], replace[1], pour chaque élément)
# Usage = re.sub(pattern[2], replace[3], pour chaque élément)
REGEX = (
    # example: Retrait BM 09:57 CC Matran Numéro de carte: 70097499
    ['^Retrait BM (.{5}) (.*) Numéro de carte: (.*)$', 'Bancomat \\2, \\3',
     '^Retrait BM (.{5}) (.*) Numéro de carte: (.*)$', 'Prélèvement bancomat, \\2, #ValDt# \\1, Carte: \\3'],
    # example: Prélèvement bancomat CHF, COTTENS, 04.09.2021 10:26, Carte: 70097499
    ['^Prélèvement bancomat (.*), (.*), .* Carte: (.*)$', 'Bancomat \\1, \\2',
     '^(Prélèvement bancomat .*, Carte: .*)$', '\\1'],
    # example: Débit direct Maestro 18:14 Omaura SA Numéro de carte: 70097416
    ['^Débit direct Maestro .{5} (.*) Numéro de carte: .*$', '\\1',
     '^(Débit direct Maestro) (.{5}) .* Numéro de carte: (.*)$', '\\1 #ValDt# \\2, Carte: \\3'],
    # example: Débit TWINT pilates Berset, Sandrine, +41793385902 0400000421763661
    ['^Débit TWINT (.*) (.*)$', '\\1',
     '^(Débit TWINT) .* (.*)$', '\\1 \\2'],
    # example: Crédit TWINT Marfurt Fünfschilling, Emilie, +41795676646 0400000506569366
    ['^Crédit TWINT (.*) .*$', '\\1',
     '^(Crédit TWINT) .* (.*)$', '\\1 \\2'],
    # example: Crédit Caisse de prévoyance du personnel
    ['^Crédit (.*)', '\\1',
     '^(Crédit) .*', '\\1'],
    # example: Bonification PENSIONSKASSE BUNDES PUBLICA
    ['^(Bonification) .*', '\\1',
     '^(Bonification) .*', '\\1'],
    # example: Débit e-banking KPT Krankenkasse AG
    ['^Débit e-banking (.*)$', '\\1',
     '^(Débit e-banking) .*', '\\1'],
    # example: Débit LSV+ TOPCARD SERVICE AG
    ['^Débit LSV\+ (.*)$', '\\1',
     '^(Débit LSV\\+) .*', '\\1'],
    # example: Votre ordre de paiement Electro Renevey SA
    # unification avec le terme 'ordre e-banking'
    ['^Votre ordre de paiement (.*)$', '\\1',
     '^Votre ordre de paiement .*', 'Ordre e-banking'],
    # example: Ordre e-banking 990000004057599200081544690
    ['^Ordre e-banking (.*)$', '\\1',
     '^(Ordre e-banking .*)$', '\\1']
)

# 2ème remplacement pour Texte
REGEX2 = (
    ['Pharm.-Parf. Sunstor', 'Pharmacie Sunstore'],
    ['Boul. Poste Marchon', 'Boulangerie Marchon, poste'],
    ['Estava.*', 'Estavayer-le-Lac']
)

ns = {'': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}  # global namespace


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


def set_destinataire_usage(element):
    # AddtlNtryInf ou AddtlTxInf
    if re.sub('{.*}', '', element.tag) == 'TxDtls':
        tag = 'AddtlTxInf'
    else:
        tag = 'AddtlNtryInf'
    inf: str = element.findtext(tag, '', ns)
    dest = clean_destinataire(inf)

    usage = clean_usage(inf)

    # nom et adresse du débiteur/créancier dans certains cas
    if 'e-banking' in usage or 'ordre' in usage or 'Bonification' in usage:
        if element.findtext('CdtDbtInd', None, ns) == 'DBIT':
            tag = 'Cdtr'
        else:
            tag = 'Dbtr'
        party = element.find('RltdPties/' + tag, ns)
        if party is not None:
            dest = party.findtext('Nm', '', ns)
            if party.find('PstlAdr', ns) is not None:
                for child in party.find('PstlAdr', ns):
                    dest = dest + ', ' + child.text

    # payement en monnaie étrangère
    montant = element.find('AmtDtls/TxAmt/Amt', ns)
    if montant is not None:
        ccy = montant.attrib['Ccy']  # devise
        if ccy != 'CHF':
            rate = element.findtext('AmtDtls/TxAmt/CcyXchg/XchgRate', 'default', ns)
            print(ccy, rate)
            usage = usage + ' (' + ccy + ' à ' + rate + ')'

    return dest, usage


def clean_destinataire(texte):
    # corrige un BUG de données mal encodées
    # http://www.unicode-symbol.com/u/FFFD.html
    t = re.sub('\N{replacement character}', '', texte)
    t = re.sub('Maracher', 'Maraîcher', t)
    t = re.sub('Dbit', 'Débit', t)

    t0 = t
    for exp in REGEX:
        t = re.sub(exp[0], exp[1], t0)
        if t != t0:
            break
    for exp in REGEX2:
        t = re.sub(exp[0], exp[1], t)

    t = clean_maestro(t)
    return t


def clean_usage(texte):
    # corrige un BUG de données mal encodées
    # http://www.unicode-symbol.com/u/FFFD.html
    t = re.sub('\N{replacement character}', '', texte)
    t = re.sub('Dbit', 'Débit', t)
    t = re.sub('Maracher', 'Maraîcher', t)

    t0 = t
    for exp in REGEX:
        t = re.sub(exp[2], exp[3], t0)
        if t != t0:
            break

    # unification des termes entre les banques
    t = re.sub('Votre ordre de paiement', 'Ordre e-banking', t)
    # nom du détenteur de carte
    t = clean_maestro(t)
    return t


def clean_maestro(texte):
    texte = re.sub('70097416', 'Marie', texte)
    texte = re.sub('70097499', 'Yogi', texte)
    return texte


def set_titre_categorie(destinataire, montant):
    titre, categorie = ['', '']
    for c in CATEGORIES:
        for _ in c:
            if _ in destinataire.lower():
                titre = c[0]
                categorie = re.sub('(.*), .*', '\\1', titre)
                break
        if titre > '':
            break

    # exceptions:
    if 'ERV,' in destinataire:  # confusion avec service
        titre = 'Voiture, assurances'
        categorie = 'Voiture'

    # affinement catégerie selon montant
    valeur = Decimal(montant.replace(',', '.')) * -1
    if 'wingo' in destinataire.lower() and valeur < 40:
        titre = re.sub('internet', 'mobile', titre)
    if 'KPT' in destinataire and valeur > 974:
        titre = titre + ', prime'


    return titre, categorie


def correct_date(date):
    date = date.replace('janv.', 'janvier', 1)
    date = date.replace('fév.', 'février', 1)
    date = date.replace('avr.', 'avril', 1)
    date = date.replace('juil.', 'juillet', 1)
    date = date.replace('sept.', 'septembre', 1)
    date = date.replace('oct.', 'octobre', 1)
    date = date.replace('nov.', 'novembre', 1)
    date = date.replace('déc.', 'décembre', 1)
    return datetime.strptime(date, '%d %B %Y').strftime('%Y-%m-%d')
