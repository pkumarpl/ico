import requests 
from bs4 import BeautifulSoup
import csv
import re
import time 
from daterangeparser import parse
from datetime import datetime as dt

url = "https://icobench.com/icos"

pages=[]

while pages == '':
    try:
        pages = requests.get(url)
        break
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(5)
        print("Was a nice sleep, now let me continue...")
        continue
r = requests.get(url)

soup = BeautifulSoup(r.content,"lxml")


#page 1
refs = soup.find_all ("a", {"class": "name"})
for ref in refs: pages+=["https://icobench.com/"+ref.get("href")]

#page 2- all 

total_pages=int(soup.find_all("div", {"class": "pages"})[0].find_all("a")[len(soup.find_all("div", {"class": "pages"})[0].find_all("a"))-2].get_text())

for i in range (2,total_pages):
   url = "https://icobench.com/icos?page=%d" %i
   r = requests.get(url)
   soup = BeautifulSoup(r.content,"lxml")
   refs = soup.find_all ("a", {"class": "name"})
   for ref in refs: pages+=["https://icobench.com/"+ref.get("href")]

with open ('icobench_data.csv','w') as outfile:
   csv_writer= csv.writer (outfile)
   csv_writer.writerow (["name", 'norm_name', "symbol", "rating", "domain", "website", "start_date", "end_date",  "rated_by", "profile_rating", "team_rating", "vision_rating", "product_rating","PreICO_Price","Price","Platform","Accepting","Minimum_investment","Soft_cap","Hard_cap","Country","Whitelist_KYC","Restricted_areas","preICO_start","preICO_end","ICO_start","ICO_end","Raised","Status", "source"])

