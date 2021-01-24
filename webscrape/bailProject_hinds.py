import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from lxml import html

# my_url = "https://www.co.jackson.ms.us/324/Inmate-Lookup"
my_url ='http://www.co.hinds.ms.us/pgs/apps/inmate/inmate_list.asp?name_sch=&SS1=1&search_by_city=&search_by=&ScrollAction=Page+2'
# opening up connection, grapping the page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# html parsing
page_soup = soup(page_html, "html.parser")
# print(page_soup.body.find("div", {"class":"outer-wrap"}))
# file2write=open("filename",'w')
# file2write.close()
# print(page_soup.h1)
# container = page_soup.findAll("div", {"id":"inmateListWrapper"})[0].findAll("article", {"class":"ilcard"})
container = page_soup.find_all('a', {"class":"Right_Link"})
# container = page_soup.select('#customHtmld7475a71-a0ea-4d23-b933-25c29af5ee39')[0].div.div

# print(page_soup.body)
print(len(container))
for i in container:
    print(i.text)
