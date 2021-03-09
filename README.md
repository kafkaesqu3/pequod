## Fireprox
Step 1: Fireprox to set up AWS API gateway endpoint (https://github.com/ustayready/fireprox): 

```
python fire.py --access_key ZZZZZ --secret_access_key XXXXXXXXX --region us-east-1 --command create --url https://www.google.com
```

## Employee scraping: 
```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --dorkfile companyname-dorkfile.txt
```

For linkedin, dorkfile should look like this: 

```
site:linkedin.com/in sales at companyname
site:linkedin.com/in hr at companyname
site:linkedin.com/in accounting at companyname
site:linkedin.com/in finance at companyname
...
````

For zoominfo, the dorkfile should look like: 
```
site:zoominfo.com/p/ engineer intitle:"companyname" Employee Profiles
site:zoominfo.com/p/ developer intitle:"companyname" Employee Profiles
site:zoominfo.com/p/ devops intitle:"companyname" Employee Profiles
```


## Search developer/paste sites for information leaks

```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target companyname.com --target-operator intext --dorkfile dorkfiles/dev.txt --out devdorks-results.txt --pages 12
```

## Scrape documents directly from a list of sites: 
```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target-file sitelist.txt --target-operator site --dorkfile dorkfiles/documents-dorkfile.txt --out document-results.txt --pages 12
```

## Subdomain scraping
Extract hostnames from Google search results, using Fireprox AWS API gateway: 

Writes to stdout

1 domain: 
```
cd HostnameDork/
python google-hostnames.py -d example.com --proxy https://XXXXX.execute-api.us-east-1.amazonaws.com/fireprox/
```

Many domains: 

```
python google-hostnames.py -f file-with-domains.txt --proxy https://XXXXX.execute-api.us-east-1.amazonaws.com/fireprox/
```

## GHDB

Run scraper to update ghdb.sqlite with latest dorks from Google Hacking Database https://www.exploit-db.com/google-hacking-database

```
scrape-ghdb.py
```

Generate dorkfiles from sqlite db: 
```
$ python generate-dorkfile.py
ghdb-Files_Containing_Juicy_Info.txt: 913 entries
ghdb-Pages_Containing_Login_Portals.txt: 1089 entries
ghdb-Sensitive_Directories.txt: 422 entries
ghdb-Web_Server_Detection.txt: 167 entries
ghdb-Various_Online_Devices.txt: 574 entries
ghdb-Advisories_and_Vulnerabilities.txt: 2203 entries
ghdb-Files_Containing_Passwords.txt: 364 entries
ghdb-Footholds.txt: 119 entries
ghdb-Error_Messages.txt: 123 entries
ghdb-Network_or_Vulnerability_Data.txt: 104 entries
ghdb-Vulnerable_Servers.txt: 106 entries
ghdb-Files_Containing_Usernames.txt: 39 entries
ghdb-Sensitive_Online_Shopping_Info.txt: 11 entries
ghdb-Vulnerable_Files.txt: 67 entries
```

Find login portals: 

```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target companysite.com --target-operator site --dorkfile dorkfiles/ghdb/ghdb-Pages_Containing_Login_Portals.txt
```

## Search file share sites for documents mentioning a company

```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target '"company name"' --target-operator intitle --dorkfile dorkfiles/document-hosting.txt
```

## Misc notes

* google doesnt usually return more than 300 (30 pages) results, in practice. 
* --debug will print queries being made and URL to page
* remember bash will eat double quotes, be sure to escape them if your target has spaces, ex: --target '"company name"'

## Dork files

### analysis.txt

Domain analysis sites (urlscan, censys, etc)

### cloud.txt

Cloud hosting sites

### developer.txt

Code sharing, paste sites (pastebin, gists, etc)

### document-hosting.txt

Sites that host documents

### documents.txt

Document filetypes

### edu.txt

Online trainings/universities

### file-storage.txt

File storage websites

### filetype.txt

Interesting filetypes

### forms.txt

Forms, surveys, etc

### ghdb/

Dorks from google hacking database

### linkedin-titles.txt

Common job titles for tuning scrapes of Linkedin, Zoominfo, etc

### meetings.txt

Conferecing/meeting URLs

### orgs.txt

Dorks to uncover information about an organization

### other.txt

Misc

### shorteners.txt

URL shorteners

### social.txt

Social media sites

### trello.txt

Trello boards
