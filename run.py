import urllib
import requests
from bs4 import BeautifulSoup
import sys
import time
import argparse
import re
import urllib.request
import random
import string
from sty import fg, ef, rs
import re
import time
import threading

import inspect
#global lock object for handling output
lock = threading.Lock()

#thread safe handling function of output
def handleOutput(stdout_string, log_string):
    with lock:     
        print("{}".format(stdout_string))
        if args.out and log_string: 
            runlog_file = open(args.out, "a")
            runlog_file.write(log_string)
            runlog_file.flush()
            runlog_file.close()

def runQuery(query):
    query = query.strip()
        
    page=args.start
    while(page<=PAGES_MAX): 
        # build query
        URL = f"https://google.com/search?q={urllib.parse.quote(query)}&start={page}0"
        if "execute-api" in proxy: # replace URL with API gateway endpoint
            URL = f"{proxy}search?q={urllib.parse.quote(query)}&start={page}0&filter=0"
        else: 
            URL = f"https://google.com/search?q={urllib.parse.quote(query)}&start={page}0&filter=0"
        if args.debug: 
            debug_string = f"[-] DEBUG -- QUERY: {query} URL: {URL}"
            handleOutput(debug_string, None)
        
        # make request
        if "execute-api" in proxy: # no gateway, no proxies
            # set random X-My-X-Forwarded-For to prevent IP leak
            rand = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0", f"X-My-X-Forwarded-For": "{rand}" }
            
            try: 
                resp = requests.get(URL, headers=headers, timeout=15)
            except requests.exceptions.Timeout as e: 
                print("Timeout error: {}".format(URL))
                raise(e)
            except ConnectionError as e:
                print("Connection error: {}".format(URL))
                raise(e)
        else: # use rotating proxy to make request
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0"}
            try: 
                resp = requests.get(URL, headers=headers, proxies=proxy, timeout=15)
            except requests.exceptions.Timeout as e: 
                print("Timeout error: {}".format(URL))
                raise(e)
            except ConnectionError as e:
                print("Connection error: {}".format(URL))
                raise(e)
        
        
        #handle results
        if resp.status_code == 200:
            results = []
            soup = BeautifulSoup(resp.content, "html.parser")

            # Check if any relevant results were returned
            noresults = soup.find('div', {"role": "heading"})
            if noresults: 
                if "No results found for" in noresults.get_text(): 
                    return
            noresults2 = soup.find('p', {"role": "heading"})
            if noresults2: 
                if "did not match any documents" in noresults2.get_text():
                    return
            page_results = soup.find_all(class_='g')
            if len(page_results) < 10: 
                # not a full page of results, we're done with the query
                return
            # foreach result (10 per page)
            for g in page_results:
                anchors = g.find_all('a')
                body = str(g.find_all('span')[-1]).replace("<span>", "").replace("</span>", "")
                if anchors and g.find('h3'):
                    link = anchors[0]['href']
                    title = (g.find('h3')).text
                    item = {
                        "title": title,
                        "link": link,
                        "body": body
                    }
                    results.append(item)
            for result in results: #print results after each page
                if args.body: # body
                    if args.nocolor: # no color
                        title_out = result.get('title')
                        link_out = result.get('link') 
                    else: # color
                        title_out = fg.green + result.get('title') + fg.rs
                        link_out = fg.blue + result.get('link') + fg.rs
                        body = result.get('body') 
                        if args.target: # if a target was specified, try to highlight the match in the body
                            start_mark = body.find("<em>")
                            end_mark = body.find("</em>")
                            start_str = body[0:start_mark]
                            match = body[start_mark+4:end_mark]
                            end_str = body[end_mark+5:]
                            body_out = start_str + ef.bold + match + rs.bold_dim + end_str
                        else: # no target, no markings
                            body_out = body
                    stdout_string = f"{title_out} : {link_out} : \"{body_out}\""
                    log_string = f"{result.get('title')} : {result.get('link')} : \"{result.get('body')}\"\n"
                else: # no body
                    if args.nocolor: 
                        title_out = result.get('title')
                        link_out = result.get('link')   
                    else: 
                        title_out = fg.green + result.get('title') + fg.rs
                        link_out = fg.blue + result.get('link') + fg.rs
                    stdout_string = f"{title_out} : {link_out}"
                    log_string = f"{result.get('title')} : {result.get('link')}\n"
                handleOutput(stdout_string, log_string)
            page+=1
        else: 
            raise RuntimeError("Blocked by google: {}".format(resp.status_code))
    return

