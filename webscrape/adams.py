import urllib.request
from bs4 import BeautifulSoup as soup
import pandas as pd
import csv

u_Adams = urllib.request.urlopen('http://www.adamscosheriff.org/inmate-roster/')
Adams_html = u_Adams.read()
u_Adams.close()
adams_soup = soup(Adams_html, "html.parser")

page_num = adams_soup.select(".page-numbers")[-2].get_text()

names = []
booking_nums = []
age = []
gender = []
race = []
booking_date = []
charges = []
bonds = []
bondable = []
bondable_names = []
num_bondable = 0
num_errs = 0

for page in range(int(page_num)):
	#scrapes for profile links
	u_page= urllib.request.urlopen('http://www.adamscosheriff.org/inmate-roster/page/' + str(page+1) + "/")
	page_html = u_page.read()
	u_page.close()
	page_soup = soup(page_html, "html.parser")

	page_profile_links = page_soup.select(".profile-link")

	for profile in page_profile_links:
		try: 
			#print(profile.a.get("href"))

			u_inmate = urllib.request.urlopen(profile.a.get("href"))
			inmate_html = u_inmate.read()
			u_inmate.close()
			inmate_soup = soup(inmate_html, "html.parser")

			#scrapes 
			p_vals = inmate_soup.find_all("p")
			name = (p_vals[0].get_text().strip("Full Name:").strip())
			names.append(name)
			booking_nums.append((p_vals[1].get_text().strip("Booking Number:").strip()))
			age.append(p_vals[2].get_text().strip("Age:").strip())
			gender.append(p_vals[3].get_text().strip("Gender:").strip())
			race.append(p_vals[4].get_text().strip("Race:").strip())
			booking_date.append(p_vals[7].get_text().strip("Booking Date:").strip())
			charges.append(p_vals[8].get_text().strip("Charges:").strip())
			b = p_vals[9].get_text().strip("Bond:").replace(",", "").strip()
			b_able = False
			if b == "":
				bond = 0.0
			else:
				bond = float(b)
				b_able = True
				num_bondable += 1
				bondable_names.append(name)
			bonds.append(bond)
			bondable.append(b_able)

		except IndexError:
			num_errs += 1
			print("IndexError")

dic = {"Name": names, "Booking Number": booking_nums, "Age": age, "Gender": gender, "Race": race, "Booking Date": booking_date, 
		"Charges": charges, "Bondable?": bondable, "Bond": bonds}
df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)

compression_opts = dict(method='zip', archive_name='adams.csv')
df.to_csv('adams.zip', index=False, compression=compression_opts)