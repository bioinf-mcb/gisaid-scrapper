# GISAID scrapper
Scrapping tool for GISAID data regarding SARS-CoV-2. You need an active account in order to use it. 

Your login and password should be provided in `credentials.txt` file in format:
```
login
password
```

## Usage
`python3 gisaid_scrapper_headless.py` should run the scrapper in headless mode. If you need a browser window, you can specify it 
by changing `False` to `True` in the line `scrapper = GisaidCoVScrapper(False)`
