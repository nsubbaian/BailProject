import requests
import urllib.request
from bs4 import BeautifulSoup as soup
import pandas as pd

#Goes through all pages of the database to find links to the inmate pages
#Is there a way to do this that doesn't open the first page twice? Especially without rewriting a bunch of code outside the loop
u_Hinds = urllib.request.urlopen('http://www.co.hinds.ms.us/pgs/apps/inmate/inmate_list.asp?name_sch=&SS1=1&search_by_city=&search_by=&ScrollAction=Page+1')
Hinds_html = u_Hinds.read()
u_Hinds.close()
hinds_soup = soup(Hinds_html, "html.parser")

num_pages = int(hinds_soup.h3.get_text().split()[3])
hinds_prefix = "http://www.co.hinds.ms.us/pgs/apps/inmate/inmate_list.asp?name_sch=&SS1=1&search_by_city=&search_by=&ScrollAction=Page+"
inmate_prefix = "http://www.co.hinds.ms.us/pgs/apps/inmate/"
inmate_links = []

name = []
address = []
dob = []
sex = []
race = []
height = []
weight = []
eye_col = []
hair_col = []
arrest_agency = []
arrest_date = []
offense1 = []
offense2 = []
offense3 = []
offense4 = []
pin = []
location = []


#finds links to all inmate pages
for i in range(num_pages):

	u_Hinds = urllib.request.urlopen(hinds_prefix + str(i + 1))
	Hinds_html = u_Hinds.read()
	u_Hinds.close()
	hinds_soup = soup(Hinds_html, "html.parser")

	lin = hinds_soup.find_all("a")

	num_links = len(lin)
	last_link = num_links - 6
	page_links = lin[6:last_link]

	for link in page_links:
		inmate_links.append(inmate_prefix + link.get('href'))

increment = 0
for inmate_link in inmate_links:
	try:
		u_Hinds = urllib.request.urlopen(inmate_link)
		Hinds_html = u_Hinds.read()
		u_Hinds.close()
		inmate_soup = soup(Hinds_html, "html.parser")

		#generates a list of all the classes which contain relevant information
		left_txt = inmate_soup.select(".normaltxtleft")

		#generates information available, excludes those which do not seem to have anything listed
		name.append(left_txt[0].get_text().strip())
		address.append(" ".join(left_txt[1].get_text().split()))
		dob.append(left_txt[3].get_text().strip())
		sex.append(left_txt[5].get_text().strip())
		race.append(left_txt[7].get_text().strip())
		height.append(left_txt[9].get_text().strip())
		weight.append(left_txt[11].get_text().strip())
		eye_col.append(left_txt[13].get_text().strip())
		hair_col.append(left_txt[15].get_text().strip())
		arrest_agency.append(left_txt[17].get_text().strip())
		arrest_date.append(left_txt[19].get_text().strip())
		offense1.append(left_txt[20].get_text().strip())
		offense2.append(left_txt[27].get_text().strip())
		offense3.append(left_txt[34].get_text().strip())
		offense4.append(left_txt[41].get_text().strip())
		pin.append(left_txt[49].get_text().strip())
		location.append(left_txt[51].get_text().strip())
		increment += 1

	except IndexError:
		print("Index error at ", str(increment+1))
		increment += 1


dic = {"Name": name, "Address": address, "DoB": dob, "Sex": sex, "Race": race, "Height": height, "Weight": weight, "Eye color": eye_col,
"Hair color": hair_col, "Arresting agency": arrest_agency, "Arrest date": arrest_date, "Pin": pin, "Location": location,
"First offense": offense1, "Second offense": offense2, "Third offense": offense3, "Fourth offense": offense4}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)
#print(df)

from datetime import date
today = date.today()
today_date = str(today.strftime("%m-%d-%Y"))

#creates a csv
df.to_csv(today_date + '_Hinds.csv', index=False)
