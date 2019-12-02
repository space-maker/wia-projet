# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 15:52:19 2019

@author: jonat
"""

import spacy


nlp = spacy.load('en_core_web_sm')

#import neuralcoref
#neuralcoref.add_to_pipe(nlp)

print("Ouverture et lecture du contenu en mode read only")

with open('corpus/exemple1.txt', 'r') as content_file:
    content = content_file.read()

print("Analyse du texte en cours...")    
doc = nlp("San Francisco considers banning sidewalk delivery robots 5% French to b. You are beautiful")
print("Analyse terminée")

#if doc._.has_coref == True:
#    print("Coréférences trouvées")
#else:
#    print("Coréférences non-trouvées")
    
print()
for entity in doc.ents:
    print(entity.text, entity.label_, entity.start_char)  
    
print()
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)
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