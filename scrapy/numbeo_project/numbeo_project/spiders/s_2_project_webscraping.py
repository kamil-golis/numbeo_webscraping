# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd

import re


def close(self, reason):
    start_time = self.crawler.stats.get_value('start_time')
    finish_time = self.crawler.stats.get_value('finish_time')
    print("Total run time: ", finish_time - start_time)

# These options allow to show all columns and rows in the output
pd.options.display.width = None
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', -1)

# below a boolean parameter which determines how many pages are scraped:
# True - default - scrape first 100 links
# False - scrape all links
limit_scraper = True



class LinksSpider(scrapy.Spider):
    name = 'prices'
    allowed_domains = ['https://www.numbeo.com/cost-of-living/']


    try:
        with open("link_lists.csv", "rt") as f:
            if limit_scraper == True:

                start_urls = [url.strip() for url in f.readlines()][1:101]
            else:
                start_urls = [url.strip() for url in f.readlines()][1:]
    except:
        start_urls = []


    def parse(self, response):
        countries = []
        products = []
        prices = []
        ranges = []
        min_prices = []
        max_prices = []


        #The content of a site is collected by Beautiful Soup library.
        soup = BeautifulSoup(response.text, 'lxml')
        content = soup.find_all()

        #The name of a given country is scraped
        country_name_html = soup.find_all('a', {'class': 'breadcrumb_link'})  # <span itemprop="name">Afghanistan</span>
        for x in country_name_html:
            c_name = x.text

        #The name of a country is replicated to prepare a
        countries = [c_name]*55

        table = soup.find('table', {'class': 'data_wide_table new_bar_table'})
        prices_html = table.find_all('span', {'class': 'first_currency'})  # elements to gather info about prices
        ranges_html = table.find_all('td', {'class': 'priceBarTd'})

        for element in table:
            element_to_be = element.text
            element_rdy = re.findall(".+?(?=(?:\d+\.\d+.\$|\d+,\d+\.\d+.\$|\?))|Mortgage.*Fixed-Rate", element_to_be)
            # for each prepared list, append to the product list the elements of length > 3 (condition set to get rid of empty strings)
            # additionally, once a product is added, also add a country name to list with countries that are going to be put in the
            # result dataframe - in order to assure the appropriate structure (all products assigned to each of the countries)
            for elem in element_rdy:
                if len(elem) > 3:
                    products.append(elem.strip())

        for element in prices_html:
            element_to_be = element.text
            if element_to_be == '':
                prices.append('')  # condition for empty elements - additional security check
            else:
                element_rdy = re.findall("(?:\d{1,9}.\d{1,9}|\d{1,9},\d{1,9}.\d{1,9}|\?)",
                                         element_to_be)  # pattern to find prices
                # for each extracted list,, extract and append an appropriate price value
                for elem in element_rdy:
                    if elem == '?':  # null values for prices are denoted as '?' - let's put them into list as '' to get a
                        # homogeneous datatype in a resulting column
                        prices.append('')
                    else:
                        prices.append(
                            elem.replace(',', ''))  # delete commas from big numbers (values in thousands, e.g. 27,000)

        for element in ranges_html:
            element_to_be = element.text
            # print(element.text)
            # price ranges are a specific case - in order to catch nulls, we have to specify both '', and '\n'
            # additionally, we would like to store information about min and max prices from the range,
            if element_to_be in ('', '\n'):
                ranges.append('')
                min_prices.append('')
                max_prices.append('')
            else:
                element_rdy = re.findall(
                    "(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})-(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})",
                    element_to_be)
                # for each extracted list,, extract and append an appropriate price range/ min and max value
                for elem in element_rdy:
                    ranges.append(elem.replace(',', ''))  # again, get rid of commas from numbers
                    min, max = elem.split("-")  # spit the range into min and max prices
                    min_prices.append(min.replace(',', ''))  # again, get rid of commas from numbers
                    max_prices.append(max.replace(',', ''))  # again, get rid of commas from numbers

        df_countries = pd.DataFrame(countries, columns=['country'])
        df_products = pd.DataFrame(products, columns=['product'])
        df_prices = pd.DataFrame(prices, columns=['price'])
        df_ranges = pd.DataFrame(ranges, columns=['range'])
        df_min = pd.DataFrame(min_prices, columns=['min'])
        df_max = pd.DataFrame(max_prices, columns=['max'])
        df_final = pd.concat([df_countries,df_products, df_prices, df_ranges, df_min, df_max], axis=1)
        

        #The final output is exported as a merged dataframe:
        yield {'name': df_final.copy()}
