Extract hostnames from Google search results, using Fireprox AWS API gateway: 

Writes to stdout

1 domain: 
```
python google-hostnames.py -d example.com --proxy https://XXXXX.execute-api.us-east-1.amazonaws.com/fireprox/
```

Many domains: 

```
python google-hostnames.py -f file-with-domains.txt --proxy https://XXXXX.execute-api.us-east-1.amazonaws.com/fireprox/
```