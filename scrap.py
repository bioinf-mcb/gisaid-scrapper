import argparse, sys
from gisaid_scrapper import GisaidCoVScrapper
import os

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--username', '-u', help="Username for GISAID", type=str)
    parser.add_argument('--password', '-p', help="Password for GISAID", type=str)
    parser.add_argument('--filename', '-f', help="Path to file with credentials (alternative, default: credentials.txt)", type=str, default="credentials.txt")
    parser.add_argument('--destination', '-d', help="Destination directory (default: fastas/)", type=str, default="fastas/")
    parser.add_argument('--headless', '-q', help="Headless mode of scraping (experimental)", type=str2bool, nargs='?', default=False)
    parser.add_argument('--whole', '-w', help="Scrap whole genomes only", type=str2bool, nargs='?', default=False)

    args = parser.parse_args()
    args.headless = True if args.headless is None else args.headless
    args.whole = True if args.whole is None else args.whole  
    return parser, args

def get_credentials(args):
    if "DOCKER_MODE" in os.environ:
        login = os.getenv("GISAID_USER")
        passwd = os.getenv("GISAID_PASS")
        destination = os.getenv("DESTINATION")
        whole = os.getenv("WHOLE_GENOME")==1
    else:
        if args.username is None or args.password is None:
            if args.filename is None:
                raise ValueError
            try:
                with open(args.filename) as f:
                    login = f.readline()
                    passwd = f.readline()
            except FileNotFoundError:
                print("File not found.")
                raise ValueError
        else:
            login = args.username
            passwd = args.password

        whole = args.whole
        destination = args.destination


    return login, passwd, whole, destination

if __name__ == "__main__":
    parser, args = parse_args()
        
    try:
        login, passwd, whole, destination = get_credentials(args)
    except ValueError:
        print(parser.format_help())
        sys.exit(-1)
    scrapper = GisaidCoVScrapper(args.headless, whole, destination)
    scrapper.login(login, passwd)
    # scrapper.load_epicov()
    # page = 0

    # for i in range(150):
    #     scrapper.go_to_next_page()
    #     page += 1

    # while not scrapper.finished:
    #     print("Page:", page)
    #     scrapper.download_from_curr_page()
    #     scrapper.go_to_next_page()
    #     page += 1

    scrapper.download_packages('metadata_tsv')
    scrapper.download_packages('fasta.tar')
    print("New samples:", scrapper.new_downloaded)