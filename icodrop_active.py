import time
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import requests
import csv
import datetime
from dateutil import parser
from daterangeparser import parse

url = 'https://icodrops.com/category/upcoming-ico/'

browser = webdriver.PhantomJS()
browser.get(url)
time.sleep(2)

lastHeight = browser.execute_script("return document.body.scrollHeight")
print('lastHeight', lastHeight)
while True:
	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(1)
	newHeight = browser.execute_script("return document.body.scrollHeight")
	if newHeight == lastHeight:
		break
	lastHeight = newHeight

soup = BeautifulSoup(browser.page_source, "html.parser")
icos = soup.findAll("a", {'id': 'n_color'})
#print(icos)

this_year = ['january', 'february', 'march']
last_year = ['april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

#def add_year(input_date: str)-> str:
 #   month = input_date.split(' ')[-1]
 #   updated_date = f'{input_date} 2018' if month.lower() in this_year else f'{input_date} 2017'
 #   new = parser.parse(updated_date)
 #   formated = new.strftime('%Y-%m-%d')
 #   return formated
    
def clean(input):
	return re.sub("[^0-9.]", "", input)


def raised(input):
	try:
		return clean(input.find('div', class_='goal-in-card').find('span').text.strip())
	except:
		return '-'



def subpage_data(url):
	price = '-'
	goal = '-'
	date = ''
	token = '-'
	start = ''
	end = ''
	html = requests.get(url).content
	#print(html)
	soup = BeautifulSoup(html, "lxml")
	#print(soup)
	try:
		pr = soup.findAll('div', class_='col-12 col-md-6')[0].findAll('li')[2].text
		if 'ICO Token Price:' in pr:
			splitted = pr.split()
			price =  splitted[6]
		else: 
			price = '-'
	except:
		price = '-'

	try:
		text = soup.find('div', class_='ico-right-col')
		goal = clean(text.find('div', class_="goal").text.split("(")[0].strip())
	except:
		goal = '-'
	
	try:
		tk = soup.findAll('div', class_='col-12 col-md-6')[0].findAll('li')[0].text
		if 'Ticker:' in tk:
			splitted = tk.split()
			token =  splitted[1]
		else:
			token = '-'
	except:
		token = '-'
	
	try:
		text = soup.find_all("div",{"class":"rating-item"})[0]
		hype = text.find('p', class_="rate").text.strip()
	except:
		hype = '-'
	
	try:
		text = soup.find_all("div",{"class":"rating-item"})[1]
		risk = text.find('p', class_="rate").text.strip()
	except:
		risk = '-'
	
	try:
		text = soup.find_all("div",{"class":"rating-item"})[2]
		roi = text.find('p', class_="rate").text.strip()
	except:
		roi = '-'

	try:
		text = soup.find('div', class_='rating-result')
		icorate = text.find('p', class_="ico-rate").text.strip()
		
	except:
		icorate = '-'
	
	try:
		text = soup.find("div", {"class": "button"}).parent['href']
		spltAr = text.split("://")
		spltAr = re.sub(r'www/.','',spltAr)
		i = (0,1)[len(spltAr)>1]
		domain = spltAr[i].split("?")[0].split('/')[0].split(':')[0].lower()

	except:
		domain = '-'
	
	try:
		text = soup.find_all("div",{"class":"col-12 title-h4"})[0].findAll('h4')[0].text.strip()
		text2 = re.sub(r'[\t\n\r]*','', text)
		text3 = re.sub(r'Token Sale: ','', text2)
		text4 = re.sub(r'\(.*\)','', text3)
		text5 = re.sub(r'since','', text4)
		text6 = re.sub(r'Market & Returns','', text5)
		date = re.sub(r'period isn\'t set','', text6)

	except: 
		date = ''
	
	try:
		s, e = parse(date)
		start = s.strftime('%Y-%m-%d')
		end = e.strftime('%Y-%m-%d')
	except:
		pass
		
	return [price, goal, date, start, end, token, hype, risk, roi, icorate, domain]

columns = ['name', 'norm_name', 'symbol', 'date', 'domain', 'website', 'ico_price', 'start_date', 'end_date', 'rating', 'hype_rating', 'risk_rating', 'roi_rating', 'raised', 'goal']
data = []

for ico in icos:
	name = ico.find('h3').text.strip()
	tmp = re.sub(r'[\.\-_]*','',name)
	tmp = re.sub(r'\s*','',tmp)
	tmp = re.sub(r'\(.*\)','', tmp)
	tmp = tmp.lower().strip()
	
	url = ico['href']
	#rate = ''
	[price, goal, date, start, end, token, hype, risk, roi, icorate, domain] = subpage_data(url)
	#try:
	##	rate = r.text.strip()
	#except:
	#	rate = 'NA'
	#print(start, end)
	line = [name, tmp, token, date, domain, url, price, start, end, icorate, hype, risk, roi, raised(ico), goal]
	print(line)
	data.append(line)


now = datetime.datetime.now()
date = now.strftime("%Y_%m_%d")

with open("upcoming_ico_data_" + date + ".csv", "w+") as my_csv:
	csvWriter = csv.writer(my_csv, delimiter=',')
	csvWriter.writerow(columns)
	csvWriter.writerows(data)
