# numbeo_webscraping

Welcome to our Numbeo Scraping Project Repository.
The file description.pdf contains detailed description of prepared scrapers.

In folder appendix one will find an analytical dashboard prepared using the scraped data (as Power Bi file and as pdf with views created in the dashboard).

Folders Soup, Scrapy and Selenium consist of files necessary to run and scrape the data. In order to run the scrapers:

Beautiful Soup Scraper:
1) Open Command Prompt
2) set the working directory as the one where is the beautiful soup scraper (numbeo_soup.py)
3) run the command: "python numbeo_soup.py"
4) Wait untill u get message - 'Scraping is done!'
5) Scraping is done :)

Scrapy Scraper:
1) Open Command Prompt
2) Set the current directory as per scrapy project:
"cd C:\Users\rafal\Downloads\scrapy_project\numbeo_project"
3) Run the following command to run the first Spider:
"scrapy crawl link_lists -o link_lists.csv"
4) When the Command Prompt will show that the Spider is closed (INFO: Spider closed (finished)),
run the following command to run the Second Spider:
"scrapy crawl prices  -o dataset.csv"
5) The webscraping part is done!

Selenium Scraper:
1) Open Command Prompt
2) set the working directory as the one where is the selenium scraper (numbeo_selenium.py)
3) run the command: "python numbeo_selenium.py"
4) Wait for the output.
5) Scraping is done :)
