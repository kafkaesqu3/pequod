import requests
from bs4 import BeautifulSoup
import sqlite3
from os.path import exists, abspath
import json
import time
import sys

table_name = 'ghdb'

def init_table(): 
    sqlite_file = 'ghdb.sqlite'

    #check if file exists in pwd
    #if exists, open it and return conn string
    abs_path = abspath(sqlite_file)
    if exists(abs_path): 
        print("Database exists")
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        return (conn, c)
    else: 
        #if not, create the file and return conn string
        print("Database does not exists")
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()


        # Creating a new SQLite table with 1 column
        c.execute('CREATE TABLE {tn} ({nf} {ft} NOT NULL PRIMARY KEY)'.format(tn=table_name, nf='path', ft='TEXT'))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn='title', ct='TEXT'))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn='category', ct='TEXT'))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn='value', ct='TEXT'))
        return (conn, c)

conn, c = init_table()

for page in list(range(0, 45, 1)):
    url = f"https://www.exploit-db.com/google-hacking-database?draw={page}&columns%5B0%5D%5Bdata%5D=date&columns%5B0%5D%5Bname%5D=date&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=url_title&columns%5B1%5D%5Bname%5D=url_title&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=cat_id&columns%5B2%5D%5Bname%5D=cat_id&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=false&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=author_id&columns%5B3%5D%5Bname%5D=author_id&columns%5B3%5D%5Bsearchable%5D=false&columns%5B3%5D%5Borderable%5D=false&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start={page*120}&length=120&search%5Bvalue%5D=&search%5Bregex%5D=false&author=&category=&_=1583252753702"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0", "Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://www.exploit-db.com/google-hacking-database", "X-Requested-With": "XMLHttpRequest", "Connection": "close"}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200: 
        print("Didn't get HTTP 200, exiting")
        sys.exit(1)

    try: 
        parsed = json.loads(resp.content)
    except: 
        print("Error parsing JSON (response from server must not be JSON)")
        sys.exit(1)

    for item in parsed['data']: 
        url_title = item['url_title']
        soup = BeautifulSoup(url_title, "html.parser")

        path = soup.find('a')['href']
        title = soup.find('a').text
        category = item['cat_id'][1]
        dork_url = f"https://www.exploit-db.com{path}"

        # check if entry exists in db before fetching file
        query = """SELECT count(*) FROM ghdb where path = ?"""
        c.execute(query, (dork_url,))
        data = c.fetchone()
        if data==(1,): #if exists, we're all up to date
            print("Up to date!")
            conn.close()
            sys.exit(0)
        # if it doesnt exist, fetch the entry and put it in the db

        resp = requests.get(dork_url, headers=headers)
        #time.sleep(0.5)
        soup = BeautifulSoup(resp.content, "html.parser")
        body = soup.find('code').text

        try:
            print("Got {}".format(path))
            query = """INSERT INTO ghdb (path,title,category,value) VALUES(?,?,?,?);"""
            c.execute(query, (dork_url, title, category, body))
            conn.commit()
        except sqlite3.IntegrityError:
            print('ERROR: ID already exists in PRIMARY KEY column {}'.format(dork_url))
    print("Done with page {}".format(page))
    #time.sleep(10) # be respective of our friends at offsec
conn.close()
