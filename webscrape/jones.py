import requests
import urllib.request
from bs4 import BeautifulSoup as soup
import pandas as pd
import math

#initializing fields
first_names = []
last_names = []
booking_nums = []
ages = []
gender = []
race = []
addresses = []
arrest_agency = []
book_date = []
charges = []
bonds = []
bondable = []
num_bondable = 0

u_jones = requests.get("https://www.jonesso.com/roster.php")
jones_soup = soup(u_jones.text, "html.parser")
u_jones.close()

num_inmates = int(jones_soup.find_all("h2")[0].get_text().replace("Inmate Roster (", "").replace(")", "").strip())
num_pages = math.ceil(num_inmates/20)
#page_links = jones_soup.select(".page_num")[3:-2]
page_range = range(num_pages+1)[1:]
inmate_links = []
#for a in a_tags:
#	inmate_links.append(a.get("href"))

page_prefix = "https://www.jonesso.com/roster.php?&grp="
inmate_prefix = "https://www.jonesso.com/"

for page in page_range:

	u_page = requests.get(page_prefix + str(page*20))
	page_soup = soup(u_page.text, "html.parser")
	u_page.close()


	a_tags = (page_soup.find_all(attrs={"id":"cms-body-content"})[0].find_all("a"))
	for a in a_tags:
		inmate_links.append(a.get("href"))

	#print(page_soup.find_all("a"))


for inmate in inmate_links:
	cgs = []
	u_inmate = requests.get(inmate_prefix + inmate)
	inmate_soup = soup(u_inmate.text, "html.parser")
	u_inmate.close()

	name = inmate_soup.select(".ptitles")[0].get_text().split()
	first_names.append(name[0])
	last_names.append(name[1])

	rows = inmate_soup.find(attrs={"id":"cms-body-content"}).select(".row")[0].select(".row")
	booking_nums.append(rows[0].find_all("div")[1].get_text())
	ages.append(rows[1].get_text().strip().strip("Age:").strip())
	gender.append(rows[2].get_text().strip().strip("Gender:").strip())
	race.append(rows[3].get_text().strip().strip("Race:").strip())
	addresses.append(rows[4].get_text().strip().strip("Address:").strip())
	arrest_agency.append(rows[5].get_text().strip("Arresting Agency:").strip())
	book_date.append(rows[6].get_text().replace("Booking Date:", "").strip().split()[0])
	off_str = str(rows[8]).strip("<div class=\"row\">").strip().strip("<div class=\"cell inmate_profile_data_content\"><span class=\"text2\">")
	off_str = off_str.replace("<br/></span></div>\n</", "").strip().split("<br/>")
	for off in off_str:
		cgs.append(off.strip())
	charges.append(cgs)
	bond = int(rows[9].get_text().strip().strip("Bond:").replace("$", "").strip())
	bonds.append(bond)
	if bond != 0:
		bondable.append(True)
		num_bondable += 1
	else:
		bondable.append(False)

dic = {"First name": first_names, "Last name": last_names, "Booking Number": booking_nums, "Age": ages, "Gender": gender,
	"Race": race, "Address": addresses, "Arrest agency": arrest_agency, "Book date": book_date, "Charges": charges,
	"Bond": bonds, "Bondable?": bondable}

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)
#print(df)

compression_opts = dict(method='zip', archive_name='jones.csv')
df.to_csv('jones.zip', index=False, compression=compression_opts)

print("There are currently ", num_bondable, " bondable detainees.")