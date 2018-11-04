# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 10:56:24 2018
@author: srodriguezl

Functions to extract information from tripadvisor restaurants.
Input: namecity
       number of pages you want to check
Output: dataframe with restaurants information(name,rating, number of reviews, price category,...)

Example:
dfout = crawl_restaurant_tripadvisor(nameCity="Málaga")

"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

def crawl_restaurant_tripadvisor(nameCity, max_num_pages=100):
    #  we are initializing "FireFox" by making an object of it
    driver = webdriver.Firefox()
    driver.get("https://www.tripadvisor.es/Restaurants")
    
    # Fill box with city name
    nameRestaurant = driver.find_element_by_class_name("typeahead_input")
    nameRestaurant.clear()
    nameRestaurant.send_keys(nameCity)
    nameRestaurant.send_keys(Keys.RETURN)
    
    # Initialize dataframe
    df = pd.DataFrame([])    
    
    for i in range(1,(max_num_pages+1)):
           
        # number of page your are exploring
        print(i)
        
        # sometimes website takes long time to reload and you scrape the old page
        # Check that the number of the page is different from the page you have previously analyze    
        old_page = True
        while old_page:
            try:
                if(int(driver.find_element_by_class_name("pageNum.current").text) == i):
                    old_page = False
            except:
                pass

        # scrape info and save
        html_txt = driver.page_source
        df = df.append(parse_restaurant_tripadvisor(html_txt,nameCity))    
    
        # A small box sometimes appears at the bottom of the web page, and it hides the next button
        if(driver.find_elements_by_xpath("/html/body/div[10]/div[8]/div")):
            question = driver.find_element_by_xpath("/html/body/div[10]/div[8]/div") 
            question.click()
         
        # go to the bottom of the webpage (to avoid a new popup box hide the button)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
       
        # Check the page is the last one
        if not driver.find_elements_by_class_name('nav.next.rndBtn.ui_button.primary.taLnk'):
            break
        
         # click next page
        nextPage = driver.find_element_by_class_name('nav.next.rndBtn.ui_button.primary.taLnk')
        nextPage.click()
        
    
    
    df = df.reset_index(drop=True)
    driver.close()
    return(df)

from bs4 import BeautifulSoup

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