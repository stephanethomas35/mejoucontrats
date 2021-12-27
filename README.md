# Générateur de contrats pour Le Méjou
Exécuter
```sh
python mejougui.py
```

# Prérequis
Python 3.9

# Problèmes identifiés
1. La mise à jour des réservations par les boutons `Bloquer` et `Annuller` ne raffraichit pas la
liste des réservations.

# Templates
Les templates se trouvent dans le répertoire `templates`. Pour les

# Fichiers de configuration
## mejoucontrats.ini
Paramètres de la sernière location traitée par la script. Ce sont ces valeurs qui seront affichées
lors de la prochaine exécution.

## mejougites.ini
Définit tous les gîtes. Pour chacun, donne les valeurs:
- lits: Nombre de lits
- caution: Montant de la caution
- semaine_menage: Montant du ménage pour une semaine de location (ou plus)
- semaine_basse: Loyer d'une semaine en **basse** saison
- semaine_moyenne: Loyer d'une semaine en **moyenne** saison
- semaine_haute: Loyer d'une semaine en **haute** saison
- semaine_t_haute: Loyer d'une semaine en **très haute** saison
- nuit_menage: Montant du ménage pour une nuit de location (ou plus)
- nuit_basse: Loyer d'une nuit en **basse** saison
- nuit_moyenne: Loyer d'une nuit en **moyenne** saison

## mejousaisons.ini
Donne les dates de début et de fin de chaque saison. Ce fichier doit être mis à jour pour chaque
année.

Le format est le suivant
```
[2022_haute1]
debut = 02/07/22
fin   = 11/07/22
type  = haute
```

### section
Le nom de la section est purement informative. Elle doit juste être unique dans le fichier.

### debut
(tag sans accent)
Date de début de la saison.

### fin
Date de début de la saison.
Note: la date de fin est le samedi, donc doit être égale à la date de début de la saison suivante.

### type
Type de la saison. Les valeurs possibles sont :
- `basse`
- `moyenne`
- `haute`
- `tres haute`

# Outils
## pipinstall.bat
Permet d'installer les bibliothèques requises.

## mejou_qrcode
Génère un fichier png contenant l'URL des avis sur Google.