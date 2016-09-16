import sys
import os
import time
import ConfigParser
import logging
import json
import urlparse
#Web scraping
from bs4 import BeautifulSoup
import requests

config = ConfigParser.ConfigParser()
config.read("config.cnf")

#Logging
log_path = config.get('logging', 'log_path')
log = None

category_link_file = config.get('category', 'category_link_file')
product_links_file  = config.get('product', 'products_link_file')
product_data_file = config.get('product', 'product_data_file')

main_category_links = []

class Scrap(object):

    def __init__(self):
        print "Initiating.."

    # Main function to initiate the process
    # i/p - main_url
    # o/p - product data
    def main(self, main_url):
        try:
            if(main_url):
                page_content = self.parse_url(main_url)
                if(page_content):
                    print "Getting Category Link .."
                    self.get_category(page_content)                    
                    if(os.stat(category_link_file).st_size != 0):
                        print "Getting Products links.."
                        self.get_products_link(category_link_file)
                        if(os.stat(product_links_file).st_size != 0):
                            print "Getting Products data.."
                            self.get_products(product_links_file)
                            if(os.stat(product_data_file).st_size != 0):
                                print "Products Parsed Succssfully"
                                return 1
                            else:
                                print "product data is empty"
                                return 0
                        else:
                            print "products links are empty"
                            return 0
                    else:
                        print "category links are empty"
                        return 0
                else:
                    print "Page content in empty"
                    return 0
            else:
                print "main_url is empty"
                return 0
        except Exception as e:
            print(e)
            return 0
    
    #Parse the page
    #i/p - url
    #o/p - page_content         
    def parse_url(self,url):
        try:        
            if(url):
                page_content = ""
                print("Parse the page - "+str(url))
                response = requests.get(url)
                if(response.status_code == 200):
                    print("Response received")
                    page_content = response.text
                    return page_content
                else:
                    print("Data retrieval failed. Received responsed from the web page: " + str(response.status_code))
                    return 0
            else:
                print "url is empty"
                return 0
        except Exception as e:
            print(e)
            return 0

    #Get Main Getgory url's from menu
    #i/p - main page_content
    #o/p - category links 
    def get_category(self, page_content):
        try:
            if(page_content):
                soup = BeautifulSoup(page_content, "html5lib")
                category_link = soup.findAll("a", {"class": "main-nav1"})                
                for links in category_link:               
                    if links.get('href') != '' and  links.get('href') != 'javascript:void(0)':
                        main_category_links.append(links.get('href'))
                        with open(category_link_file, "a") as myfile:
                            myfile.write(links.get('href'))  
                            myfile.write("\n")    

                return main_category_links  
            else:
                print "No Category Found" 
                return 0
        except Exception as e:
            print(e)
            return 0

    #Get the Product link from each category url
    #i/p - category links
    #o/p - product page links
    def get_products_link(self, link_file):
        try:
            if(link_file):                
                for link in open(link_file):
                    pages = []                    
                    page_content = self.parse_url(link.strip())
                    if(page_content):
                        soup = BeautifulSoup(page_content, "html5lib")

                        # Get The Pagination link if product catogory have 1 or more pagination
                        paginations = soup.findAll('div',{'class','pagination'})
                        if(paginations):                    
                            page_links = paginations[0].findAll('a')
                            for page_link in page_links:
                                if page_link.get('href') != '' and  page_link.get('href') is not None:
                                    pages.append(page_link.get('href'))
                            pages = list(set(pages))
                            
                            # Parse the each pagination link
                            for page_link in pages:                          
                                page_content = self.parse_url(page_link)
                                if(page_content):                                
                                    soup = BeautifulSoup(page_content, "html5lib")
                                    product_links = soup.findAll("div",{"class","product-name"})
                    
                                    if(product_links):
                                        for product_link in product_links:                                            
                                            with open(product_links_file, "a") as myfile:
                                                myfile.write(product_link.find('a').get('href'))
                                                myfile.write("\n")
                                            
                                            #print product_links_data
                        else:
                            product_links = soup.findAll("div",{"class","product-name"})
                            for product_link in product_links:
                                with open(product_links_file, "a") as myfile:
                                    myfile.write(product_link.find('a').get('href'))
                                    myfile.write("\n")

                        time.sleep(60)
                if(product_links_data):
                    return product_links_data
                else:
                    print "Product Link is empty"
                    return 0
        except Exception as e:
            print(e)
            return 0
    
    #Get the Product Data from each product page url
    #i/p - product page links
    #o/p - product data as json
    def get_products(self, link_file):
        try:
            products = []
            if(link_file):
                for link in open(link_file):
                    page_content = self.parse_url(link.strip())
                    if(page_content):
                        data = {}
                        soup = BeautifulSoup(page_content, "html5lib")
                        product_sku = soup.find('div',{'class','pdt-skuid'})
                        if(product_sku):
                            sku = product_sku.text.split(":")[1].strip()
                            data[sku] = {}
                        product_data = soup.find('table',{'class','data-table'})

                        if(product_data):
                            product_data = product_data.findAll('td')
                            if(product_data):
                                for index, val in enumerate(product_data): 
                                    if index%2 == 0:
                                        if(val):
                                            data[sku][val.text.strip()] = product_data[index+1].text.strip()        
                                if(data):
                                    products.append(data)                                                                       

                if(products):
                    with open(product_data_file, "a") as myfile:
                        myfile.write(json.dumps(products))

                    return 1
                else:
                    print "No Products found"
                    return 0
                time.sleep(60)
            else:
                print "Product links is empty"
                return 0
        except Exception as e:
            print(e)
            return 0

Scrap().main(sys.argv[1])
