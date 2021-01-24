import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from lxml import html
import json
import re
from re import sub
from decimal import Decimal
import csv

# regex formatting to get Calculate total Bond
regex = re.compile('Bond:\ \$[0-9]*.[0-9]*')
regex_money = re.compile('\$[0-9]*.[0-9]*')
regex_num = re.compile('[0-9]*.[0-9]*')


# obtain the total count of inmates
count_url = "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=count"
uClient = uReq(count_url)
count_html = uClient.read()
uClient.close()
total_count = soup(count_html, "html.parser")
print("Total Inmate Count:", total_count )

# to state details of inmates
inmates = {}
inmate_ID_list = []
page = 0
y = []
# Iterate through the pages of inmates and get all the inmate IDs
while(len(y)>0 or page == 0): # increase the page count
    page = page + 1
    inmate_ID = "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=list&Page=" + str(page)
    uClient = uReq(inmate_ID)
    inmate_ID = uClient.read()
    uClient.close()
    y = json.loads(soup(inmate_ID, "html.parser").prettify())
    for i in y:
        inmate_ID_list.append(i['ID_Number'].strip() )
        for k in range(10):
            del i[str(k)]
        del i['RowNum']
        del i['Name_Suffix']
        inmates[i['ID_Number'].strip()] = i
print("Total Count of ID Numbers Obtained:", len(inmate_ID_list))
print("# of Pages of inmates on website:", page)


bond_count = 0
bondable_count = 0
# iterate through inmate cards with the inmate IDs and store in inmates dict
for inmate_ID in inmate_ID_list:
    my_url ='https://services.co.jackson.ms.us/jaildocket/inmate/_inmatedetails.php?id='+ inmate_ID
    # opening up connection, grapping the page
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    # Obtain inmate details (race, height, ... whether they are bondable )
    container = page_soup.select("[class~=iltext] p")
    name = []
    bondable = "No"
    for i in container:
        item = ' '.join(i.string.split())
        if item == 'Bondable':
            bondable_count = bondable_count +1
            bondable = "Yes"
        name.append(item)

    # Obtain their offense charge and bond amount
    container = page_soup.select("[class~=offenseItem] p")
    offense = []
    for i in container:
        item = ' '.join(i.string.split())
        offense.append(item)

    # Calculate the total bond amount for the inmate
    total = 0
    bonds = regex_money.findall(str(regex.findall(str(offense))))
    for b in bonds:
        total = total + Decimal(sub(r'[^\d.]', '', b))

    # Store all values in dictionary for the inmate
    inmates[inmate_ID]["Total Bond($)"] = total
    inmates[inmate_ID]["Bondable?"] = bondable
    inmates[inmate_ID]["inmate_info"] = name
    inmates[inmate_ID]["inmate_offense"] = offense

    # Calculate the amount of inmates that are Bondable
    if inmates[inmate_ID]["Total Bond($)"]>0:  bond_count = bond_count + 1


print("# of inmates with bond:", bond_count)
print("# of inmates that are bondable:", bondable_count)

# Store Values in CSV
csv_columns = list(list(inmates.values())[0].keys())
dict_data = list(inmates.values())
csv_file = "Jackson_inmates.csv"

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error")

csvfile.close()
