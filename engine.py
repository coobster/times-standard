from requests import get
from sqlite3 import connect
from bs4 import BeautifulSoup as bs
from time import sleep,time,localtime
from threading import Thread
from os.path import exists, isfile

DATABASE = 'newssource-humboldt'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

source = 'www.times-standard.com'

def setup():
	if not exists(DATABASE):
		sql = "CREATE TABLE art (h_link,url,title,year,month,day)"
		db = connect(DATABASE)
		cur = db.cursor()
		cur.execute(sql)
		db.commit()
		db.close()

def download_day(source,ymd):
	url = "https://{}/{}/{}/{}".format(source,ymd[0],ymd[1],ymd[2])
	art_count = 0
	existing_count = 0
	print('-'*30)
	print("DATE: {}/{}/{}".format(ymd[1],ymd[2],ymd[0]))
	while True:
		r = get(url,headers=headers)
		soup = bs(r.content,features="lxml")
		href = [i.a for i in soup.findAll('div') if i.get('class') and 'article-info' in i.get('class')]
		links = [(i.text.strip(),i.get('href')) for i in href if i.get('href') and '2020' in i.get('href') and i.text]
		db = connect(DATABASE)
		cur = db.cursor()
		for article in links:
			result = cur.execute('SELECT COUNT(url) FROM art WHERE url=?',(article[1],))
			count = int(result.fetchone()[0])
			if not count:
				y,m,d = url.split('/')[3:6]
				cur.execute('INSERT INTO art VALUES(?,?,?,?,?,?)',(time(),article[1],article[0],y,m,d))
				art_count += 1
			else:
				existing_count += 1
		db.commit()
		db.close()

		load_more = [i.get('href') for i in soup.findAll('a') if i.get('class') and 'load-more' in i.get('class')]
		if len(load_more):
			url = load_more[0]
		else:
			break
	print ("ADDED {} articles to database.".format(art_count))
	print ("{} articles already exist.".format(existing_count))

if __name__ == '__main__':
	setup()
	# download current day articles
	download_day(source,localtime(time())[:3])
