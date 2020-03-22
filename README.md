# GISAID scrapper
Scrapping tool for GISAID data regarding SARS-CoV-2. You need an active account in order to use it. 

## Preparations
Install all requirements for the scrapper.
```
pip install -r requirements.txt
```
You need to download a ![Firefox WebDriver](https://github.com/mozilla/geckodriver/releases) for your operating system and place it in script's directory.

Your login and password can be provided in `credentials.txt` file in format:
```
login
password
```

## Usage
```
usage: scrap.py [-h] [--username USERNAME] [--password PASSWORD]  
                          [--filename FILENAME] [--destination DESTINATION] 
                          [--headless [HEADLESS]] [--whole [WHOLE]]

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME, -u USERNAME
                        Username for GISAID
  --password PASSWORD, -p PASSWORD
                        Password for GISAID
  --filename FILENAME, -f FILENAME
                        Path to file with credentials (alternative, default:
                        credentials.txt)
  --destination DESTINATION, -d DESTINATION
                        Destination directory (default: fastas/)
  --headless [HEADLESS], -q [HEADLESS]
                        Headless mode (no browser window)
  --whole [WHOLE], -w [WHOLE]
                        Scrap whole genomes only
```
Example:
```
python3 scrap.py -u user -p pass -w
```
run the scrapper with username `user` and password `pass`, downloading only whole sequence data.
```
python3 scrap.py -w -q -d whole_genome
```
run the scrapper in headless mode with username and password read from `credentials.txt`, downloading only whole sequence data
into `whole_genome` directory.

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
The tool has only been tested on windows 10.


## Docker Image
It is also possible to run this scrapper in headless mode inside docker container. This allows to use it on any Operating Sysytem that is able to run Docker. Image created by Pawel Kulig and hosted on his DockerHub. Image is based on Fedora 31 and has all requirements needed to run scrapper already installed. Since password and username have to be provided per user, container has to use volume to load neccessary files. Script in container is by default executed with --headless option. Credentials should be provided in credentials.txt file located in gisaid_scrapper directory.

To download image from DockerHub run:
```
docker pull pawelkulig/gisaid_scrapper
```

To run scrapper in container:
```
docker container run -rm -it -v path_to_gisaid_scrapper_directory:/home pawelkulig/gisaid_scrapper
```

To build Docker Image on your own run below command inside gisaid_scrapper directory:
```
docker build --tag name:tag .
```
geckodriver file inside gisaid_scrapper directory is required to perform this operation.
