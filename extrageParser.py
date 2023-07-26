import sqlite3
from datetime import date
import requests

response = requests.get('https://mercury.extra.ge/categories?requestId=88723e07-3fd1-4cf2-3fe5-af69ed406f3f')
response.json()['data']

original_slugs = {}
for i in response.json()['data']:
    original_slugs[i['id']] = [i['caption'],i['originalSlug']]


import requests
from tqdm import tqdm

progress_bar = tqdm()
product_ids = []
exist = True
increment = 1
while exist:
    json_data = {
        'brandIds': [],
        'categoryId': 1,
        'modelIds': [],
        'features': {},
        'merchantSlugs': [],
        'sortType': 1,
        'sortBy': 1,
        'pageNumber': increment,
        'pageSize': 100,
    }

    productsreq = requests.post('https://mercury.extra.ge/search/billie-jean',  json=json_data)
    product_ids.extend(productsreq.json()['data'])
    if len(productsreq.json()['data']) ==0:
        exist = False
        break
    increment += 1
    progress_bar.update(1)
    
progress_bar.close()


json_data = product_ids
productsmeta = requests.post('https://mercury.extra.ge/products/gimme', json=json_data)

productsmetajson = productsmeta.json()
len(productsmetajson['data'])




import re
import pandas as pd

def split_camel_case(string):
    words = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', string)
    return '_'.join(words)

myProducts = {}
for i in productsmetajson['data']:
    myProducts[i['id']] = {
        "extraid":i['id'],
        "title":i['title'],
        "productOriginalSlug":i["productOriginalSlug"],
        "categorySlug":i["categorySlug"],
        "sellPrice":i["sellPrice"],
        "monthlyPayment":i["monthlyPayment"],
        "discountPercent":i["discountPercent"],
        "discountedPrice":i["discountedPrice"],
        "discountPeriodStartDate":i["discountPeriodStartDate"],
        "discountPeriodEndDate":i["discountPeriodEndDate"],
        "hasGift":i["hasGift"],
        "sellerName":i["sellerName"],
    }
    
#აქედან იწყება დატაბეიზში ჩაწერა წამოღებული დატის 

import sqlite3
from datetime import date
DBNAME = 'extage.db'

# Connect to the SQLite database sqlite ის შემთხვევაშ მარტივად იქმნება დატაბეიზის ფაილი სქვა ბაზაზე ჩასასწორებელი იქნება ეს ნაწილი 
conn = sqlite3.connect(DBNAME)
cursor = conn.cursor()

#ეს ქვერი ქმნის ცხრილს productsPrices თუ არარსებობს 
queryproductsPrices = '''
    CREATE TABLE IF NOT EXISTS productsPrices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        extraid INTEGER,
        sellPrice REAL,
        discountedPrice REAL
    )
'''
#ეს ქვერი ქმნის ცხრილს products თუ არარსებობს 
queryproducts = '''
    CREATE TABLE IF NOT EXISTS products (
        extraid INTEGER PRIMARY KEY,
        title TEXT,
        productOriginalSlug TEXT,
        categorySlug TEXT,
        sellPrice REAL,
        monthlyPayment REAL,
        discountPercent REAL,
        discountedPrice REAL,
        discountPeriodStartDate TEXT,
        discountPeriodEndDate TEXT,
        hasGift INTEGER,
        sellerName TEXT
    )
'''

querycategory  = '''
    CREATE TABLE IF NOT EXISTS products (
        categoryid INTEGER,
        title TEXT
    )
'''

cursor.execute(queryproducts )
cursor.execute(queryproductsPrices )
cursor.execute(querycategory )

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()


# ამ ნაწილში პროდუქტის სრულ ინფოს ვინახავთ 
# Connect to the SQLite database
conn = sqlite3.connect(DBNAME)
cursor = conn.cursor()


# ამ ქვერით თუ უკვე არის extraid ით ჩანაწერილი განაახლებს და თუ არარის დააინსერთებს
# Define the SQL query to insert the data
query = '''
    INSERT OR REPLACE INTO products ( 
        extraid,
        title,
        productOriginalSlug,
        categorySlug,
        sellPrice,
        monthlyPayment,
        discountPercent,
        discountedPrice,
        discountPeriodStartDate,
        discountPeriodEndDate,
        hasGift,
        sellerName
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

#აქ პროდუქტის სრულ ინფოს შევინახავთ ბოლო მონაცემებით
for i in myProducts:
    data = myProducts[i]
# Execute the SQL query with the data
    cursor.execute(query, (
        data['extraid'],
        data['title'],
        data['productOriginalSlug'],
        data['categorySlug'],
        data['sellPrice'],
        data['monthlyPayment'],
        data['discountPercent'],
        data['discountedPrice'],
        data['discountPeriodStartDate'],
        data['discountPeriodEndDate'],
        data['hasGift'],
        data['sellerName']
    ))
    
    
# Commit the changes to the database
conn.commit()
# Close the database connection
conn.close()
