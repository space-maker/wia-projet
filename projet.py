# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 15:52:19 2019

@author: jonat
"""

import spacy
import re


print("Chargement du modèle...")
nlp = spacy.load('en_core_web_sm')

# Activer ou non la coréférence
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
    
# Ouverture du corpus
with open('corpus/sherlock.txt', 'r') as content_file:
    corpus = content_file.read().strip().replace('\n', ' ')

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
    # On supprimer les "Monsieur", "Madame" des noms des personnages
    c = list(map(lambda s: re.sub("mrs |mme |'s|mr ", "", s),\
                 list(characters)))
    c_clean = []
    
    while c != []:
        count = 0
        c_clean.append(c[0])
        
        c_tmp = c.copy()
        for k in range(1, len(c_tmp)):
            s = c_tmp[k] + "$|^" + c_tmp[k] + "| " + c_tmp[k] + " " 
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
    
    return characters

    
"""
Vérifie si un token correspond à un personnage. (fonctionnement basique)
Exemple: Le token "Alice" correspond au personnage "Alice Lee".
"""
def match_character(token, list_characters):
    for chara in list_characters:

        if token.pos_ != "PUNCT" and re.match(token.text.lower(), chara) \
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
            
            # r_type = r[key][0]
            # r_type == relation_type and 
            if ((rc1 == c1 and rc2 == c2)\
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
                                   , c) == False:
                    relations.append({match_charac: [c, match_charac_2]})
                    break
            break
    
# =============================================================================
# Analyse d'un texte
# =============================================================================
import numpy as np

# Coréférences
print("Analyse du texte en cours...")    

doc = nlp(corpus)

if neuralcoref_active:
    a = doc._.coref_clusters
    corpus_neural = np.array(doc, dtype = str)
    
    for x in a:
        for y in x.mentions:
            # Gestion des noms composés de type "Prenom Nom"
            c = y._.coref_cluster.main.text.split()
            if y ==  y._.coref_cluster.main:
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

relations = start_analyze_relationships(doc, characters, 5)
print(relations)

# =============================================================================
# Évaluations du résultat
# =============================================================================
import matplotlib.pyplot as plt

# Ouverture du corpus annoté
relations_annoted = []

with open('corpus/debug_annote.txt', 'r') as content_file:
    for line in content_file:
        corpus_annote = line.strip().split(',')
        relations_annoted.append({corpus_annote[0].lower(): \
                                  [corpus_annote[1],\
                                   corpus_annote[2].lower()]})

# exist_relation(relations, match_charac, match_charac_2\
#                                    , c)
        
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
            

cardinal_relations_annoted = len(relations_annoted)


start_k = 1
stop_k = 15
n = (stop_k - start_k) + 1

recall = np.empty(n)
accuracy = np.empty(n)

start = 0

for k in range(start_k, stop_k + 1):
    relations = start_analyze_relationships(doc, characters, k)
    
    m = match_between_relations(relations, relations_annoted)
    
    recall[start] = (m / cardinal_relations_annoted)
    accuracy[start] = (m / len(relations))
    
    start += 1
    
plt.clf()
plt.grid()

plt.xlabel("Précision")
plt.ylabel("Rappel")

plt.plot(recall, accuracy, "kx-")
plt.show()

#    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#            token.shape_, token.is_alpha, token.is_stop, token.ent_type_)
#print(doc._.coref_clusters)
    
#print(doc._.has_coref)
#print(doc._.coref_clusters)
#print(doc._.coref_resolved)
#
#print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
#print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "PERSON"])
#
## Find named entities, phrases and concepts
#for entity in doc.ents:
#    if entity.label_ == "PERSON":
#        print(entity.text, entity.label_, entity.start_char)