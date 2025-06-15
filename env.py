import re
from datetime import datetime
from decimal import Decimal


DIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/'
ODIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/-Compta/'
# transaction normalisée (nouvelle version décembre 2021)
HEADER = ['Date', 'Source', 'Titre', 'Destinataire', 'Usage', 'Montant', 'Solde', 'Catégorie']
# (catégorie, tag(s) en minuscules, ...), le premier cas trouvé prime
CATEGORIES = [
    ('Loisirs, tea-room', 'tea-room', 'pause'),
    # jardin avant coop et migros (alimentation)
    ('Appartement, ménage', 'schilliger', 'landi', 'garden centre', 'bauhaus', 'do it garden'),
    # coiffeuse avant cottens (impôts)
    ('Santé', 'coiffeuse'),
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
    ('Impôts, communaux', 'commune de cottens'),
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
    ('Appartement, assurances', 'etablissement cantonal', 'mobiliar'),
    ('Appartement, hypothèques', 'hypothekenzentrum'),
    # mobile avant internet pour m-budget
    ('Appartement, mobile', 'mobile', 'm-budget'),
    ('Appartement, internet', 'internet', 'wingo'),
    ('Appartement, internet, iCloud espace disque 200 G', 'Apple', 'apple.com/bill'),
    ('Appartement, mobile', 'mobile', 'm-budget'),
    ('Appartement, ménage, abonnement imprimante HP', 'HP', 'hp instant ink', 'hpschweizgm'),
    ('Appartement, ménage', 'pfister', 'renevey', 'livique'),
    ('Appartement, électricité', 'groupe e'),
    ('Rentes, caisse de prévoyance du personnel', 'caisse de prévoyance du personnel'),
    ('Rentes, pensionskasse', 'pensionskasse'),
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
    # Retrait bancomat CHF, COTTENS, 11:53, carte: 535445******8471 (BCF depuis 11.2023)
    # Retrait bancomat CHF, AVRY-CENTRE 2, 23.11.2023 13:58, carte: Marie
    ['^Retrait bancomat CHF, (.*), (.*), carte: (.*)$', 'Bancomat \\1, \\2',
     '^Retrait bancomat CHF, (.*), (.*), carte: (.*)$', 'Prélèvement bancomat, \\1, #ValDt# \\2, Carte: \\3'],
    # example: Retrait BM COTTENS COTTENS CH - 07.01 10:08:56 - xxxxxxxxxxxx8471 - 200 CHF
    ['^Retrait BM (.*) - (.* .*) - (.*) - .* .*$', 'Bancomat \\1',
     '^Retrait BM (.*) - (.* .*) - (.*) - .* (.*)$', 'Prélèvement bancomat \\4 du \\2, Carte: \\3'],
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
    ['^Débit LSV\\+ (.*)$', '\\1',
     '^(Débit LSV\\+) .*', '\\1'],
    # example: Votre ordre de paiement Electro Renevey SA
    # unification avec le terme 'ordre e-banking'
    ['^Votre ordre de paiement (.*)$', '\\1',
     '^Votre ordre de paiement .*', 'Ordre e-banking'],
    # example: Ordre e-banking 990000004057599200081544690
    ['^Ordre e-banking (.*)$', '\\1',
     '^(Ordre e-banking .*)$', '\\1'],
    # example: Achats carte de débit 27.06.2022 10:56 Migros MMM Avry Numéro de carte: 5352220006123662
    ['^Achats carte de débit .* [0-9]{2}:[0-9]{2} (.*) Numéro de carte: .*', '\\1',
     '(^Achats carte de débit .* [0-9]{2}:[0-9]{2}) .* Numéro de carte: (.*)', '\\1, \\2'],
    # Bancomat 26.06.2022 09:05 COTTENS Numéro de carte: 5352220006121518
    ['^Bancomat .* .* (.*) Numéro de carte: .*', 'Bancomat \\1',
     '^Bancomat (.* .*) (.*) Numéro de carte: (.*)', 'Prélèvement bancomat \\2, \\1, Carte: \\3'],
    # Paiement 31.10.2023 15:01 Coop-3585 Numéro de carte: 535445******8471 (BCF depuis 11.2023)
    ['^Paiement (.{10} .{5}) (.*) Numéro de carte: (.*)$', '\\2',
     '^Paiement (.{10} .{5}) (.*) Numéro de carte: (.*)$', 'Carte \\3, paiement du \\1'],
    # Paiement - CAL_Bulle_C604, Bulle - 04.01.2023 15:08 - N° carte xxxxxxxxxxxx8471 - 34.50 CHF (BCF depuis 2023)
    ['^Paiement - (.*) - (.* .*) - N° carte (.*) .*', '\\1',
     '^Paiement - (.*) - (.* .*) - N° carte (.*) - .*', 'Carte \\3, paiement du \\2']
)

# 2ème remplacement pour Texte
REGEX2 = (
    ['Pharm.-Parf. Sunstor', 'Pharmacie Sunstore'],
    ['Pharmacie Sunstoree', 'Pharmacie Sunstore'],
    ['Boul. Poste Marchon', 'Boulangerie Marchon, poste'],
    ['Bou.-P.tiss.Marchon', 'Boulangerie Marchon, poste'],
    ['Estava.*', 'Estavayer-le-Lac']
)


ns = None  # namespace global


def init_ns(source):
    global ns
    if source == 'BCF':
        ns = {'': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08'}
    elif source == 'VZ':
        ns = {'': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.04'}


def set_montant(element, solde, ttlamt):
    sign = ''
    montant: str = element.findtext('Amt', None, ns)  # montant, p.ex 12.3
    if element.findtext('CdtDbtInd', None, ns) == 'CRDT':
        sign = '+'  # crédit
    if element.findtext('CdtDbtInd', None, ns) == 'DBIT':
        sign = '-'  # débit
    montant = sign + montant  # ajoute le signe comme prefixe

    # traitement foireux des devises étrangères par la BCF
    if ttlamt is not None and ttlamt != montant:
        print('WARNING - BCF, montants différents, problème avec devise étrangère', ttlamt, montant)
        montant = ttlamt

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
    # http://www.unicode-symbol.com/u/FFFD.html
    # BUG de données mal encodées chez VZ semble corrigé en juillet 2022

    t = ''
    t0 = texte
    for exp in REGEX:
        t = re.sub(exp[0], exp[1], t0)
        if t != t0:
            break
    for exp in REGEX2:
        t = re.sub(exp[0], exp[1], t)

    t = clean_maestro(t)
    return t


def clean_usage(texte):
    # http://www.unicode-symbol.com/u/FFFD.html
    # BUG de données mal encodées chez VZ semble corrigé en juillet 2022

    t = ''
    t0 = texte
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
    texte = re.sub(r'\d{4}.{8}3662', 'Marie', texte)
    texte = re.sub('.{12}8471', 'Marie', texte)
    texte = re.sub('70097499', 'Yogi', texte)
    texte = re.sub(r'\d{4}.{8}1518', 'Yogi', texte)
    return texte


def set_titre_categorie(destinataire, montant):
    titre, categorie = ['', '']
    for c in CATEGORIES:
        for _ in c:
            if _ in destinataire.lower():
                titre = c[0]
                categorie = re.sub('(.*?), .*', '\\1', titre)
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
    if 'KPT' in destinataire and valeur > 1300:
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
