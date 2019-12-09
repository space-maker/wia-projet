# wia-projet
Projet d'école sur l'extraction de relations au sein de corpus.

# Objectif du programme
L'objectif du programme est de récolter des informations Ã  partir d'un texte sur les relations entre les différents personnages, fictifs ou pas. Par exemple, dans un texte fictif, une phrase tel que "Alice est la soeur de Bob" relie Alice à Bob dans une catégorie famille. On peut ainsi lister tous les personnages disponibles dans le texte puis en ressortir les relations potentielles entre protagoniste de la narration.

# Utilisation du programme
## Prérequis
Pour faire ce programme, on, utilise conda pour créer un environnement virtuel dédiée Ã  la matière WIA. Puis, on installe ceci:
spacy 2.1 (pip install spacy )

neuralcoref (pip install neuralcoref)

python -m spacy download en_core_web_sm (modèle utilisé)

Une version plus récente de spacy existe mais Ã  cause de difficultés de fonctionnement liés Ã  neuralcoref, une version plus ancienne a été testé et fonctionne correctement.
Ne pas oublier d'installer des modèles telles que 'en_core_web_[sm-md-lg]'.

## Exécution du programme
Le programme se lance en introduisant la chemin du corpus et le chemin du corpus annoté (avec la liste des relations entre deux personnages). On peut aussi activer la recherche de coréférences 
ou pas. Attention !!! La coréférence peut prendre **beaucoup** de temps.

# Contribution
Auteur: BOAKNIN Jonathan

Mail: jonathan.boaknin@ensiie.fr
