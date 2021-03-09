Step 1: Fireprox to set up AWS API gateway endpoint (https://github.com/ustayready/fireprox): 

```
python fire.py --access_key ZZZZZ --secret_access_key XXXXXXXXX --region us-east-1 --command create --url https://www.google.com
```

Employee scraping: 
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


Search developer/paste sites for information leaks

```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target companyname.com --target-operator intext --dorkfile dorkfiles/dev.txt --out devdorks-results.txt --pages 12
```

Scrape documents for a list of sites: 
```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target-file sitelist.txt --target-operator site --dorkfile dorkfiles/documents-dorkfile.txt --out document-results.txt --pages 12
```

Run through GHDB: 

```
python run.py --proxy https://xxxxxx.execute-api.us-east-1.amazonaws.com/fireprox/ --target "companysite.com" --target-operator site --dorkfile linkedin-companyname-dorkfile.txt
```

* google doesnt usually return more than 300 results, in practice. 
* --debug will print queries being made and URL to page
* remember bash will eat double quotes, be sure to escape them if your target has spaces, ex: --target '"company name"'