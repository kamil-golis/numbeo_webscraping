from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import pandas as pd
import re




# Init:
gecko_path = '/opt/homebrew/bin/geckodriver'
ser = Service(gecko_path)
options = webdriver.firefox.options.Options()
options.headless = False
driver = webdriver.Firefox(options = options, service=ser)

url = 'https://www.numbeo.com/cost-of-living/'

driver.get(url)

my_countries = driver.find_elements(By.XPATH,"//td/a")
#The first link needs to be removed
my_countries = my_countries[1:]

limit_scraper = True
if limit_scraper == True:
    my_countries = my_countries[:101]


temp_list = []
temp_list_2 = []
temp_list_3 = []
temp_list_4 = []
temp_list_5 = []
min_price = []
max_price = []
ranges      = []
mortgage = []


for my_elem in my_countries:
        # driver = webdriver.Firefox(executable_path=r'C:\Users\rafal\AppData\Local\Programs\Python\Python310\geckodriver.exe')
        driver = webdriver.Firefox(options=options, service=ser)
        time.sleep(2)
        driver.get(my_elem.get_attribute("href") + '&displayCurrency=USD')

        table = driver.find_elements(By.XPATH,"//html/body/div[2]/table/tbody/tr")

        table_ranges_2 = driver.find_elements(By.XPATH,"/html/body/div[2]/table/tbody/tr/td[3]")

        table_prices = driver.find_elements(By.XPATH,"/html/body/div[2]/table/tbody/tr/td[2]/span")
        for l in table_prices:
            temp_list_prices = l.text

            price = re.findall("(?:\d{1,9}.\d{1,9}|\d{1,9},\d{1,9}.\d{1,9}|\?)", temp_list_prices)
            for y in price:
                if y=='?':
                    temp_list_3.append('')
                else:
                    temp_list_3.append(y.replace(',', ''))

        for x in table_ranges_2:
            temp_list_ranges = x.text
            if temp_list_ranges in ('', '\n'):
                ranges.append('')
                min_price.append('')
                max_price.append('')
            else:
                variance = re.findall("(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})-(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})",temp_list_ranges)
                # for each extracted list,, extract and append an appropriate price range/ min and max value
                for z in variance:
                    ranges.append(z.replace(',', ''))  # again, get rid of commas from numbers
                    min, max = z.split("-")  # spit the range into min and max prices
                    min_price.append(min.replace(',', ''))  # again, get rid of commas from numbers
                    max_price.append(max.replace(',', ''))  # again, get rid of commas from numbers

        for elems in table:
            temp_list = elems.text

            name = re.findall(".+?(?=(?:\d+\.\d+.\$|\d+,\d+\.\d+.\$|\?))|Mortgage.*Fixed-Rate", temp_list)
            for x in name:
                if len(x) > 3:
                    temp_list_2.append(x.strip())
                    if my_elem.text == "Kosovo (Disputed Territory)":
                        temp_list_5.append(my_elem.text.replace(" (Disputed Territory)", ""))
                    else:
                        temp_list_5.append(my_elem.text.replace(" ", "_"))


        driver.quit()

df_1 = pd.DataFrame(temp_list_2, columns =['product'])
df_2 = pd.DataFrame(temp_list_3, columns =['price'])
df_3 =  pd.DataFrame(temp_list_4)
df_4 = pd.DataFrame(temp_list_5, columns =['country'])
d_ranges = pd.DataFrame(ranges, columns =['range'])
d_min_price = pd.DataFrame(min_price, columns =['min'])
d_max_price = pd.DataFrame(max_price, columns =['max'])
df_test = pd.concat([df_4, df_1, df_2, d_ranges, d_min_price, d_max_price], axis=1)

df_test.to_csv('dataset.csv')

driver.quit()



