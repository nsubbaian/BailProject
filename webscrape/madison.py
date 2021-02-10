import urllib.request
from bs4 import BeautifulSoup as soup
import pandas as pd
import csv

#opening connection, reading page
u_Madison = urllib.request.urlopen('http://mydcstraining.com/agencyinfo/MS/4360/inmate/ICURRENT.HTM')
Madison_html = u_Madison.read()
u_Madison.close()



mad_soup = soup(Madison_html, "html.parser")

prefix = 'http://mydcstraining.com/agencyinfo/MS/4360/inmate/ICUD'

#determines the number of people detained
inmate_num = int(mad_soup.find_all('b')[4].get_text()) 

#generates a list of links to intake reports
links = []
for i in range(inmate_num):
	if i < 9:
		links.append(prefix + "000" + str(i+1) + ".HTM")
	elif i < 99:
		links.append(prefix + "00" + str(i+1) + ".HTM")
	else:
		links.append(prefix + "0" + str(i+1) + ".HTM")

#initializes lists 
#note that the index is offset by one from the list of inmates in the url (starts at 1 rather than zero)
index = 0
names = []
ages = []
birthdays = []
arrest_dates = []

heights = []
weights = []
race = []
sex = []
hair_colors = []
eye_colors = []
facial_hair = []
complexions = []

off_dates = []
case_nums = []
intake_dates = []
intake_times = []
intake_nums = []
arrest_agencies = []

num_bondable = 0
written_bonds = []
cash_bonds = []
bondable = []
bondable_names = []

offenses = []


for link in links:
	u_inmate = urllib.request.urlopen(link)
	inmate_html = u_inmate.read()
	u_inmate.close()


	inmate_soup = soup(inmate_html, "html.parser")

	fieldsets = inmate_soup.find_all("fieldset")

	#Finds names and splits among respective lists according to length
	#note that this produces an array for the first name when there are three names, is this an issue?
	name_dob_age = fieldsets[0].find_all("tr")
	name = name_dob_age[0].get_text()[9:]
	names.append(name)

	#finds age and birthday from same fieldset as name
	dob_age = name_dob_age[3].find_all("td")
	birthdays.append(dob_age[0].get_text()[5:].strip())
	ages.append(dob_age[1].get_text()[5:].strip())

	#scrapes the "description" box
	appearance_fields = fieldsets[1].find_all("tr")
	heights.append(appearance_fields[0].find_all("td")[0].get_text()[5:].strip())
	weights.append(appearance_fields[0].find_all("td")[1].get_text()[5:].strip())
	race.append(appearance_fields[1].find_all("td")[0].get_text()[6:].strip())
	sex.append(appearance_fields[1].find_all("td")[1].get_text()[5:].strip())
	hair_colors.append(appearance_fields[2].find_all("td")[0].get_text()[6:].strip())
	eye_colors.append(appearance_fields[2].find_all("td")[1].get_text()[5:].strip())
	facial_hair.append(appearance_fields[3].find_all("td")[0].get_text()[7:].strip())
	complexions.append(appearance_fields[3].find_all("td")[1].get_text()[7:].strip())

	#scrapes the "intake/booking" box
	intake_fields = fieldsets[2].find_all("tr")
	off_date = intake_fields[0].get_text()[11:].split()[0]
	if off_date == "00/00/0000":
		off_date = ""
	off_dates.append(off_date)
	case_num = intake_fields[0].get_text()[11:].split()[3]
	if case_num == "OTHER":
		case_num = ""
	case_nums.append(case_num)

	intake_dates.append(intake_fields[1].get_text().split()[2])
	intake_times.append(intake_fields[1].get_text().split()[4])
	intake_nums.append(intake_fields[2].get_text()[11:].strip())
	arrest_agencies.append(intake_fields[3].get_text()[19:].strip())

	#Bond Information box
	written_bond = (float(fieldsets[4].find_all("tr")[0].get_text().split()[3].strip(",grt").replace(',', "")))
	written_bonds.append(written_bond)
	bondable_ = bool(written_bond)
	bondable.append(bondable_)
	if bondable_:
		num_bondable += 1
		bond_names = [name.strip(), index]
		bondable_names.append(bond_names)
	cash_bonds.append(float(fieldsets[4].find_all("tr")[1].get_text().split()[3].strip(",grt").replace(',', "")))

	#Offense text box
	offs = fieldsets[5].find_all("tr")[2:]
	desc = []
	court = []
	bond_amt_ = []
	for o in offs:
		off = o.find_all("td")
		desc.append(off[0].get_text())
		court.append(off[1].get_text().strip() + " COURT")
		bond_amt = off[2].get_text().strip().replace(",", "")
		if bond_amt == "":
			bond_amt = "0"
		bond_amt_.append(float(bond_amt))

	off_dict = {"Description": desc, "Court": court, "Bond amount": bond_amt_}
	offenses.append(off_dict)
	index += 1 



#generates a dataframe with dictionary dic, then prints dataframe as specified
dic = {"Name": names, "Ages": ages, "Birthdays": birthdays, 
	"Height": heights, "Weight": weights, "Race": race, "Sex": sex, "Hair color": hair_colors, "Eye color": eye_colors, "Facial hair": facial_hair, 
	"Complexion": complexions, 
	"Off date": off_dates, "Case number": case_nums, "Intake date": intake_dates, "Intake number": intake_nums, "Arresting agency": arrest_agencies, 
	"Bondable?": bondable, "Written bond": written_bonds, "Cash bond": cash_bonds,
	"Offense(s)": offenses}
#make offenses a dictionary so it's more readable

df = pd.DataFrame.from_dict(dic)
pd.set_option("display.max_rows", 12, "display.max_columns", None)
print(df)
print(num_bondable)

#creates a csv
compression_opts = dict(method='zip', archive_name='madison.csv')
df.to_csv('madison.zip', index=False, compression=compression_opts)
