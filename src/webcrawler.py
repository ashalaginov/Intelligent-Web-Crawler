# WebCrawler

import os
from dotenv import load_dotenv
import bs4 as bs
import re
import urllib.request
import random
import time
import mysql.connector
from mysql.connector import Error

__author__ = "Andrii Shalaginov"
__date__ = "$03.okt.2020 13:34:19$"

# Loading credentials - excluded from Git repository
load_dotenv()
MYSQL_HOST_NAME = os.getenv("MYSQL_HOST_NAME")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# Crawler config
FLAG_CATEGORIES_COLLECTION = 1  # to prevent categories crawler from running
FLAG_PRODUCTS_COLLECTION = 1  # to prevent products crawler from running
DOMAIN_NAME = "https://WEBSITE" # domain name to explore
debug_total_urls = 0; # count number of urls
HTTPerror = 0;

### Functions ###
def categories_crawler(categories_urls, categories_names):
    tmp_categories_urls = {}  # "url: parent url"
    tmp_categories_names = categories_names  # "url: name"
    tmp_count = 0 # number of newly added categories that the crawler has not seen before
    global DOMAIN_NAME
    global debug_total_urls
    global HTTPerror
    for current_url in categories_urls.keys():
        # Check if the page already been visited - in category names
        if current_url not in tmp_categories_names.keys():
            
            try:
                time.sleep(random.randint(0, 100) / 1000) # time to get a webpage from WEBSITE - under 100 msec
                # Get rendered HTML webape
                source = urllib.request.urlopen(DOMAIN_NAME + current_url).read()
                debug_total_urls += 1
            except urllib.error.HTTPError as e:
                # Return code error (e.g. 404, 501, ...)
                HTTPerror += 1
            else:          
                # make BS object and use HTML parser - faster
                soup = bs.BeautifulSoup(source, "lxml")

                # Name of the category - getting from last element of breadcrumb - universal accross categories/sub-categories
                category_name = (
                                 soup.find_all("div", class_="product-category-header")[0]
                                 .find_all(attrs={"itemprop": "title"})[-1]
                                 .string
                                 )
                # Find parent link - usefull to determine partent category/subcategory
                parent_link = (
                               soup.find_all("li", class_="parent-category active")[0]
                               .select("h4 > a", class_="aggregation-filter-headline")[0]
                               .get("href")
                               )
                tmp_categories_names[current_url] = category_name

                # Collect any relevant URLs that were found on the webpage - only categories
                for links in soup.find_all("a", href=re.compile("kategorier")):
                    if any(map(str.isdigit, str(links))):
                        link = links.get("href")
                        if link not in tmp_categories_urls.keys():
                            # A check for categories - three slashes and subcategories - sub-slashes
                            if (link.count("/")) == 4:
                                tmp_categories_urls[link] = parent_link
                            else:
                                tmp_categories_urls[link] = "/kategorier"
                            tmp_count += 1

    tmp_categories_urls.update(categories_urls)
    tmp_categories_names.update(categories_names)

    return tmp_count, tmp_categories_urls, tmp_categories_names


def products_crawler(categories_urls):
    products = [] # new products in format (url, name, price, sub-category)
    tmp_count = 0
    tmp_id=0
    global debug_total_urls
    global HTTPerror
    for result in categories_urls:
        print("Processing category ID " + str(tmp_id) + "; URL: " + result[0])
        tmp_id+=1
        i=0
        while i<10:
            # Each category might have multiple pages with products
            current_url = DOMAIN_NAME + result[0] + "?page=" + str(i) 

            try:
                time.sleep(random.randint(0, 100) / 1000) # time to get a webpage from WEBSITE - under 100 msec 
                source = urllib.request.urlopen(current_url)
                debug_total_urls += 1
            except urllib.error.HTTPError as e:
                # Return code error (e.g. 404, 501, ...)
                HTTPerror += 1
                i=10
            else:
                # 200
                i+=1
                source = source.read()
                soup = bs.BeautifulSoup(source, "lxml")
                # Find a product block on the web page
                for product in soup.find_all("div", class_="product-list-item"):
                    tmp_count += 1
                    # Extracting name
                    name = product.find_all("div", class_="name-main wrap-two-lines")[
                        0
                    ].string
                    
                    # Sometimes discounted prices are printed along with the regular one
                    if (
                        len(product.find_all("p", class_="price label label-price"))
                        == 1
                        ):
                        price = (
                                 product.find_all("p", class_="price label label-price")[0]
                                 .string.replace("kr", "")
                                 .replace(",", ".")
                                 .strip()
                                 )
                    elif (
                          len(
                          product.find_all(
                          "p", class_="price label label-price-discounted"
                          )
                          )
                          == 1
                          ):
                        body = product.find(
                                            "p", class_="price label label-price-discounted"
                                            )
                        price = (
                                 product.find(
                                 "p", class_="price label label-price-discounted"
                                 )
                                 .find("span", class_="undiscounted-price")
                                 .next_sibling.string.replace("kr", "")
                                 .replace(",", ".")
                                 .strip()
                                 )
                        
                    url = product.select("a", class_="modal-link")[0].get("href")
                    product = (url, name, price, result[0])
                    products.append(product)

    return tmp_count,products


