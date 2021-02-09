import webbrowser 
import requests
import urllib.request
import math
from bs4 import BeautifulSoup as soup
import pandas as pd

#opens the first page of the roster to generate links to inmate pages
roster_prefix = "http://www.claysheriffms.org/roster.php"
u_clay = requests.get(roster_prefix)
clay_soup = soup(u_clay.text, "html.parser")
u_clay.close()

inmate_prefix = "http://www.claysheriffms.org/"
inmate_links = []

name = []
booking_num = []
age = []
sex = []
race = []
arrest_agency = []
arrest_date = []
bond = []
bondable = []
offenses = []

num_inmates = int(clay_soup.select(".ptitles")[0].get_text().split()[2].replace("(", "").replace(")", ""))
num_pages = math.ceil(num_inmates/10)

#steps through the pages of the roster and scrapes for urls to inmate pages
for page in range(num_pages):
	u_clay = requests.get(roster_prefix + "?grp=" + str(page*10))
	clay_soup = soup(u_clay.text, "html.parser")
	u_clay.close()

	inmate_table = clay_soup.select(".inmateTable")
	for i in inmate_table:
		inmate_links.append(inmate_prefix + i.select(".text2")[-1].get("href"))


#goes through list of links to inmate pages and finds information
for inmate in inmate_links:
	u_inmate = requests.get(inmate)
	inmate_soup = soup(u_inmate.text, "html.parser")
	u_inmate.close()

	table = inmate_soup.find_all("table")[6].select(".text2")

	name.append(' '.join(inmate_soup.select('.ptitles')[0].get_text().split()))

	booking_num.append(table[0].get_text().strip())
	age.append(int(table[1].get_text().strip()))
	sex.append(table[2].get_text().strip())
	race.append(table[3].get_text().strip())
	arrest_agency.append(table[4].get_text().strip())
	arrest_date.append(table[5].get_text().split()[0])

	bond_ = float(table[8].get_text().strip("$"))
	bond.append(bond_)
	bondable.append(bool(bond_))

	offenses.append(str(table[7]).strip("<span class=\"text2\">").strip("</").split("<br/>"))

#generates a dictionary, then creates a dataframe to print

dic = {"Name": name, "Booking number": booking_num, "Arrest agency": arrest_agency, "Arrest date": arrest_date, 
"Bondable?": bondable, "Bond": bond, "Age": age, "Sex": sex, "Race": race, "Offense(s)": offenses}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)

print(df)
