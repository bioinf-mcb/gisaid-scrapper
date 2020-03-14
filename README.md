# GISAID scrapper
Scrapping tool for GISAID data regarding SARS-CoV-2. You need an active account in order to use it. 

## Preparations
Install all requirements for the scrapper.
```
pip install -r requirements.txt
```
You need to download a ![Firefox WebDriver](https://github.com/mozilla/geckodriver/releases) for your operating system and place it in script's directory.

Your login and password should be provided in `credentials.txt` file in format:
```
login
password
```

## Usage
```
python3 gisaid_scrapper.py
```
should run the scrapper. If you need a headless mode, you can specify it 
by changing `False` to `True` in the line `scrapper = GisaidCoVScrapper(False)`

## Result
The whole and partial genom sequences from GISAID will be downloaded into `fastas/` directory. `metadata.tsv` file will also be created, containing following information for every sample:

* Accession
* Collection date	
* Location	
* Host	
* Additional location information	
* Gender	
* Patient age	
* Patient status	
* Specimen source	
* Additional host information	
* Outbreak	
* Last vaccinated	
* Treatment	
* Sequencing technology	
* Assembly method	
* Coverage	
* Comment	
* Length

as long as they were provided.
You can interrupt the download and resume it later, the samples won't be downloaded twice. 


The tool was written for personal use, so little to no maintenance is to be expected.
