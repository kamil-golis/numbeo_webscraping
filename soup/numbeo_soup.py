################################################################################
# Scraping the Numbeo Site using Beautiful Soup                                #
################################################################################

# import appropriate libraries
from urllib import request
from bs4 import BeautifulSoup as BS
import re
import pandas as pd
import time

# below a boolean parameter which determines how many pages are scraped:
# True - default - scrape first 100 links
# False - scrape all links
limit_scraper = True

# Define the main url from which we are going to gather appropriate information:
# The choosen webpage is numbeo, which gathers information about costs of living across different countries.
# The data is based on surveys delievered by the users.
url = 'https://www.numbeo.com/cost-of-living/' 
html = request.urlopen(url)
bs = BS(html.read(), 'html.parser')

################################################################################
# prepare list of countries, which we are going to scrape information about    #
################################################################################

# prepare list with links, which we are going to scrape the cost information from
tags = bs.find('div', {'class':'small_font links_for_countries'}).find_all('a')

#links = [url + tag['href'] for tag in tags]                            # version with domestic currency - possible, not applicable here
links = [url + tag['href'] + '&displayCurrency=USD' for tag in tags]    # version with standardised currency (here USD), used to compare different countries

# prepare list of countries in order to put them into the result dataframe
list_countries = []
for tag in tags:
    list_countries.append(tag['href'].split("=",1)[1].replace("+","_"))

# one exception - kosovo - let's clean this one manually:
for i in range(len(list_countries)):
    if list_countries[i] == 'Kosovo_%28Disputed_Territory%29':
        list_countries[i] = list_countries[i].replace("Kosovo_%28Disputed_Territory%29","Kosovo")
    else:
        next


################################################################################
# scrape information about prices in different countries                       #
################################################################################

# prepare empty lists to put the scraped information
countries   = []
products    = []
prices      = []
ranges      = []
min_prices  = []
max_prices  = []

# prepare a variable informing how many pages are going to be scraped - depends on the limit_scraper boolean variable
if limit_scraper == True:
    pages = range(100)
else:
    pages = range(len(links))

# run through each of the countries present in numbeo.com or through first 100 pages
for i in pages:

    # open the appropriate link
    html = request.urlopen(links[i])
    bs = BS(html.read(), 'html.parser')

    # extract table and elements with relevant info about prices of different products:
    table = bs.find('table', {'class':'data_wide_table new_bar_table'}) # table with all informations - to gather info about product names
    prices_html = table.find_all('span', {'class':'first_currency'})    # elements to gather info about prices
    ranges_html = table.find_all('td', {'class':'priceBarTd'})          # elements to gather info about price ranges

    # extract lists of elements containing pattern appropriate for products:
    for element in table:
        element_to_be = element.text
        element_rdy = re.findall(".+?(?=(?:\d+\.\d+.\$|\d+,\d+\.\d+.\$|\?))|Mortgage.*Fixed-Rate", element_to_be)
        # for each prepared list, append to the product list the elements of length > 3 (condition set to get rid of empty strings)
        # additionally, once a product is added, also add a country name to list with countries that are going to be put in the 
        # result dataframe - in order to assure the appropriate structure (all products assigned to each of the countries)
        for elem in element_rdy:
            if len(elem) > 3:
                products.append(elem.strip())
                countries.append(list_countries[i])


    # extract lists of elements containing pattern appropriate for prices:
    for element in prices_html:
        element_to_be = element.text
        if element_to_be == '':
            prices.append('')       # condition for empty elements - additional security check
        else:
            element_rdy = re.findall("(?:\d{1,9}.\d{1,9}|\d{1,9},\d{1,9}.\d{1,9}|\?)", element_to_be) # pattern to find prices
            # for each extracted list,, extract and append an appropriate price value 
            for elem in element_rdy:    
                if elem == '?':          # null values for prices are denoted as '?' - let's put them into list as '' to get a 
                                         # homogeneous datatype in a resulting column
                    prices.append('')
                else:
                    prices.append(elem.replace(',','')) # delete commas from big numbers (values in thousands, e.g. 27,000) 

    # extract lists of elements containing pattern appropriate for price ranges:
    for element in ranges_html:
        element_to_be = element.text
        # price ranges are a specific case - in order to catch nulls, we have to specify both '', and '\n'
        # additionally, we would like to store information about min and max prices from the range,
        if element_to_be in ('', '\n') :
            ranges.append('')
            min_prices.append('')
            max_prices.append('')
        else:
            element_rdy = re.findall("(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})-(?:\d{1,9},\d{1,9}\.\d{1,9}|\d{1,9}\.\d{1,9})", element_to_be)
            # for each extracted list,, extract and append an appropriate price range/ min and max value
            for elem in element_rdy:
                ranges.append(elem.replace(',',''))     # again, get rid of commas from numbers
                min, max = elem.split("-")              # spit the range into min and max prices
                min_prices.append(min.replace(',',''))  # again, get rid of commas from numbers
                max_prices.append(max.replace(',',''))  # again, get rid of commas from numbers

    time.sleep(2)   # let's take some rest between scraped websites  


################################################################################
# construct the result dataframe                                               #
################################################################################

# transform the lists with results into dataframes
df_countries    = pd.DataFrame(countries, columns =['country'])
df_products     = pd.DataFrame(products, columns =['product'])
df_prices       = pd.DataFrame(prices, columns =['price'])
df_ranges       = pd.DataFrame(ranges, columns =['range'])
df_min          = pd.DataFrame(min_prices, columns =['min'])
df_max          = pd.DataFrame(max_prices, columns =['max'])

# concat resulting dataframes into the final one
df_final= pd.concat([df_countries, df_products, df_prices, df_ranges, df_min, df_max], axis=1)

# save the data frame into csv file
df_final.to_csv('dataset.csv')

# get a message after saving the dataframe to get to know that everything worked just fine
print('Scraping is done!')