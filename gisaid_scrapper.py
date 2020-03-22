from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import NoAlertPresentException, MoveTargetOutOfBoundsException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
import tqdm
import glob
import os
import sys
from urllib3.exceptions import MaxRetryError

METADATA_COLUMNS = [
    "Accession",
    "Collection date",
    "Location",
    "Host",
    "Additional location information",
    "Gender",
    "Patient age",
    "Patient status",
    "Specimen source",
    "Additional host information",
    "Outbreak",
    "Last vaccinated",
    "Treatment",
    "Sequencing technology",
    "Assembly method",
    "Coverage",
    "Comment",
    "Length"
]


class GisaidCoVScrapper:
    def __init__(
        self,
        headless: bool = False,
        whole_genome_only: bool = True,
        destination: str = "fastas"
    ):
        self.whole_genome_only = whole_genome_only

        self.destination = destination
        self.finished = False
        self.already_downloaded = 0
        self.samples_count = None
        self.new_downloaded = 0

        options = Options()
        options.headless = headless
        if headless and "DOCKER_MODE" in os.environ:
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            for i in range(30):
                time.sleep(1)
                try:
                    self.driver = webdriver.Remote(
                        command_executor="http://selenium:4444/wd/hub",
                        desired_capabilities=options.to_capabilities()
                    )
                    break
                except MaxRetryError:
                    pass

        else:
            self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(1000)
        self.driver.set_window_size(1366, 2000)

        if not os.path.exists(destination):
            os.makedirs(destination)

        self._update_cache()
        if os.path.isfile(destination + "/metadata.tsv"):
            self.metadata_handle = open(
                destination + "/metadata.tsv", "a", encoding='utf-8')
        else:
            self.metadata_handle = open(
                destination + "/metadata.tsv", "w", encoding='utf-8')
            self.metadata_handle.write("\t".join(METADATA_COLUMNS) + "\n")

    def login(self, username: str, password: str):
        self.driver.get("https://platform.gisaid.org/epi3/frontend")
        time.sleep(5)
        login = self.driver.find_element_by_name("login")
        login.send_keys(username)

        passwd = self.driver.find_element_by_name("password")
        passwd.send_keys(password)
        login_box = self.driver.find_element_by_class_name(
            "form_button_submit")

        self.driver.execute_script(
            "document.getElementById('sys_curtain').remove()")
        self.driver.execute_script(
            "document.getElementsByClassName('form_button_submit')[0].click()"
        )
        WebDriverWait(self.driver, 30).until(cond.staleness_of(login_box))

    def load_epicov(self):
        time.sleep(2)
        self._go_to_seq_browser()

        if self.whole_genome_only:
            time.sleep(2)
            parent_form = self.driver.find_element_by_class_name(
                "sys-form-fi-cb")
            inp = parent_form.find_element_by_tag_name("input")
            inp.click()
            time.sleep(5)

        self._update_metainfo()

    def _go_to_seq_browser(self):
        self.driver.execute_script(
            "document.getElementById('sys_curtain').remove()")
        self.driver.find_element_by_link_text("EpiCoV™").click()

        time.sleep(3)

        self.driver.execute_script(
            "document.getElementById('sys_curtain').remove()")
        self.driver.find_elements_by_xpath(
            "//*[contains(text(), 'Browse')]")[0].click()

    def _update_metainfo(self):
        self.samples_count = int(
            self.driver.find_elements_by_xpath("//*[contains(text(), 'Total:')]")[
                0
            ].text.split(" ")[1].replace(",", "")
        )
        self._update_cache()

    def _update_cache(self):
        res = [
            i.split("/")[-1].split(".")[0]
            for i in glob.glob(f"{self.destination}/*.fasta")
        ]
        self.already_downloaded = res

        if self.samples_count is not None:
            samples_left = self.samples_count - len(res)
            if samples_left > 0:
                print(samples_left, "samples left")
                self.finished = False
            else:
                self.finished = True
                print("Finished!")

    def download_from_curr_page(self):
        time.sleep(1)

        parent_form = self.driver.find_element_by_class_name("yui-dt-data")
        rows = parent_form.find_elements_by_tag_name("tr")
        time.sleep(2)

        for i in tqdm.trange(len(rows)):
            self._download_row(parent_form, i)

    def _download_row(self, parent_form, row_id):
        row = parent_form.find_elements_by_tag_name("tr")[row_id]
        col = row.find_elements_by_tag_name("td")[1]
        name = row.find_elements_by_tag_name("td")[2].text
        if name in self.already_downloaded:
            return

        self._action_click(col)

        iframe = self.driver.find_elements_by_tag_name("iframe")[0]

        self._save_data(iframe, name)

        self._action_click(self.driver.find_elements_by_tag_name("button")[1])
        self.driver.switch_to.default_content()
        time.sleep(1)

        self.new_downloaded += 1

    def _save_data(self, iframe, name):
        self.driver.switch_to.frame(iframe)
        time.sleep(2)
        pre = self.driver.find_elements_by_tag_name("pre")[0]
        fasta = pre.text
        if self.whole_genome_only:
            if len(fasta) < 29000:
                print("Full sequence was not downloaded, rerun will be needed")
        # Handle metadata
        metadata = self.driver.find_elements_by_xpath(
            "//b[contains(text(), 'Sample information')]/../../following-sibling::tr"
        )[:16]

        res = f"{name}\t"
        for line in metadata:
            try:
                info = line.text.split(":")[1].strip().replace("\n", "")
                res += info
                res += "\t"
            except IndexError:
                res += "\t"
        res += str(len(fasta))
        self.metadata_handle.write(res + "\n")

        # Save FASTA
        with open(f"{self.destination}/{name}.fasta", "w") as f:
            header = fasta.split("\n")[0]
            f.write(header.strip()+"\n")
            for line in fasta.split("\n")[1:]:
                f.write(line.strip().upper())
                f.write("\n")

    def _scroll_shim(self, element):
        x = element.location['x']
        y = element.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        self.driver.execute_script(scroll_by_coord)
        self.driver.execute_script(scroll_nav_out_of_way)

    def _action_click(self, element):
        action = ActionChains(self.driver)
        try:
            action.move_to_element(element).perform()
            element.click()
        except MoveTargetOutOfBoundsException:
            self._scroll_shim(element)
            action.move_to_element(element).perform()
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script(
                "document.getElementById('sys_curtain').remove()")
            action.move_to_element(element).perform()
            element.click()

    def go_to_next_page(self):
        try:
            self.driver.find_element_by_xpath(
                "//*[contains(text(), 'next >')]").click()
        except ElementClickInterceptedException:
            self.driver.execute_script(
                "document.getElementById('sys_curtain').remove()")
            self.driver.find_element_by_xpath(
                "//*[contains(text(), 'next >')]").click()
        self._update_metainfo()
