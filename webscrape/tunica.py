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
arrest_agency = []
book_date = []
charges = []
bonds = []
bondable = []
num_bondable = 0

u_Tunica = requests.get("https://www.tunicamssheriff.com/roster.php")
tunica_soup = soup(u_Tunica.text, "html.parser")
u_Tunica.close()

page_links = []
inmate_links = []
page_prefix = "https://www.tunicamssheriff.com/"
num_inmates = tunica_soup.select(".ptitles")[0].get_text()[15:-1]

#scrapes for links to inmate pages
links = tunica_soup.select(".table")[0].find_all("div")[4].find_all("tr")[2].find_all("a")
inmate_tables = tunica_soup.select(".inmateTable")
for inmate_table in inmate_tables:
	inmate_links.append(inmate_table.find_all("tr")[-1].td.a.get("href"))

for link in links[:-1]:
	page_links.append(link.get("href"))

for link in page_links:
	u_Page = requests.get(page_prefix + link)
	page_soup = soup(u_Page.text, "html.parser")
	u_Page.close()


	inmate_tables = page_soup.select(".inmateTable")
	for inmate_table in inmate_tables:
		inmate_links.append(inmate_table.find_all("tr")[-1].td.a.get("href"))

#goes through each inmate page
for inmate in inmate_links:
	u_inmate = requests.get("https://www.tunicamssheriff.com/" + inmate)
	inmate_soup = soup(u_inmate.text, "html.parser")
	u_inmate.close()
	name = (inmate_soup.select(".ptitles")[0].get_text().split())
	first_names.append(name[0])
	last_names.append(name[-1])
	middle_names.append(name[1:-1])

	booking_nums.append(inmate_soup.tr.find_all("tr")[0].find_all("td")[1].get_text())
	ages.append(inmate_soup.tr.find_all("tr")[1].find_all("td")[1].get_text())
	gender.append(inmate_soup.tr.find_all("tr")[2].find_all("td")[1].get_text())
	race.append(inmate_soup.tr.find_all("tr")[3].find_all("td")[1].get_text())
	arrest_agency.append(inmate_soup.tr.find_all("tr")[4].find_all("td")[1].get_text())
	book_date.append(inmate_soup.tr.find_all("tr")[5].find_all("td")[1].get_text().split()[0])
	off_str = str(inmate_soup.tr.find_all("tr")[7].td)
	off_str = off_str.strip("<br/></span></td").strip("<td colspan=\"2\"><span class=\"text2\">")
	offs = off_str.split("<br/>")
	charges.append(offs)
	
	#note that charges are sometimes not listed
	try:
		bd = inmate_soup.tr.find_all("tr")[8].find_all("td")[1].get_text()
	except IndexError:
		bd = ""
	if "$" in bd:
		bonds.append(float(bd.strip("$")))
		bondable.append(True)
		num_bondable += 1
	else:
		bonds.append(0.0)
		bondable.append(False)

dic = {"First name": first_names, "Middle name": middle_names, "Last name": last_names,
	"Booking number": booking_nums, "Age": ages, "Gender": gender, "Race": race, 
	"Arrest agency": arrest_agency, "Booking date": book_date, "Charges": charges,
	"Bond": bonds, "Bondable?": bondable}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)
#print(df)

compression_opts = dict(method='zip', archive_name='tunica.csv')
df.to_csv('tunica.zip', index=False, compression=compression_opts)