########################################################################
# Crawler config
start_url = "/kategorier"
categories_urls = {}  # "url: parent url"
categories_names = {}  # "url: name"


# MySQL
try:
    mydb = mysql.connector.connect(
                                   host=MYSQL_HOST_NAME,
                                   database=MYSQL_DB,
                                   user=MYSQL_USER,
                                   password=MYSQL_PASSWORD,
                                   auth_plugin="mysql_native_password",
                                   )

    if mydb.is_connected():
        db_Info = mydb.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        mycursor = mydb.cursor()
        mycursor.execute("select database();")
        record = mycursor.fetchone()
        print("You're connected to database: ", record)
except Error as e:
    print("Error while connecting to MySQL", e)
    exit


####################CATEGORIES##########################################
if FLAG_CATEGORIES_COLLECTION == 1:
    print("Starting processing categories on the website \n")
    start_general = time.time()
    # Crawling around website until no new categories discovered or more than 10 iterations
    i = 0
    count = 1
    categories_urls[start_url] = start_url
    while i < 10 and count > 0:
        start_time = time.time()
        # Collection of all categories/subcategories
        count, categories_urls, categories_names = categories_crawler(
                                                                      categories_urls, categories_names
                                                                      )

        print("Interation id: " + str(i))
        print("Total new URLs per iteration count: " + str(count))
        print(
              "Current number of collected URLs to process: " + str(len(categories_urls))
              )
        print("Number of processed unique URLs: " + str(len(categories_names)))
        print("Elapsed: --- %s seconds ---" % (time.time() - start_time))
        print("\n")
        start_time = time.time()
        i += 1

        
    # Delete the main category 
    del categories_urls[start_url]
    del categories_names[start_url]

    print("All categories have been processed...writing to MySQL \n")
    query_array = []
    for current_url in categories_urls.keys():
        query = (
                 current_url,
                 categories_names[current_url],
                 categories_urls[current_url],
                 )
        query_array.append(query)
    sql = "INSERT IGNORE INTO categories (url,name,parent) VALUES (%s, %s, %s)"
    mycursor.executemany(sql, query_array)
    mydb.commit()   
    print("Crawling categories took : --- %s seconds ---" % (time.time() - start_general))
    print("DONE (visited URLs):" + str(debug_total_urls) + "\n")



###################PRODUCTS#############################################
if FLAG_PRODUCTS_COLLECTION == 1:
    start_time = time.time()
    print("Starting processing products on the website \n")
    # Select all subcategories and subsequent
    mycursor.execute("SELECT url FROM categories WHERE parent<>'" + start_url + "'") # excluding parent category
    # CHECK if more product on general webpage
    myresult = mycursor.fetchall()
    count = len(myresult)
    print("\n--- There are total " + str(count) + " categories to check ---\n")

    count,products = products_crawler(myresult)

    print("All products have been processed...writing to MySQL \n")
    sql = "INSERT IGNORE INTO products (url,name,price,category_url) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, products)
    mydb.commit()
    print("\n--- There are total " + str(count) + " products found ---\n")

    print("Crawling products took : --- %s seconds ---" % (time.time() - start_general))
    print("DONE (visited URLs):" + str(debug_total_urls) + "\n")
    print("\n Total number of 404 URLs: \n"+str(HTTPerror))