for page in pages:

   with open ('icobench_index_pages.csv','a') as outfile:
      csv_writer= csv.writer (outfile)
      csv_writer.writerow ([page])

   print(page)

   url = page

   r = requests.get(url)

   soup = BeautifulSoup(r.content,"lxml")

   #info

   title= ''
   subtitle= ''
   desc= ''
   categs= ''
   tmp = ''

   try:
   		title=soup.find_all ("h1")[0].text
   		tmp = re.sub(r'[\.\-_]*','',title)
   		tmp = re.sub(r'\s*','',tmp)
   		tmp = re.sub(r'\(.*\)','', tmp)
   		tmp = tmp.lower().strip()
   except: pass
   try:subtitle=soup.find_all ("h2")[0].text
   except: pass
   try:desc=soup("p")[0].text
   except: pass

   for cat in soup.find_all("div", {"class": "categories"})[0].find_all("a"): 
      try:categs += cat.text+'|'
      except: pass

   print (title)
   #print (subtitle)
   #print (desc)
   #print (categs)

   #ratings
   source = 'icobench'
   avg= ''
   profile= ''
   team= ''
   vision= ''
   product= ''
   Rated_by =''
   domain = ''
   start = ''
   end = ''
   #print(soup)
   try: avg = soup.find_all("div", {"itemprop": "ratingValue"})[0].find_all("div", {"content": ''})[0].get_text()
   except: pass
   try: profile = re.findall("\d+\.\d+",soup.find_all("div", {"class": "distribution"})[0].find_all("div", {"class": "col_4"})[0].text )[0]
   except: pass
   try: team = re.findall("\d+\.\d+",soup.find_all("div", {"class": "distribution"})[0].find_all("div", {"class": "col_4"})[1].text )[0]
   except: pass
   try: vision = re.findall("\d+\.\d+",soup.find_all("div", {"class": "distribution"})[0].find_all("div", {"class": "col_4"})[2].text )[0]
   except: pass
   try: product = re.findall("\d+\.\d+",soup.find_all("div", {"class": "distribution"})[0].find_all("div", {"class": "col_4"})[3].text ) [0]
   except: pass
   
   try: 
   		Rated_by = soup.find_all("div", {"itemprop": "ratingValue"})[0].find_all("small", {"content": ''})[0].get_text()
   		Rated_by = re.sub(r'expert ratings','',Rated_by)
   except: pass
   
   try: 
   		text = soup.find_all("div",{"class":"financial_data"})[0].find('a', class_="button_big")['href']
   		spltAr = text.split("://")
   		spltAr = re.sub(r'www\.','',spltAr[1])
   		spltAr = re.sub(r'tokensale\.','',spltAr)
   		spltAr = re.sub(r'token\.','',spltAr)
   		spltAr = re.sub(r'tokens\.','',spltAr)
   		spltAr = re.sub(r'ico\.','',spltAr)
   		spltAr = re.sub(r'coin\.','',spltAr)
   		spltAr = re.sub(r'crowdsale\.','',spltAr)
   		#i = (0,1)[len(spltAr)>1]
   		domain = spltAr.split("?")[0].split('/')[0].split(':')[0].lower()
   except: pass

   print(avg, Rated_by, profile, team, vision, product)

   #raised

   Raised=''
   try: Raised = soup.find_all("div", {"class": "raised"})[0].get_text()
   except: pass

   #time

   Time=''
   a=''
   b=''
   c=''


   try: a = soup.find_all("div", {"class": "financial_data"})[0].find_all("div",{"class":"row"})[0].find_all("div",{"class":"col_2 expand"})[0].find_all()[0].get_text()
   except: pass

   try: b = soup.find_all("div", {"class": "financial_data"})[0].find_all("div",{"class":"row"})[0].find_all("div",{"class":"col_2 expand"})[0].find_all()[1].get_text()
   except: pass

   try: c = soup.find_all("div", {"class": "financial_data"})[0].find_all("div",{"class":"row"})[0].find_all("div",{"class":"col_2 expand"})[0].find_all()[2].get_text()
   except: pass

   if a=='Time': Time=b+'  '+c
   
   print(b, c)
   try:
   		test = ' - '.join([dt.strptime(i, '%Y-%m-%d').strftime('%d %b %Y') for i in c.split(' - ')])
   		s, e = parse(test)
   		start = s.strftime('%Y-%m-%d')
   		end = e.strftime('%Y-%m-%d')
   except: pass	
   print(start, end)

   #financials

   financials = soup.find_all("div", {"class": "financial_data"})[0].find_all("div",{"class":"data_row"})

   #for row in financials:
   #   row.find_all("div",{"class":"col_2"})[0].prettify()
   #   row.find_all("div",{"class":"col_2"})[1].prettify()


   Status=''

   Token=''
   PreICO_Price=''
   Price=''
   Price_in_ICO=''
   Platform=''
   Accepting=''
   Minimum_investment=''
   Soft_cap=''
   Hard_cap=''
   Country=''
   Whitelist_KYC=''
   Restricted_areas=''
   preICO_start =''
   preICO_end = ''
   ICO_start = ''
   ICO_end = ''

   for row in financials:
      try: a= row.find_all("div",{"class":"col_2"})[0].get_text().strip()
      except: pass
      try: b=row.find_all("div",{"class":"col_2"})[1].get_text().strip()
      except: pass
      if a == 'Status': Status=b
      if a == 'Token': Token=b
      if a == 'PreICO Price': PreICO_Price=b
      if a == 'Price': Price=b
      if a == 'Price in ICO': Price_in_ICO=b
      if a == 'Platform': Platform=b
      if a == 'Accepting': Accepting=b
      if a == 'Minimum investment': Minimum_investment=b
      if a == 'Soft cap': Soft_cap=b
      if a == 'Hard cap': Hard_cap=b
      if a == 'Country': Country=b
      if a == 'Whitelist/KYC': Whitelist_KYC=b
      if a == 'Restricted areas': Restricted_areas=b
      if a == 'preICO start': preICO_start=b
      if a == 'preICO end': preICO_end=b
      if a == 'ICO start': ICO_start=b
      if a == 'ICO end': ICO_end=b


   print (Token)
   print (PreICO_Price)
   print (Price)
   print (Price_in_ICO)
   print (Platform)
   print (Accepting)
   print (Minimum_investment)
   print (Soft_cap)
   print (Hard_cap)
   print (Country)
   print (Whitelist_KYC)
   print (Restricted_areas)
   print (preICO_start)
   print (preICO_end)
   print (ICO_start)
   print (ICO_end)


   print (Raised)

   print (Status)
   print (Time)

   with open ('icobench_data.csv','a') as outfile:
      csv_writer= csv.writer (outfile)
      csv_writer.writerow ([title, tmp, Token, domain, avg, url, start, end,  Rated_by, profile, team, vision, product,PreICO_Price,Price,Platform,Accepting,Minimum_investment,Soft_cap,Hard_cap,Country,Whitelist_KYC,Restricted_areas,preICO_start,preICO_end,ICO_start,ICO_end,Raised,Status, source])
