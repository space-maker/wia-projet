# wia-projet
Projet d'école sur l'extraction de relations au sein de corpus.

# Objectif du programme
L'objectif du programme est de récolter des informations à partir d'un texte sur les relations entre les différents personnages, fictifs ou pas. Par exemple, dans un texte fictif, une phrase tel que "Alice est la soeur de Bob" relie Alice 
à Bob dans une catégorie famille. On peut ainsi lister tous les personnages disponibles dans le texte puis en ressortir les relations potentielles entre protagoniste de la narration.

# Utilisation du programme
## Prérequis
Pour faire ce programme, on, utilise conda pour créer un environnement virtuel dédiée à la matière WIA. Puis, on installe ceci:
spacy 2.1 (pip install spacy )
neuralcoref (pip install neuralcoref)
python -m spacy download en_core_web_sm (modèle utilisé)

Une version plus récente de spacy existe mais à cause de difficultés de fonctionnement liés à neuralcoref, une version plus ancienne a été testé et fonctionne correctement.

# Contribution
Auteur: BOAKNIN Jonathan

Mail: jonathan.boaknin@ensiie.fr