# function so we can split up our queries based on number of threads
def runQueriesThread(query_list):
    for query in query_list: 
        retry_counter=0
        max_retries=3
        while (retry_counter <= max_retries):
            try: 
                runQuery(query)
            except RuntimeError as e:
                print("Exception raised (possibly blocked by Google): {}".format(e))
                err_sleep_time=30 # blocked by google
            except Exception as e:
                print("Exception raised: {}".format(e))
                err_sleep_time=10
            else: # no exceptions, continue
                break
            retry_counter+=1
            time.sleep(err_sleep_time)
        

# desktop user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:64.0) Gecko/20100101 Firefox/65.0"

parser = argparse.ArgumentParser(description='White whale, holy grail\nScalable Google dorking script w/ support for proxies/AWS API gateway endpoint', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--proxy', 
                    help='(rotating) proxy string or AWS API gateway', required=True)
parser.add_argument('-t', '--target', 
                    help='domain or company name to target', required=False)
parser.add_argument('--target-file', 
                    help='file containing target info', required=False)
parser.add_argument('-o', '--operator', 
                    help='operator to place on target', required=False, type=str)
parser.add_argument('--dorkfile', 
                    help='file w/ list of dorks', required=True)
parser.add_argument('--pages', 
                    help='page search depth', type=int, default=10, required=False)                    
parser.add_argument('--start', 
                    help='start at page (0=first page)', type=int, default=0, required=False)                    
parser.add_argument('--threads', 
                    help='# of threads (default 4)', type=int, default=4, required=False)  
parser.add_argument('-w', '--out', 
                    help='results output file name', required=False)
parser.add_argument('-b', '--body', 
                    help='print body of search entry', required=False, action='store_true')
parser.add_argument('--debug', 
                    help='debug output', required=False, action='store_true')
parser.add_argument('--nocolor', 
                    help='dont print in colors', required=False, action='store_true')
args = parser.parse_args()

# validate operator is supported
supported_operators = ["site","filetype","intitle","intext","inurl","allintitle","allintext","allinurl"]
if args.operator:
    if args.operator not in supported_operators:
        print("Error: Operator {} not supported".format(args.operator))
        print("Supported: {}".format(supported_operators))
        sys.exit()

# set targets
TARGETS = []
#if only one target was specified, add it to array
if args.target: 
    if args.operator: 
        target = args.operator + ":" + args.target
        TARGETS.append(target)
    else: 
        target = '"' + args.target + '"'
        TARGETS.append(target)

# read in targets from file into an array
if args.target_file: 
    try: 
        f = open(args.target_file, 'r')
    except: 
        print("Error opening target file")
        sys.exit()
    
    for t in f:
        if args.operator: 
            target = args.operator + ":" + t
            TARGETS.append(target.rstrip())
        else: 
            target = '"' + t + '"'
            TARGETS.append(target.rstrip())
    f.close()

PAGES_MAX=args.pages-1  # because page 1 is actually &start=0
                        # page 2 is &start=10, etc

# detect if proxy is an actual proxy or an AWS API gateway endpoint
if "execute-api" in args.proxy: 
    proxy = args.proxy
else: 
    proxy = {
        "http": args.proxy,
        "https": args.proxy
    }

# build queries from targets array and dorkfile array
query_list = []
dork_list = []
DORKFILE = args.dorkfile
dorkfile_in=open(DORKFILE, 'r')
for line in dorkfile_in:
    dork_list.append(line)
dorkfile_in.close()

if TARGETS: # targets specified
    for target in TARGETS: #for each target, run through the dorkfile
        for line in dork_list:
            query_list.append("{} {}".format(target.rstrip(), line.rstrip()))
else: # no targets specified, just a dorkfile
    for line in dork_list:
        query_list.append("{}".format(line.rstrip()))

# number of queries to assign each thread
avg = len(query_list) / float(args.threads)
threaded_query_list = []
last = 0.0
while last < len(query_list):
	threaded_query_list.append(query_list[int(last):int(last + avg)])
	last += avg

threads = []
for query_list in threaded_query_list:
    try:
        t = threading.Thread(target=runQueriesThread, args=(query_list,))
        threads.append(t)
        t.start()
    except:
        print ("Error: unable to start thread")