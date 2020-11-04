## Intelligent Web Crawler
This is a simple implementation of fast and functional Python-based web crawler using Beautiful Soap 4. 

## Description
In one of the interviews for DevSecOps capacity with one of the largest online retailers I have been asked to implement something reliable, portable and without causing much DoS on their servers. The have hundereds of categories and thoughands of products. The crawler too less than a few minutes to crawl and collect information and meta information about categories and products. It includes two functions: (i) general category and sub-category collection and (ii) collection of metadata of products on each sub-category page, including pager awareness if more than one page of the products in that sub-category. All data are being stored in MySQL tables: categories and products.  The crawler prints total number of 404 pages, found sub-categories, products, visited URLs, time performance, etc.

## Anti-DoS protection
The crwaler has randomaized delay functionality (10-100 msec) between fetching webpages and considering low latency to the server. Consider increasing it if the server network bandwidth is limited. You can check it using "wget"

## Metadata collection
While processing pages on retailer website the goal is to locate suitable set of classes, IDs and tags to extract relevant metadata: name, url, etc.

## Configuration
File `.env` contains MySQL connection details and you can exclude it from Git to release only functionality. FLAG_CATEGORIES_COLLECTION and FLAG_PRODUCTS_COLLECTION enable or disable corresponding sub-functions. 

## Files
- src/webcrawler.py - implementation of crawler
- database.sql - MySQL scheme of two tables: categories and products
- requirements.txt - required Python modules
- setup.py - setup script for this crawler
- .env - configuration (can be excluded if you need to keep credentials private)


## Installation
In case if you want to install it and use later, just execute:

```bash
# Install requirements
$ pip3 install -r requirements.txt

# Install WebCraler module
python3 setup.py install
```

## Software Requirements
- Python v. 3.8.5 
- Python modules: mysql, mysql-connector, beautifulsoup4 v. 4.8.2, re, urllib, time,random, dotenv. (complete list - requirements.txt)
- MySQL v. 8.0.22
