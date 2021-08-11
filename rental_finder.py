from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import re
import time
import os
from dotenv import load_dotenv

load_dotenv('.env')
FORM_WEBSITE = 'https://docs.google.com/forms/d/e/1FAIpQLSeFGu0WXtbJs4DpzvwjapTAevSrb-y0L9fuayyoSxc4-ql0Rw/viewform?usp=sf_link'
ZILLOW_WEBSITE = 'https://www.zillow.com/san-francisco-ca/rentals/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22San%20Francisco%2C%20CA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56825484228516%2C%22east%22%3A-122.29840315771484%2C%22south%22%3A37.69044004359946%2C%22north%22%3A37.86004559039139%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20330%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A888096%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D'
MY_HEADERS = {
    'Accept-Language': os.getenv('Accept-Language'),
    'User-Agent': os.getenv('User-Agent')
}


class RentalFinder:
    """
    A class used to scrape 'Zillow' for rental pricing data
    and fill a 'Google Sheet' with the data.

    ...

    Attributes
    ----------
    path : str
        the path to the WebDriver
    response : requests.Response
        a Response object that contains the server's response to the HTTP request
    price_list : list
        a list that contains the pricing data of rentals
    url_list : list
        a list that contains the urls to the rentals
    address_list : list
        a list that contains the addresses of the rentals

    Methods
    -------
    parse_html()
        parses the HTML from the 'Zillow' website and appends data to
        price_list, url_list and address_list
    fill_forms()
        submits the data from the price_list, url_list and address_list into a 'Google Sheet'
    """

    def __init__(self, path):
        """
        Parameters
        ----------
        path : str
            The path to the WebDriver
        """

        self.path = path
        self.response = requests.get(url=ZILLOW_WEBSITE, headers=MY_HEADERS)
        self.response.raise_for_status()
        self.price_list = []
        self.url_list = []
        self.address_list = []
        self.driver = webdriver.Chrome(path)

    def parse_html(self):
        """parses the HTML from the 'Zillow' website and appends data to
        price_list, url_list and address_list
        """

        soup = BeautifulSoup(self.response.text, 'html.parser')
        print(soup.prettify())
        price_elements_list = soup.select('.list-card-price')
        for element in price_elements_list:
            price = element.getText()
            regular_expression = re.compile(r'(\d,)?\d\d\d')
            match = regular_expression.search(price)
            price = match.group()
            if len(price) == 5:
                split_list = re.split(r'\D', price)
                price = ''.join(split_list)
            self.price_list.append(price)
        address_elements_list = soup.select('.list-card-addr')
        for element in address_elements_list:
            address = element.getText()
            self.address_list.append(address)
        link_elements_list = soup.select('.list-card-link')
        for element in link_elements_list[0::2]:
            link = element.get('href')
            if link.startswith('https'):
                self.url_list.append(link)
            else:
                self.url_list.append(f'https://www.zillow.com/{link}')
        # print(len(self.url_list))
        # print(len(self.address_list))
        # print(len(self.price_list))

    def fill_forms(self):
        """submits the data from the price_list, url_list and address_list into a 'Google Sheet'
        """

        self.driver.get(FORM_WEBSITE)
        time.sleep(3)
        for i in range(len(self.url_list)):
            address_input_element = self.driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
            price_input_element = self.driver.find_element_by_css_selector('#mG61Hd > div.freebirdFormviewerViewFormCard.exportFormCard > div > div.freebirdFormviewerViewItemList > div:nth-child(2) > div > div > div.freebirdFormviewerComponentsQuestionTextRoot > div > div.quantumWizTextinputPaperinputMainContent.exportContent > div > div.quantumWizTextinputPaperinputInputArea > input')
            link_input_element = self.driver.find_element_by_css_selector('#mG61Hd > div.freebirdFormviewerViewFormCard.exportFormCard > div > div.freebirdFormviewerViewItemList > div:nth-child(3) > div > div > div.freebirdFormviewerComponentsQuestionTextRoot > div > div.quantumWizTextinputPaperinputMainContent.exportContent > div > div.quantumWizTextinputPaperinputInputArea > input')
            address_input_element.send_keys(self.address_list[i])
            price_input_element.send_keys(self.price_list[i])
            link_input_element.send_keys(self.url_list[i])
            submit_element = self.driver.find_element_by_css_selector('#mG61Hd > div.freebirdFormviewerViewFormCard.exportFormCard > div > div.freebirdFormviewerViewNavigationNavControls > div.freebirdFormviewerViewNavigationButtonsAndProgress > div > div')
            submit_element.click()
            time.sleep(2)
            submit_another_response_element = self.driver.find_element_by_css_selector('body > div.freebirdFormviewerViewFormContentWrapper > div:nth-child(2) > div.freebirdFormviewerViewFormCard.exportFormCard > div > div.freebirdFormviewerViewResponseLinksContainer > a')
            submit_another_response_element.click()
            time.sleep(2)