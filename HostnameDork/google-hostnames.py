from lxml.html import fromstring
from http.cookiejar import CookieJar
import requests
import os
import re
import time
import urllib.parse
import webbrowser
import random
import string
import argparse
import sys

parser = argparse.ArgumentParser(description='Find subdomains from google search results - AWS API gateway version')
parser.add_argument('--proxy', 
                    help='AWS API gateway', required=True)
parser.add_argument('-d', '--domain', 
                    help='domain or company name to target', required=False)
parser.add_argument('-f', '--file', 
                    help='file w/ list of names', required=False)
parser.add_argument('--pages', 
                    help='page search depth', type=int, default=1, required=False)   
parser.add_argument('--debug', 
                    help='debug output', required=False, action='store_true')

args = parser.parse_args()

if not args.domain and not args.file: 
    print("Specify either target domain (-d) or file with domains (-t)")
    sys.exit()

if "execute-api" not in args.proxy: 
    print("Incorrect AWS API gateway")
    sys.exit()

domains = []
if args.domain: 
    domains.append(args.domain)
else: 
    file_in=open(args.file)
    for line in file_in:
        domains.append(line.rstrip())

cookiejar = CookieJar()
user_agent = 'Lynx/2.8.8dev.3 libwww-FM/2.14 SSL-MM/1.4.1'

def search_google_web(query, proxy, limit=0, start_page=1):
    # parsing logic based on https://github.com/maurosoria/s3arch
    url = proxy + 'search'
    num = 100
    page = start_page
    set_page = lambda x: (x - 1) * num
    payload = {'q':query, 'start':set_page(page), 'num':num, 'complete':0}
    rand = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    headers = {'user-agent': user_agent, f"X-My-X-Forwarded-For": "{rand}"}
    results = []
    if args.debug: print(f"Searching Google for: {query}")
    while True:
        resp = requests.get(url, params=payload, headers=headers, allow_redirects=False, cookies=cookiejar)
        # detect and handle captchas
        # results = 200, first visit = 302, actual captcha = 503
        count = 0
        if resp.status_code != 200:
            if resp.status_code == 302:
                print('Google CAPTCHA triggered. No bypass available.')
            else:
                print('Google encountered an unknown error.')
            break
        tree = fromstring(resp.text)
        links = tree.xpath('//a/@href')
        regmatch = re.compile(r'^/url\?q=[^/]')
        for link in links:
            if regmatch.match(link) != None and 'http://webcache.googleusercontent.com' not in link:
                results.append(urllib.parse.unquote_plus(link[7:link.find('&')]))
        # check limit
        if limit == page:
            break
        page += 1
        payload['start'] = set_page(page)
        # check for more pages
        if '>Next</' not in resp.text:
            break
    return results



for domain in domains:
    hosts = []

    base_query = 'site:' + domain
    regmatch = re.compile(rf"//([^/]*\.{domain})")
    # control variables
    new = True
    page = 1
    nr = 100
    # execute search engine queries and scrape results storing subdomains in a list
    # loop until no new subdomains are found
    while new:
        # build query based on results of previous results
        query = ''
        for host in hosts:
            query += f" -site:{host}"
        # send query to search engine
        results = search_google_web(base_query + query, args.proxy, limit=1, start_page=page)
        # extract hosts from search results
        sites = []
        for link in results:
            site = regmatch.search(link)
            if site is not None:
                sites.append(site.group(1))
        # create a unique list
        sites = list(set(sites))
        # add subdomain to list if not already exists
        new = False
        for site in sites:
            if site not in hosts:
                hosts.append(site)
                new = True
        if not new:
            # exit if all subdomains have been found
            if not sites:
                break
            else:
                # intelligently paginate separate from the framework to optimize the number of queries required
                page += 1
                if args.debug: print(f"No New Subdomains Found on the Current Page. Jumping to Result {(page*nr)+1}.")
                new = True

    print(*hosts, sep='\n')