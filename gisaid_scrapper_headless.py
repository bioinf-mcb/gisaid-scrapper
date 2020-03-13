from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
import hashlib
import tqdm
import glob
import os

class GisaidCoVScrapper:
    def __init__(self, headless=False, destination="fastas"):
        options = Options()
        options.headless = headless

        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(1000)

        self.destination = destination
        if not os.path.exists(destination):
            os.makedirs(destination)
        self.already_downloaded = self._read_cache()

    def _read_cache(self):
        res = [i.split("\\")[-1].split(".")[0] for i in glob.glob(f"{self.destination}/*.fasta")]
        return res

    def login(self, username, password):
        self.driver.get("https://platform.gisaid.org/epi3/frontend")
        time.sleep(2)
        login = self.driver.find_element_by_name("login")
        login.send_keys(username)

        passwd = self.driver.find_element_by_name("password")
        passwd.send_keys(password)
        login_box = self.driver.find_element_by_class_name("form_button_submit")

        self.driver.execute_script("document.getElementById('sys_curtain').remove()")
        self.driver.execute_script("document.getElementsByClassName('form_button_submit')[0].click()")
        WebDriverWait(self.driver,30).until(cond.staleness_of(login_box))

    def _go_to_epicov(self):
        time.sleep(2)
        self.driver.execute_script("document.getElementById('sys_curtain').remove()")
        self.driver.find_element_by_link_text("EpiCoV™").click()
        time.sleep(2)
        self.driver.execute_script("document.getElementById('sys_curtain').remove()")
        self.driver.find_elements_by_xpath("//*[contains(text(), 'Browse')]")[0].click()
        time.sleep(2)

        parent_form = self.driver.find_element_by_class_name("sys-form-fi-cb")
        inp = parent_form.find_element_by_tag_name("input")
        inp.click()

    def download_from_curr_page(self):
        time.sleep(2)

        parent_form = self.driver.find_element_by_class_name("yui-dt-data")
        rows = parent_form.find_elements_by_tag_name("tr")
        print(len(rows))
        time.sleep(2)

        for i in tqdm.trange(len(rows)):
            self._download_row(parent_form, i)

    def _action_click(self, element):
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()
        time.sleep(1)

    def _download_row(self, parent_form, row_id):
        row = parent_form.find_elements_by_tag_name("tr")[row_id]
        col = row.find_elements_by_tag_name("td")[1]
        name = row.find_elements_by_tag_name("td")[2].text
        if name in self.already_downloaded:
            return

        self._action_click(col)

        iframe = self.driver.find_elements_by_tag_name("iframe")[0]
        self.driver.switch_to.frame(iframe)
        pre = self.driver.find_elements_by_tag_name("pre")[0]

        fasta = pre.text
        self._save_data(fasta, name)

        self._action_click(self.driver.find_elements_by_tag_name("button")[1])
        self.driver.switch_to.default_content()
        time.sleep(2)

    def go_to_next_page(self):
        self.driver.find_elements_by_xpath("//*[contains(text(), 'next >')]")[0].click()

    def _save_data(self, fasta, name):
        with open(f"{self.destination}/{name}.fasta", "w") as f:
            for line in fasta.upper().split("\n"):
                f.write(line.strip())
                f.write("\n")


with open("credentials.txt") as f:
    login = f.readline()
    passwd = f.readline()

scrapper = GisaidCoVScrapper(True)
scrapper.login(login, passwd)
scrapper._go_to_epicov()

while True:
    scrapper.download_from_curr_page()
    scrapper.go_to_next_page()
