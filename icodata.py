import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import datetime

def main():
	domain = ''
	gainers_page = requests.get("https://www.icodata.io/ICO")
	print(str(gainers_page.status_code))
	soup = BeautifulSoup(gainers_page.content, 'html.parser')
	
	table = soup.find(id="table")
	thead = table.find('thead')
	headers = []
	for th in thead.tr.find_all('th'):
		headers.append(th.text)
	
	table_body = table.find('tbody')
	gainer_list = table_body.find_all('tr')
	    #print(gainer_list)
    # Create a panda dataframe
	df = pd.DataFrame(columns=headers, index=range(0, len(gainer_list)))
	row_marker = 0
	   # Parse row by row
	for ICO in gainer_list:
		data = ICO.find_all('td')
		columns = []
		for td in data:
			text = td.text.strip()
			
			columns.append(text)
		   # Find link to the ICO page
		
		link = data[1].find('a')['href']
		link = 'https://www.icodata.io' + link
		#links.append(link)
		#columns[0] = link
		#print(type(link))
		# Index data to df
		html = requests.get(link).content
		soup = BeautifulSoup(html, "lxml")
		try:
			text = soup.find('a', class_='website')['href']
			spltAr = text.split("://")
			#print(spltAr)
			spl = re.sub(r'www/.','',spltAr[1])
			#print(spl)
			i = (0,1)[len(spl)>1]
			domain = spl.split("?")[0].split('/')[0].split(':')[0].lower()
			domain = re.sub(r'www\.','',domain)
			#print(domain)
		except:
			domain = ''
		#print(type(text))
		columns[0] = text
		#print(columns[0])
		columns[9] = domain
		
		col_marker = 0
		for column in columns:
			df.iat[row_marker,col_marker] = column
			col_marker += 1
		if len(columns) > 0:
			row_marker += 1
		#break
	now = datetime.datetime.now()
	date = now.strftime("%Y_%m_%d")
	   #print(links)
    
    # Write dataframe to a local csv file for now
	df.to_csv("ico_data_" + date + ".csv", encoding='utf-8', index=False)
    

if __name__ == "__main__":
    main()