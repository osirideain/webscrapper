import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
import pyperclip
import re
import pprint
from collections import OrderedDict
import xlsxwriter
import time

url = 'https://www.alza.cz/'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'lxml')

def firstLinks():
        list = []
        links = soup.find_all('a', class_ = 'l0-catLink', href=True)
        for link in links:
                website = link['href']
                list.append('https://www.alza.cz/EN'+ website)
        return list

def secondLinks():
        urls = firstLinks()
        list = []
        for url in urls:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'lxml')
                links = soup.find_all('a', class_ = 'subC', href=True)
                for link in links:
                        website = link['href']
                        list.append('https://www.alza.cz'+ website)
        return list

def pages():
        new_urls = secondLinks()
        list = []
        for link in new_urls:
                for page in range(1):
                        list.append(link.replace('.htm', '-p'+ str(page)+'.htm'))
        return list


def items():
        htms = pages()
        list = []
        for url in htms:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'lxml')
                links = soup.find_all('div', class_ = 'bi js-block-image')
                for link in links:
                        website = link.find('a', class_ = 'pc browsinglink', href=True)
                        list.append('https://www.alza.cz'+ website['href'])
        return list


workbook = xlsxwriter.Workbook("Alza_Products.xlsx")
worksheet_products = workbook.add_worksheet('Products')
infos = items()

Products = []
Images = []
Deals = []
Pricings = []
Originals = []
Links = []
Names = ['Names','Images','Deals Discounts','Deals Original Prices' , 'Prices', 'Original Prices', 'Links']
for url in infos:
        Deals_original = []
        def deals_original_prices():
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'lxml')
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)

                session.get(url)
                
                prices = soup.find('tr', class_ = 'priceCompare')
                price = prices.find('td', class_ = 'c2')
                try:
                        return price.text.strip()
                except AttributeError:
                        return ''
        Deals_original.append(deals_original_prices())
        
for url in infos:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text,'lxml')
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.get(url)

        product = soup.find('h1').text.strip()
        Products.append(product)

        def images():
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            image = soup.find('img', id = 'imgMain')
            try:
                return image['src']
            except TypeError:
                return ''

        Images.append(images())
        
        def deals_discounts():
##                prices = soup.find('tr', class_ = 'pricenormal')
                price = soup.find('td', class_ = 'c2')
                try:
                        return price.text.strip()
                except AttributeError:
                        return ''
        Deals.append(deals_discounts())

        def pricing():
                price = soup.find('span', class_ = 'price_withVat')
                try:
                        return price.text
                except AttributeError:
                        return ''
        Pricings.append(pricing())

        
        def original():
                list = []
                original_price = soup.find('span', class_ = 'crossPrice price_compare')
                try:
                        return original_price.text
                except AttributeError:
                        return ''
        Originals.append(original())


        def link():
                list = []
                link = soup.find('meta', property = 'og:url')
                try:
                        return link['content']
                except TypeError:
                        return ''
        Links.append(link())



worksheet_products.write_row(0,0,Names)
worksheet_products.write_column(1,0,Products)
worksheet_products.write_column(1,1,Images)
worksheet_products.write_column(1,2,Deals)
worksheet_products.write_column(1,3,Deals_original)
worksheet_products.write_column(1,4,Pricings)
worksheet_products.write_column(1,5,Originals)
worksheet_products.write_column(1,6,Links)

workbook.close()
