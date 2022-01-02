import re
from datetime import datetime


DIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/'
ODIR = '/Users/yogi/Library/Mobile Documents/com~apple~CloudDocs/Factures/-Compta/'
HEADER = ['Date', 'Source', 'Titre', 'Destinataire', 'Usage', 'Montant', 'Solde', 'Catégorie']  # transaction normalisée
CATEGORIES = [
    ('Alimentation', 'migros', 'denner', 'marchon', 'gfeller', 'coop', 'boucherie'),
    ('Cadeaux', 'greenpeace', 'randonnée', 'garde aérienne'),
    ('Impôts', 'ifd', 'contributions'),
    ('Loisirs', 'payot', 'fnac', 'tea-room', 'restaurant', 'hotel', 'cinema', 'theatre', 'expo'),
    ('Maison & Jardin', 'hypthekenzentrum', 'groupe e', 'etablissement cantonal d', 'schilliger', 'landi',
        'garden centre', 'bauhaus', 'internet', 'mobile'),
    ('Rentes', 'pensionskasse', 'caisse de prévoyance du personnel'),
    ('Santé', 'kpt', 'sunstor', 'boscacci', 'laurent juvet', 'promed', 'helvident', 'coiffeuse'),
    ('Transfert', 'topcard', 'revolut'),
    ('Voiture', 'garage', 'tcs', 'essence', 'station', 'migrol'),
    ('Vêtements', 'pkz', 'decathlon', 'ochsner', 'h & m'),
    ('Divers', 'bancomat')
]

# Texte = re.sub(pattern[0], replace[1], pour chaque élément)
# Texte2 = re.sub(pattern[2], replace[3], pour chaque élément)
REGEX = (
    # example: Prélèvement bancomat CHF, COTTENS, 04.09.2021 10:26, Carte: 70097499
    ['^(Prélèvement bancomat .*), Carte: .*$', '\\1',
     '^Prélèvement bancomat .*, Carte: (.*$)', 'Maestro \\1'],
    # example: Débit direct Maestro 18:14 Omaura SA Numéro de carte: 70097416
    ['^Débit direct Maestro .{5} (.*) Numéro de carte: .*$', '\\1',
     '^Débit direct Maestro (.{5}) .* Numéro de carte: (.*)$', 'Maestro \\2 #ValDt# \\1'],
    # example: Débit TWINT pilates Berset, Sandrine, +41793385902 0400000421763661
    ['^Débit TWINT (.*) .*$', '\\1 TWINT',
     '^Débit TWINT .* (.*)$', 'TWINT \\1'],
    # example: Crédit TWINT Marfurt Fünfschilling, Emilie, +41795676646 0400000506569366
    ['^Crédit TWINT (.*) .*$', '\\1 TWINT',
     '^Crédit TWINT .* (.*)$', 'TWINT \\1'],
    # example: Crédit Caisse de prévoyance du personnel
    ['Crédit (Caisse de prévoyance du personnel)', '\\1',
     '(Crédit) Caisse de prévoyance du personnel', '\\1'],
    # example: Bonification PENSIONSKASSE BUNDES PUBLICA
    ['Bonification (.*)', '\\1',
     '(Bonification) .*', '\\1'],
    #
    ['Votre ordre de paiement (.*)', '\\1',
     '(Votre ordre de paiement) .*', '\\1'],
    ['Débit e-banking (.*)', '\\1',
     'Débit (e-banking) .*', '\\1'],
    ['Débit LSV\\+ (.*)', '\\1',
     'Débit (LSV\\+) .*', '\\1'],
    ['Ordre e-banking (.*)', '\\1',
     'Ordre (e-banking) .*', '\\1']
)

# 2ème remplacement pour Texte
REGEX2 = (
    ['Pharm.-Parf. Sunstor', 'Pharmacie Sunstore'],
    ['Boul. Poste Marchon', 'Boulangerie Marchon, poste']
)


def set_texte(texte):
    t: str = ''
    for exp in REGEX:
        t = re.sub(exp[0], exp[1], texte)
        if t != texte:
            break
    for exp in REGEX2:
        t = re.sub(exp[0], exp[1], t)
    return t


def set_texte2(texte):
    t: str = ''
    for exp in REGEX:
        t = re.sub(exp[2], exp[3], texte)
        if t != texte:
            break

    t = re.sub('70097416', 'Marie', t)
    t = re.sub('70097499', 'Yogi', t)
    return t


def set_categorie(texte):
    # exceptions:
    if texte == 'ERV':  # confusion avec service
        return 'Voiture'

    for categorie in CATEGORIES:
        for _ in categorie:
            if _ in texte.lower():
                return categorie[0]
    return ''


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
