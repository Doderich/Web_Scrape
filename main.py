#Import list
from bs4 import BeautifulSoup # html parsing
import requests # connection to website
import csv # operationg csv files
import os.path # chekc if files exists

URL = 'https://www.wollplatz.de/wolle/?page='
all_product_csv = 'wollplatz.csv'
 
#gesuchte Namen
#query = ['DMC Natura XL',
#        'Drops Safran',
#        'Drops Baby Merino Mix',
#        'Hahn Alpacca Speciale',
#        'Stylecraft Sepcial double knit'
#]

#returns a list of the 
def get_product_info(link_list):
    all_prod = []    
    for link in link_list:
        data = requests.get(link).text
        soup = BeautifulSoup(data, 'html.parser')
        #with soup.find navigate to the place on the page and get the value
        name = soup.find(class_="maintitle-holder").select('h1')[0].text.strip()
        price = soup.find(class_="product-price").select('span')[1].text.strip()
        aval = soup.find(id="ContentPlaceHolder1_upStockInfoDescription").select('span')[0].text.strip()
        needle = soup.find(id="pdetailTableSpecs").select('tr')[4].text.strip()
        comp = soup.find(id="pdetailTableSpecs").select('tr')[3].text.strip()
        #store it in a dictionary
        all_prod.append({
            "name": name,
            "price": price,
            "avalability": aval,
            "needle": needle.replace("Nadelstärke",""), #replace cuts away unnesesary strings
            "composition": comp.replace("Zusammenstellung","")
        })
    return all_prod

#gets the amount of product pages
def get_page_count(url):
    req = requests.get(url + str(1))
    soup = BeautifulSoup(req.text, 'html.parser')
    # the location of the amount
    page_count = soup.find(id='ContentPlaceHolder1_lblPaginaVanTop')
    return int(page_count.select("b")[1].text.strip())

#gets a list of all products of the website with the link to the products page
def get_links(url,num, num2=1):
    all_links = []
    #for every page on the website
    for page in range(num2,num):
        #connection to website
        req = requests.get(url + str(page))
        soup = BeautifulSoup(req.text, 'html.parser')
        # gets every producte on page
        titles = soup.find_all(class_='productlist-title gtm-product-impression')
        #for every product on the website
        for i in range(0,len(titles)):
            all_links.append({
                        'name': titles[i].text.strip(),
                        'link': titles[i].find("a")['href']
            })
        print(page)
    return all_links

#turns a dictonarie into a csv file
def dict_to_csv(links, name):
    keys = links[0].keys()
    with open(name, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(links)

# Searches the names of the products and gives back the link to the products page
def search_csv(filename, query):
    ls = []
    with open(filename, 'r') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            for item in query:
                if item in row[0]:
                    ls.append(row[1])
    return ls

def get_query_from_txt(file):
    ls = []
    f = open(file,'r')
    for line in f:
        ls.append(line.strip())
    f.close()
    return ls




#pulls all products from the website if it doesnt exist yet
if not (os.path.exists(all_product_csv)):
    page_count = get_page_count(URL)
    dict_to_csv(get_links(URL,page_count),all_product_csv)

query = get_query_from_txt("query.txt")
print(query)
links = search_csv(all_product_csv,query)
dict_to_csv(get_product_info(links), 'products.csv')