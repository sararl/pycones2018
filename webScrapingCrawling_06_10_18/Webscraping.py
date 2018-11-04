# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 10:32:14 2018
@author: srodriguezl

Functions to extract information from tripadvisor restaurants(one page).
Input: url tripadvisor restaurant
Output: dataframe with restaurants information(name,rating, number of reviews, price category,...)
Example:
dfout = get_tripadvisor(URL = "https://www.tripadvisor.es/Restaurants-g187438-Malaga_Costa_del_Sol_Province_of_Malaga_Andalucia.html")

"""

from bs4 import BeautifulSoup
import pandas as pd
import requests

def get_tripadvisor(URL):
    '''
    Extract html code from url 
    '''
    # Nombre ciudad
    nombreCiudad = URL.split("-")[2].split("_")[0]
    # Conexión
    peticion_restaurantes = requests.get(URL)
    
    # Compruebas conexión ok
    if peticion_restaurantes.status_code == 200:   
        strhtml = peticion_restaurantes.text # is a string that contains the web page source
        df = parse_restaurant_tripadvisor(strhtml,nombreCiudad)
        return(df)
    else:
        return(pd.DataFrame())
    

def parse_restaurant_tripadvisor(strhtml,nombreCiudad):
    
    '''
    Extract restaurants information from html code
    '''
        
    # Objeto beautiful soup
    soup = BeautifulSoup(strhtml,"lxml") 
        
    # creas listas que irás relenando con datos
    name = []
    position = []
    rating = []
    numReview = []
    euros = []
    food = []
        
    # Parseas el código html extrayendo la información de interés
    for sec in soup.find_all("div",class_="shortSellDetails"):
        # Evitas los que son restaurantes patrocinados
        patro = sec.find(class_="ui_merchandising_pill")
        
        if(patro == None):
            # position
            if sec.find("div",class_="popIndex rebrand popIndexDefault") is not None:
                pos = sec.find("div",class_="popIndex rebrand popIndexDefault").get_text(strip=True) # extraccion
                pos = int(pos.split(" de ")[0].replace(".", "")) # tratamiento
            else:
                pos=""
            position.append(pos) # append
            
            # restaurant name
            nam = sec.find("a",class_="property_title").get_text(strip=True) # extraccion
            name.append(nam)
            
            # rating
            if sec.find("span",class_="ui_bubble_rating") is not None:
                rate = sec.find("span",class_="ui_bubble_rating").get("alt") # extraccion
                rate = float(rate.split(" de ")[0].replace(",","."))  # tratamiento
            else:
                rate = 0
            rating.append(rate)
            
            # number or reviews
            if sec.find("span",class_="reviewCount") is not None:
                reviews = sec.find("span",class_="reviewCount").get_text(strip=True) # extraccion
                reviews = int(reviews.replace("opiniones", "").replace("opinión","").replace(".", ""))  # tratamiento
            else:
                reviews = 0
            numReview.append(reviews)
            
            # euroscategory
            if sec.find("span",class_="item price") is not None:
                price = sec.find("span",class_="item price").get_text(strip=True)  
            else:
                price = " "
            euros.append(price)
            
            # food category
            typefood = [secfood.get_text() for secfood in sec.find_all("a",class_="item cuisine")] # extraccion
            typefood = ','.join(typefood) # tratamiento
            food.append(typefood)            
            
            df = pd.DataFrame({'position':position,'restaurants':name,"ratings":rating,
                               "number_reviews":numReview, "price_category":euros,
                              'food_category':food},          
                    columns = ["position","restaurants","ratings","number_reviews","price_category","food_category"])
             
            df.index.name = nombreCiudad
            
    return(df)  