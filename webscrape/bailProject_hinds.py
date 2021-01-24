import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from lxml import html
import json
import re
from re import sub
from decimal import Decimal
import csv

# to state details of inmates
inmates = {}
count_url = 'http://www.co.hinds.ms.us/pgs/apps/inmate/inmatecount.asp'
uClient = uReq(count_url)
count_html = uClient.read()
uClient.close()

# html parsing
page_soup = soup(count_html, "html.parser")
container = page_soup.select("td")
print(len(container))
for i in range(len(container)-6)[::3]:
    print(container[i].text.strip(), container[i+1].text, container[i+2].text)

# for i in range (2):
my_url ='http://www.co.hinds.ms.us/pgs/apps/inmate/inmate_list.asp?name_sch=&SS1=1&search_by_city=&search_by=&ScrollAction=Page+' + "1"
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html, "html.parser")
container = page_soup.find_all('a', {"class":"Right_Link"})

# # Store Values in CSV
# csv_columns = list(list(inmates.values())[0].keys())
# dict_data = list(inmates.values())
# csv_file = "hinds_inmates.csv"
#
# try:
#     with open(csv_file, 'w') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         writer.writeheader()
#         for data in dict_data:
#             writer.writerow(data)
# except IOError:
#     print("I/O error")
#
# csvfile.close()
