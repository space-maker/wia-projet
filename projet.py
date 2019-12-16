# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 15:52:19 2019

@author: jonat
"""

import spacy
import re

# =============================================================================
# Fonctions intermédiaires.
# =============================================================================
"""
Enlève les noms qui se ressemblent. Par exemple, "Alice Lee", "Alice" ou 
"Mme Lee" sont en général les mêmes personnages.
Attention: ne marche pas tout le temps car "Mme Lee" peut désigner un autre
personnage.
"""
def clean_characters(characters):
    # On supprimer les "Monsieur", "Madame" des noms des personnages.
    # Le strip supprime les espaces sur le côté droit et gauche du nom.
    c = list(map(lambda s: re.sub("mrs |mme |'s|mr |'|miss |mister |the "\
                                  , "", s).strip(),\
                 list(characters)))
    c_clean = []
    
    while c != []:
        count = 0
        c_clean.append(c[0])
        
        c_tmp = c.copy()
        for k in range(1, len(c_tmp)):
            s = " " + c_tmp[k] + "$|^" + c_tmp[k] + " | " + c_tmp[k] + " |^"\
                + c_tmp[k] + "$"
            if re.search(s, c_tmp[0]) is not None:
                del c[k - count]
                count += 1
        del c[0]                    
    
    return c_clean


"""
Extrait des personnages
"""
def extract_characters(doc):
    characters = {}
    
    for entity in doc.ents:
        if entity.label_ == "PERSON":
            if entity.text.lower() in characters:
                characters[entity.text.lower()].append({"pos_start": \
                          entity.start_char, "pos_end": entity.end_char})
                # print(entity, entity.text, entity.label_, entity.start_char)  
            else:
                characters[entity.text.lower()] = [\
                          {"pos_start": \
                          entity.start_char, "pos_end": entity.end_char}]
    
    """
    Le trie sert à mettre en avant les noms "complets" dans la fonction
    de nettoyage. Par exemple si Alice et Alice Lee sont une même personne,
    on préfera garder le nom entier Alice Lee.
    """
    return clean_characters(sorted(characters, \
                                   key = lambda s: len(s), reverse = True))

    
"""
Vérifie si un token correspond à un personnage. (fonctionnement basique)
Exemple: Le token "Alice" correspond au personnage "Alice Lee".
"""
def match_character(token, list_characters):
    for chara in list_characters:
        token_text = token.text.lower()
        s = " " + token_text + "$|^" + token_text + " | " + token_text + " |" \
            + "^" + token_text + "$"
        
        if token.pos_ != "PUNCT" and re.match(s, chara) \
            is not None:
            return chara
        
    return None

"""
Vérifie si un token correspond à une catégorie. (fonctionnement basique)
Exemple: Le token "sister" correspond à la catégorie "famille".
"""
def match_category(token, cat):
    for c in cat:
        if token.lower() in cat[c]:
            return c
        
    return None

"""
Fonction qui permet d'éviter les doublons dans la liste des relations entre
personnages
"""
def exist_relation(relations, c1, c2, relation_type):
    for r in relations:
        for key in r:
            rc1 = key
            rc2 = r[key][1]
            
            r_type = r[key][0]

            if (relation_type is None or r_type == relation_type) and \
                ((rc1 == c1 and rc2 == c2)\
                or (rc2 == c1 and rc1 == c2)):
                    return True
    
    return False


"""
Extrait les relations des personnages
"""
def extract_relation(relations, cat, doc, characters, match_charac,\
                     start_token, stop_iteration):
    stop_iteration = stop_iteration + start_token\
    if (stop_iteration + start_token) < len(doc) else len(doc) - 1
    
    for index in range(start_token, stop_iteration):
        c = match_category(doc[index].text, cat)
       
        if (c is not None):
            for indexbis in range(index, len(doc) - 1):
                
                match_charac_2 = match_character(doc[indexbis], characters)
                """
                On évite les relations de type "A est en relation avec A" et
                les doublons comme "A [relation] B" == "B [relation] A"
                """
                if match_charac_2 is not None and \
                    match_charac != match_charac_2 and \
                    exist_relation(relations, match_charac, match_charac_2\
                                   , None) == False:
                    relations.append({match_charac: [c, match_charac_2]})
                    break
            break
    
# =============================================================================
# Analyse d'un texte
# =============================================================================
import numpy as np



def get_doc(nlp, corpus, neuralcoref_active):
    doc = nlp(corpus)
    
    """
    Change les coréférences par leurs noms associés. Par exemple, 
    si 'him' désinge 'Harry', alors on remplace 'him' par 'Harry'.
    """
    # Coréférences
    print("Analyse du texte en cours...")    
    if neuralcoref_active:
        pronouns = ["I", "you", "she", "he", "it", "we", "they", "me", "him"\
                    , "her", "my", "mine", "your", "yours", "his", "her"\
                 , "who", "whom", "whose", "that", "which", "another", "other"\
                    , "myself", "them", "their", "yourself", "themself"]
        
        a = doc._.coref_clusters
        corpus_neural = np.array(doc, dtype = str)
        
        for x in a:
            for y in x.mentions:
                # Gestion des noms composés de type "Prenom Nom"
                # c = y._.coref_cluster.main.text.split()
                if y ==  y._.coref_cluster.main or \
                    y.text.lower() not in pronouns:
                    continue
                else:
                    corpus_neural[y.start] = y._.coref_cluster.main.text
                # corpus_neural[y.start] = y._.coref_cluster.main
        
        corpus_new = ""
        for s in np.array(corpus_neural, dtype=str):
            corpus_new += " " + s
        
        doc = nlp(corpus_new)
    
    print("Analyse terminée.")
    
    # Analyse effective du texte
    
    # Liste des personnages
    characters = extract_characters(doc)
    
    return (doc, characters)
    
    # relations = ['Personnage1': {lien de la relation, Personnage2}]
"""
Fonction d'analyse des relations
"""
def start_analyze_relationships(doc, characters, stop_iteration):
    relations = []
    start = 0
    for token in doc:
        start += 1
        # Correspondance d'un personnages
        match_charac = match_character(token, characters)
        if match_charac is None:
            continue
        
        """
        Si on trouve une correspondance d'un personnage, on vérifie une 
        relation potentielle avec un autre personnage parmi les 
        'stop_iteration' tokens suivants à partir du token actuel.
        """
        extract_relation(relations, cat, doc, characters, match_charac, start,\
                         stop_iteration)

    return relations


# =============================================================================
# Évaluations du résultat
# =============================================================================
import matplotlib.pyplot as plt
        
def match_between_relations(relations1, relations2):
    c = 0
    
    for r in relations1:
        for r_text in r:
            c1 = r_text
            c2 = r[r_text][1]

            relation_type = r[r_text][0]
                        
            if exist_relation(relations2, c1, c2, relation_type):
                c += 1
                
    return c
            

def eval_match(start_k, stop_k, doc, characters, relations_annoted):
    cardinal_relations_annoted = len(relations_annoted)
    n = (stop_k - start_k) + 1
    
    recall = np.empty(n)
    accuracy = np.empty(n)
    
    start = 0
    
    for k in range(start_k, stop_k + 1):
        relations = start_analyze_relationships(doc, characters, k)
        
        m = match_between_relations(relations, relations_annoted)
        
        recall[start] = (m / cardinal_relations_annoted)
        accuracy[start] = (m / len(relations)) if len(relations) > 0 else 0
        
        start += 1
        
    plt.clf()
    plt.grid()
    
    plt.xlabel("Décalage de k-occurences")
    plt.ylabel("Rappel / Précisions")
    
    t = np.arange(start_k, stop_k + 1)
    plt.plot(t, recall, "kx-", label = "Rappel")
    plt.plot(t, accuracy, "rx-", label = "Précision")
    
    plt.legend()
    
    
    plt.show()
    
    plt.figure()
    plt.grid()
    
    plt.xlabel("Rappel")
    plt.ylabel("Précision")
    
    plt.plot(recall, accuracy, "kx-")
    
    plt.show()
    
    return (recall, accuracy)
# =============================================================================
# Exécution des fonctions principales
# =============================================================================





# Chargement du modèle
print("Chargement du modèle...")

# Avec CUDA installé (version 9.2 utilisé ici)
# spacy.prefer_gpu()
nlp = spacy.load('en_core_web_sm')

# Activer ou non la coréférence. Peut prendre un certain temps d'exécution.
neuralcoref_active = False

if neuralcoref_active:
    import neuralcoref
    neuralcoref.add_to_pipe(nlp)


print("Ouverture et lecture du contenu en mode read only...")

cat = {}
# Ouverture du fichier qui contient les catégories de relations possibles
with open('relations_properties.txt', 'r') as content_file:
    for line in content_file:
        content = line.strip().split(':')
        cat[content[0]] = content[1].strip().split()

"""
Programme principale
name_corpus: nom du corpus
name_corpus_annote: nom du corpus annoté
characters: permet d'ajouter les personnages manuellement au lieu d'utiliser
l'extracteur automatique du programme (mettre [] pour extraire auto)
graph: mode d'évaluation rappel / précision
"""
def run_extration(name_corpus, name_corpus_annote, characters_input, k, \
                  graph = False, start_k = 1, stop_k = 20):
    # Ouverture du corpus
    with open(name_corpus, 'r') as content_file:
        corpus = content_file.read().strip().replace('\n', ' ')
        
    doc, characters = get_doc(nlp, corpus, neuralcoref_active)
    
    if characters_input != []:
        print("Extraction of characters not auto")
        characters = characters_input
    
    relations = start_analyze_relationships(doc, characters, k)
    print(relations)
    
    
    # Ouverture du corpus annoté
    relations_annoted = []
    
    with open(name_corpus_annote, 'r') as content_file:
        for line in content_file:
            corpus_annote = line.strip().split(',')
            relations_annoted.append({corpus_annote[0].lower(): \
                                      [corpus_annote[1],\
                                        corpus_annote[2].lower()]})
    recall, accuracy = [], []
    if graph:
        recall, accuracy = eval_match(start_k, stop_k, doc, characters, \
                                      relations_annoted)
        
    return (characters, recall, accuracy)

# Paramètres principales du programme

# =============================================================================
# Debug
# =============================================================================
name_corpus = "corpus/debug.txt"
name_corpus_annote = "corpus/debug_annote.txt"
characters = run_extration(name_corpus, name_corpus_annote, [], 5, True)

# =============================================================================
# Sherlock Holmmes
# =============================================================================
name_corpus = "corpus/sherlock.txt"
name_corpus_annote = "corpus/sherlock_annote.txt"
characters = run_extration(name_corpus, name_corpus_annote, [], 5)
   
# =============================================================================
# Little Women
# =============================================================================
name_corpus = "corpus/little_womens.txt"
name_corpus_annote = "corpus/little_womens_annote.txt"
characters = run_extration(name_corpus, name_corpus_annote, [], 5, True)

# =============================================================================
# Main Street (personnages ajoutés manuellement)
# =============================================================================
name_corpus = "corpus/main_street.txt"
name_corpus_annote = "corpus/main_street_annote.txt"
characters = [
    "carol",
    "kennicott",
    "raymond wutherspoon",
    "guy pollock",
    "vida sherwin",
    "miles bjornstam",
    "bea sorenson",
    "erik valborg",
    "maud dyer",
    "whittier smail"
    ]
characters = run_extration(name_corpus, name_corpus_annote, characters, \
                            5, True)

# =============================================================================
# Middlermarch (assez long à exécuter)
# =============================================================================
characters = [
    "dorothea brooke",
    "edward casaubon",
    "will ladislaw",
    "harriet bulstrode",
    "arthur brooke",
    "godwin lydgate",
    "wrench",
    "fred vincy",
    "tertius lydgate",
    "rosamond vincy"
    ]
name_corpus = "corpus/middlemarch.txt"
name_corpus_annote = "corpus/middlemarch_annote.txt"
characters = run_extration(name_corpus, name_corpus_annote, characters, \
                            5, True)
        

# =============================================================================
# Évaluation totale (très long à exécuter, coréférence à exclure si possible)
# =============================================================================
corpus_array = [
    "corpus/debug.txt",
    "corpus/little_womens.txt",
    "corpus/sherlock.txt",
    "corpus/main_street.txt",
    "corpus/middlemarch.txt"
    ]

corpus_annote_array = [
    "corpus/debug_annote.txt",
    "corpus/little_womens_annote.txt",
    "corpus/sherlock_annote.txt",
    "corpus/main_street_annote.txt",
    "corpus/middlemarch_annote.txt"
    ]

characters = [
    [],
    [],
    [],
    [
    "carol",
    "kennicott",
    "raymond wutherspoon",
    "guy pollock",
    "vida sherwin",
    "miles bjornstam",
    "bea sorenson",
    "erik valborg",
    "maud dyer",
    "whittier smail"
    ],
    [
    "dorothea brooke",
    "edward casaubon",
    "will ladislaw",
    "harriet bulstrode",
    "arthur brooke",
    "godwin lydgate",
    "wrench",
    "fred vincy",
    "tertius lydgate",
    "rosamond vincy"
    ]
    ]

recall, accuracy = [], []
for k in range(len(corpus_array)):
    _, recall_tmp, accuracy_tmp = run_extration(corpus_array[k], \
                                corpus_annote_array[k], characters[k], 5,\
  True)
    recall.append(recall_tmp)
    accuracy.append(accuracy_tmp)
    
r = sum(recall) / len(corpus_array)
a = sum(accuracy) / len(corpus_array)
k = np.arange(1, 21)

plt.clf()
plt.grid()

plt.xlabel("Occurence k")

plt.plot(k, r, label = "Rappel")
plt.plot(k, a, label = "Précision")

plt.legend()

plt.show()

# Graphe rappel-précision

plt.clf()
plt.grid()

plt.xlabel("Rappel")
plt.ylabel("Précision")

plt.plot(r, a)

plt.show()