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
page_prefix = "https://www.tunicamssheriff.com/roster.php?&grp="
inmate_prefix = "https://www.tunicamssheriff.com/"
num_inmates = int(tunica_soup.select(".ptitles")[0].get_text()[15:-1])
num_pages = math.ceil(num_inmates/10)
for p in range(num_pages):
	page_links.append(page_prefix + str((p+1)*10))

for page in page_links:
	u_page = requests.get(page)
	page_soup = soup(u_page.text, "html.parser")
	u_page.close()

	links = page_soup.find_all(attrs={"id":"cms-body-content"})[0].select("a")
	for link in links:
		inmate_links.append(inmate_prefix + link.get("href"))

print(inmate_links)


#goes through each inmate page
for inmate in inmate_links:
	u_inmate = requests.get(inmate)
	inmate_soup = soup(u_inmate.text, "html.parser")
	u_inmate.close()

	name = (inmate_soup.select(".ptitles")[0].get_text().split())
	first_names.append(name[0])
	last_names.append(name[-1])
	middle_names.append(name[1:-1])

	rows = inmate_soup.find_all(attrs={"id":"cms-body-content"})[0].select(".row")[0].select(".row")
	booking_nums.append(int(rows[0].find_all("div")[1].get_text()))
	ages.append(int(rows[1].find_all("div")[1].get_text()))
	gender.append(rows[2].find_all("div")[1].get_text())
	race.append(rows[3].find_all("div")[1].get_text())
	arrest_agency.append(rows[4].find_all("div")[1].get_text())
	book_date.append(rows[5].find_all("div")[1].get_text().split()[0])
	offs = []
	offs_str = (str(rows[7].select(".text2")[0]).replace("<span class=\"text2\">", "").replace("</span>", "").split("<br/>"))
	for off in offs_str:
		offs.append(off.strip())
	charges.append(offs)
	try:
		bd = rows[8].get_text().replace("Bond:", "").strip()
		if "$" in bd:
			bonds.append(float(bd.strip("$")))
			bondable.append(True)
			num_bondable += 1
		else:
			bonds.append(0.0)
			bondable.append(False)
	except IndexError:
		bonds.append(0.0)
		bondable.append(False)


dic = {"First name": first_names, "Middle name": middle_names, "Last name": last_names,
	"Booking number": booking_nums, "Age": ages, "Gender": gender, "Race": race, 
	"Arrest agency": arrest_agency, "Booking date": book_date, "Charges": charges,
	"Bond": bonds, "Bondable?": bondable}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)

compression_opts = dict(method='zip', archive_name='tunica.csv')
df.to_csv('tunica.zip', index=False, compression=compression_opts)
