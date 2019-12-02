# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 15:52:19 2019

@author: jonat
"""

import spacy
import re


print("Chargement du modèle...")
nlp = spacy.load('en_core_web_md')

#import neuralcoref
#neuralcoref.add_to_pipe(nlp)


print("Ouverture et lecture du contenu en mode read only...")

cat = {}
# Ouverture du fichier qui contient les catégories de relations possibles
with open('relations_properties.txt', 'r') as content_file:
    for line in content_file:
        content = line.strip().split(':')
        cat[content[0]] = content[1].strip().split()
    
# Ouverture du corpus
with open('corpus/debug.txt', 'r') as content_file:
    corpus = content_file.read().strip()

print("Analyse du texte en cours...")    
doc = nlp(corpus)
print("Analyse terminée.")

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
                #print(entity, entity.text, entity.label_, entity.start_char)  
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

        if token.pos_ != "PUNCT" and re.match(token.text.lower(), chara) is not None:
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
                if match_charac_2 is not None:
                    relations.append({match_charac: [c, match_charac_2]})
                    break
            break
        

# Liste des personnages
characters = extract_characters(doc)

# relations = ['Personnage1': {lien de la relation, Personnage2}]
relations = []
stop_iteration = 5
start = 0
for token in doc:
    start += 1
    match_charac = match_character(token, characters)
    if match_charac is None:
        continue
    
    extract_relation(relations, cat, doc, characters, match_charac, start, stop_iteration)
    
print(relations)
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