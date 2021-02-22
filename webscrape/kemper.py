import requests
import urllib.request
from bs4 import BeautifulSoup as soup
import pandas as pd
import math

first_names = []
middle_names = []
last_names = []
booking_nums = []
ages = []
gender = []
race = []
addresses = []
book_dates = []
charges = []

u_Kemper = requests.get("https://www.kempercountysheriff.com/roster.php?&grp=10")
kemper_soup = soup(u_Kemper.text, "html.parser")
u_Kemper.close()

#scrapes the first page to get the number of inmates, computes the number of pages, then generates links
page_links = []
inmate_links = []
num_inmates = int(kemper_soup.h2.get_text().strip("Inmate Roster (").strip(")"))
num_pages = math.ceil(num_inmates/10)

for n in range(num_pages):
	page_links.append("https://www.kempercountysheriff.com/roster.php?&grp=" + str((n+1)*10))



#scrapes each page for inmate links
for page in page_links:
	u_page = requests.get(page)
	page_soup = soup(u_page.text, "html.parser")
	u_page.close()

#print(kemper_soup.find_all(attrs={"id":"cms-body-content"})[0].find_all("a")[0].get("href"))
	inmate_table = page_soup.find_all(attrs={"id":"cms-body-content"})[0].find_all("a")
	for inmate in inmate_table:
		inmate_links.append("https://www.kempercountysheriff.com/" + inmate.get("href"))

for inmate in inmate_links:
	u_inmate = requests.get(inmate)
	inmate_soup = soup(u_inmate.text, "html.parser")
	u_inmate.close()

	name = inmate_soup.select(".ptitles")[0].get_text().split()
	first_names.append(name[0])
	last_names.append(name[-1])
	middle_names.append(name[1:-1])

	rows = inmate_soup.find_all(attrs={"id":"cms-body-content"})[0].select(".row")
	#note that not all pages have the address listed, this messes up indexing
	booking_nums.append(rows[1].find_all("div")[1].get_text())
	ages.append(rows[2].get_text().replace("Age:", "").strip())
	gender.append(rows[3].get_text().replace("Gender:", "").strip())
	race.append(rows[4].get_text().replace("Race:", "").strip())
	if len(rows) == 9:
		addresses.append("")
		book_dates.append(rows[5].get_text().split()[2])
		charges.append(rows[7].get_text().strip())

	else:
		addresses.append(rows[5].get_text().replace("Address:", "").strip())
		book_dates.append(rows[6].get_text().split()[2])
		charges.append(rows[8].get_text().strip())	

dic = {"First name": first_names, "Middle name": middle_names, "Last name": last_names,
	"Booking number": booking_nums, "Age": ages, "Gender": gender, "Race": race, 
	"Address": addresses, "Booking date": book_dates, "Charges": charges}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)
print(df)

compression_opts = dict(method='zip', archive_name='kemper.csv')
df.to_csv('kemper.zip', index=False, compression=compression_opts)