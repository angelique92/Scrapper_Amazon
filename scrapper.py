from bs4 import BeautifulSoup
from googletrans import Translator
import csv
import re
import requests
import argparse


#Liste contenant un tupple des commentaires avec le nombre d'étoile associé
global liste_comment_class
liste_comment_class=[]


# Recherche Amazon 
def url_recherche_amazon(search_term):
    template='https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term=search_term.replace(' ', '+')

    url=template.format(search_term)

    url+='&page{}'
    return url

# Recherche le lien de tous les produits vendus
def recupere_lien_all_produit( url ):
    #Chargement de Page
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    page = requests.get(url, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
    liste_lien=[]
    #print(soup1, soup2)
    try:
        review=soup2.find_all('div' , { 'data-component-type' : "s-search-result" }) 
        try:
            for elt in review :
                # Recherche le lien d'un produit
                try:
                    a = elt.find('a')
                    try:
                        if 'href' in a.attrs:

                            url = a.get('href')
                            url= "https://www.amazon.fr/" + url
                            liste_lien.append(url)
                    except:
                        print("pas de balise href --> Recherche le lien d'un produit")
                except: 
                    print("pas de balise a --> Recherche le lien d'un produit")
            
        except:
            print("Balise pas trouvé  ! ---> Review ")
    except:
        print("Page pas charger")
    
    print("\t > Nombre de produits trouvés: ", len(liste_lien))
    
    return liste_lien


# Renvoie le lien des commentaire pour un produit 
def recupere_lien_comment (url): 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    page = requests.get(url, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")

    soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
    try:
        
        for h in soup2.findAll('div', {"id":"cr-pagination-footer-0"}):
            try:
                a = h.find('a')
                try:
                    if 'href' in a.attrs:

                        url = a.get('href')
                        url= "https://www.amazon.fr/" + url
                        #print("\nLien qui dirige vers les commentaires :",url , " \n")

                        return url

                except:
                    print("Balise pas trouvé  !  <a>")
            except:
                print("Balise pas trouvé  !  <div { id:cr-pagination-footer-0 } >")
    except:
        print("Page pas charger")



# Fonction qui charge une page et récolte les commentaires et les étoiles
def charge_Comment_Class_Page(url, nb_comment):
    #Chargement de Page
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    page = requests.get(url, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
    global liste_comment_class
    try:
        #Balise contenant la liste de tous les commentaires de la pages
        reviews = soup1.find_all('div', {'data-hook': 'review'})
        try:
            for elt in reviews:
                etranger=0
                try:
                    #Recherche la balise étoile
                    etoile= elt.find('i', {'data-hook': 'review-star-rating'}).text[0]
                except:
                    #Recherche de l'étoile étranger -> Commentaire sera étranger
                    etoile= elt.find('i', {'data-hook': 'cmps-review-star-rating'}).text[0]
                    etranger=1
                #print(etoile)
                try:
                    #Recherche la balise commentaire
                    comment= elt.find('span', {'data-hook': 'review-body'}).text.strip()
                except:
                    print("Pas trouver la balise comment")
                #print(comment)
                
                #Traduction des commentaires étrangers en français
                if etranger == 1:
                    translator = Translator()
                    translated_text = translator.translate(comment, dest='fr')
                    comment=translated_text.text
                    etranger=0

                if len(liste_comment_class) < nb_comment:
                    liste_comment_class.append((etoile, comment))
                    print("Ajout de commentaire  / taille de la liste des commentaire > ", len(liste_comment_class))
                    
                else: 
                    break

        except:
            print("Ne trouve pas la balise review")
            pass
        
    except:
        print("Ne lis pas la page")
        pass
        

# Parcours différentes page de commentaires : 
def recupere_comment( url , nb_comment):

    global liste_comment_class
    # Parcours différentes page de commentaires : 
    print("URL : ",url)
    nb_pages= 10000  #Nombre de pages à balayer
    #url_general = re.sub('/ref=', '', url)
    pos1 = url.find('/ref=') 
    url_general=url[: pos1]
    # url=url_general + "/ref=cm_cr_arp_d_paging_btm_"+ str(2) +"?ie=UTF8&pageNumber="+ str(2) +"&reviewerType=all_reviews"
    # print("url_general : ", url_general)
    # print("url :", url)
    #print("url_general : ",url_general)
    taille_max = len(liste_comment_class) + nb_comment
    # while taille_max > len(liste_comment_class):
    for i in range(1,nb_pages):
        if taille_max > len(liste_comment_class):
            url=url_general + "/ref=cm_cr_arp_d_paging_btm_"+ str(i) +"?ie=UTF8&pageNumber="+ str(i) +"&reviewerType=all_reviews"
            print("Page ",i, " des commentaires :",url)
            avanttaille=len(liste_comment_class)
            charge_Comment_Class_Page(url , taille_max)
            aprestaille=len(liste_comment_class)
            if aprestaille == avanttaille:
                break
        else:
            break

#Préparation du fichier CSV 
def dataset_csv ( ):
    global liste_comment_class
    with open('amazonDataset.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        
        # write the header
        writer.writerow(["étoile", "commentaire"])

        # write the data
        for elt in liste_comment_class:
            writer.writerow(elt)


if __name__ == '__main__':
    # LIS LES ARGUMENTS DE LA LIGNE DE COMMANDE LORS DE L EXÉCUTION >
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--string", type=str, required=True)
    parser.add_argument("nb_produit", type=int, help="nombre de produit")
    parser.add_argument("nb_comment", type=int, help="nombre de commentaire")

    args = parser.parse_args()
    # ASSOCIATION DES PARAMETRES RÉCOLTÉS >
    nom_produit= args.string
    nb_produit=args.nb_produit
    nb_comment= args.nb_comment

    # RECHERCHE DU PRODUIT SUR AMAZON >
    lien =url_recherche_amazon(nom_produit)

    print( " RECHERCHE SUR AMAZON DU PRODUIT < ", nom_produit , "\n\t> URL :",lien )
    print("\n === Chargement de la page et récupération des diférents liens de tous les produits vendus === \n")

    # RECHERCHE LES LIENS DE TOUS LES PRODUITS DE LA PAGE >
    liste_lien = recupere_lien_all_produit(lien )  

    # Suprimme Le premier element n'est pas un produit 
    liste_lien.pop(0)

    # POUR CHAQUE PRODUIT :
        # RECHERCHE DE LA PAGE DE COMMENTAIRE
        # RECOLTAGE DES COMMENTAIRES SUR LES DIFFERENTES PAGES DE COMMENTAIRES >
    print("Chargement des différentes pages de produits - récoltage des commentaires et étoiles assosiées \n")
    
    for count , elt in enumerate(liste_lien):
        if len(liste_comment_class) < nb_comment*nb_produit:
            print("Produit : ", count)
            print("Lien du produit : ", elt)
            lien_comm= recupere_lien_comment(elt)
            if lien_comm != None:
                recupere_comment(lien_comm, nb_comment)
            else:
                print("error : Page pas accessible")
        else:
            break
    
    print("== Chargement des données récoltées dans le fichier amazonDataset.csv == ")
    dataset_csv()

# J'ai installer proxychains pour ne pas me faire bloquer à chaque fois que je scrappe des données sur Amazon
# https://www.grabitgo.com/2022/03/proxychains-not-working-in-ubuntu-step.html
# Avant exécution faire la commande : proxychains bash
# Puis le lancement du programme exemple : python3 scrapper.py --string "tee shrit" 2 10