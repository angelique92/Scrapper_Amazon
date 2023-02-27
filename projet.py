# Angélique Delevingne
# M1 Informatique
# 19000955

#FICHIERS IMPORT
import visualisation

import math
import pandas as pd
import spacy
import string
import re
import matplotlib.pyplot as plt
import numpy as np


# Scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neural_network import MLPClassifier



# Lecture de fichier amazonData.csv
# Renvoie le dataframe ayant les sentiment et le dataframe ayant les commentaire
def lecture_fichier(nomfichier) : 
    data = pd.read_csv(nomfichier, sep=',')
    index_with_nan = data.index[data.isnull().any(axis=1)]
    data.drop(index_with_nan,0, inplace=True)
    sentiment = data['étoile']
    review = data['commentaire']
    return sentiment , review

# Suprimme les element n'ayant pas de commentaire dans le dataframe
def suprimme_element_vide(comment,sentiment):
    for i,elt in enumerate(comment):
        if elt == "" :
            sentiment.pop(i)
            comment.pop(i)
    return comment,sentiment

# Renvoie le commentaire en transformant certains mots par la racine du mot
def lemmatisation(text, nlp):
    comment_lemmatisation=[]
    for comment in text:
        lst=[]
        doc = nlp(comment)
        for token in doc:
            #print(token.text + "-->" + token.lemma_)
            lst.append(token.lemma_)
        comment_lemmatisation.append(' '.join(str(a) for a in lst))
    return comment_lemmatisation

# Nettoyage du commentaire
#Supprime les caractères/mots qui n'influence pas sur le sentiment
def pre_traitement( texte, classe , nlp ,l_stop ):
    comment_pretraitee=[]
    for comment in texte:
        # Suprime la ponctuation et emoji
        new_string=re.sub(r'[^\w\s]', ' ', comment)
        # Suprimme les espaces 
        new_string= new_string.lstrip()
        # Minuscule
        new_string= new_string.lower()
        #Chiffre
        newstring = re.sub(r'[0-9]+', '', new_string)
        # Suprime stopword
        lst=[]
        for token in new_string.split():
            if token.lower() not in l_stop:
                lst.append(token)
        comment_pretraitee.append(' '.join(str(a) for a in lst))
    newcomment,newsentiment=suprimme_element_vide(comment_pretraitee,classe)
    newcomment=lemmatisation(newcomment,nlp)
    return newcomment,newsentiment

# Vectorisation TFID
def fct_tfid(X_train,X_test):
    pipe = make_pipeline(CountVectorizer(), TfidfTransformer())
    pipe.fit(X_train[0])
    feat_train = pipe.transform(X_train[0])
    feat_test = pipe.transform(X_test[0])
    return feat_train,feat_test

# Vectorisation NGRAM
def fct_ngram(X_train,X_test):
    pipe2 = make_pipeline(CountVectorizer(ngram_range=(1, 2)),
                      TfidfTransformer())
    pipe2.fit(X_train[0])
    feat_train2 = pipe2.transform(X_train[0])

    feat_test2 = pipe2.transform(X_test[0])
    return feat_train2,feat_test2

# Méthode d'apprentissage Forest
def forest(feat_train,y_train,feat_test,y_test):
    clf = RandomForestClassifier(n_estimators=50)
    clf.fit(feat_train, y_train)
    resultat=clf.score(feat_test, y_test)
    print("\tTAUX DE CLASSIFICATION POUR FOREST :  ", resultat*100, "%")
    return resultat*100

# Méthode d'apprentissage Desicion Tree
def desiciontree(feat_train,y_train,feat_test,y_test):
    dt = DecisionTreeClassifier()
    dt.fit(feat_train, y_train)
    resultat=dt.score(feat_test, y_test)
    print("\tTAUX DE CLASSIFICATION POUR DecisionTreeClassifier :  ", resultat*100, "%")
    return resultat*100

# Méthode d'apprentissage CNN
def cnn(feat_train,y_train,feat_test,y_test):
    clf = MLPClassifier( random_state=1)
    clf.fit(feat_train, y_train)
    resultat=clf.score(feat_test, y_test)
    print("\tTAUX DE CLASSIFICATION POUR CNN :  ", resultat*100, "%")
    return resultat*100

def analyse_sentiment(file, nlp, l_stop ):
    print("> Lecture du fichier")
    classe , commentaire = lecture_fichier(file)
    print("> Pré-traitement du texte")
    newcomment,newsentiment= pre_traitement(commentaire,classe,nlp, l_stop)

    # List to DF
    dfcomment = pd.DataFrame(newcomment)

    #TRANDFORME LES ETOILES
    newsentiment.replace(to_replace = 1, value = 0, inplace=True)
    newsentiment.replace(to_replace = 2, value = 0, inplace=True)
    newsentiment.replace(to_replace = 3, value = 1, inplace=True)
    newsentiment.replace(to_replace = 4, value = 2, inplace=True)
    newsentiment.replace(to_replace = 5, value = 2, inplace=True)


    # print(newsentiment)


    print("> Répartition des avis en fonction des étoiles")
    print(newsentiment.value_counts())

    print("\n> Séparation test et train ")
    X_train, X_test, y_train, y_test = train_test_split(dfcomment, newsentiment, random_state=42)
    
    print("\n> Vectorisation des commentaires en TFID et ensuite en NGRAM")
    feat_train_tfid,feat_test_tfid= fct_tfid(X_train,X_test)
    feat_train_ngram,feat_test_ngram=fct_ngram(X_train,X_test)
   
    print("\n> Apprentissage avec la vectorisation : TFID ")
    res_TFID_F=forest(feat_train_tfid,y_train,feat_test_tfid,y_test)
    res_TFID_D=desiciontree(feat_train_tfid,y_train,feat_test_tfid,y_test)
    res_TFID_C=cnn(feat_train_tfid,y_train,feat_test_tfid,y_test)
    

    print("\n> Apprentissage avec la vectorisation : NGRAM ")
    res_NGRAM_F=forest(feat_train_ngram,y_train,feat_test_ngram,y_test)
    res_NGRAM_D=desiciontree(feat_train_ngram,y_train,feat_test_ngram,y_test)
    res_NGRAM_C=cnn(feat_train_ngram,y_train,feat_test_ngram,y_test)


    FOREST=[res_TFID_F,res_NGRAM_F]
    DESICION=[res_TFID_D,res_NGRAM_D]
    CNN=[res_TFID_C,res_NGRAM_C]

    visualisation.diagramme(FOREST,DESICION,CNN)



if __name__ == '__main__':
    nlpfr = spacy.load("fr_core_news_sm")
    from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
    
    analyse_sentiment("amazonData.csv", nlpfr, fr_stop)

   