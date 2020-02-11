import csv
import requests
import psycopg2
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import date

url = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo={geolocation}'

# locations = ["RO","US", "DK", "FR", "IT"]
locations = ["RO"]
connection = None
cursor = None

insert_sql_query = """INSERT INTO data(id, title, description, traffic) VALUES(nextval('data_id_seq'), %s, %s, %s)"""

def init_connections() :
    global connection
    global cursor
    connection = psycopg2.connect(host="localhost", 
        port = 5432, database="google_trends", user="postgres", password="postgres")
    cursor = connection.cursor()

def close_conections():
    cursor.close()
    connection.close()

def collect_data() :
    for location in locations:
        response = requests.get(url.format(geolocation=location))
        save_to_file(response)

def get_file_name() :
    today = date.today()
    return today.strftime("%b%d%Y") + ".xml"

def save_to_file(response):
    root = ET.fromstring(response.text.encode('utf-8'))
    tree = ET.ElementTree(root)
    tree.write(get_file_name())

def parse_file(file_name) :
    infile = open(file_name,"r")
    content = infile.read()
    parse(content)

def parse(content):
    soup = BeautifulSoup(content,'xml')
    titles = soup.find_all('title')
    items = soup.find_all('item')
    for item in items:
        title = item.find('title').get_text()
        item_description = item.find('description').text
        approx_traffic = item.find('ns1:approx_traffic').get_text()
        print(title + " " + approx_traffic)

def save_to_database(file_name):
    init_connections()
    infile = open(file_name,"r")
    content = infile.read()
    soup = BeautifulSoup(content,'xml')
    titles = soup.find_all('title')
    items = soup.find_all('item')
    for item in items:
        title = item.find('title').get_text()
        item_description = item.find('description').text
        approx_traffic = item.find('ns1:approx_traffic').get_text().replace(",","").replace("+","")
        cursor.execute(insert_sql_query,(title, item_description, approx_traffic))

def main():
    # collect_data()
    # parse_file(get_file_name())
    save_to_database(get_file_name())
      
if __name__ == "__main__": 
    main()