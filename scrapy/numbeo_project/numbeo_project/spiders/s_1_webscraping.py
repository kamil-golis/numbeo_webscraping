# -*- coding: utf-8 -*-
import scrapy

class Link_l(scrapy.Item):
    link_l = scrapy.Field()

class LinkListsSpider(scrapy.Spider):
    name = 'link_lists'
    allowed_domains = ['https://www.numbeo.com/']
    start_urls = ['https://www.numbeo.com/cost-of-living/']

    def parse(self, response):
        xpath = '//div[contains(@class, "small_font links_for_countries")]//a/@href'
        selection = response.xpath(xpath)
        for s in selection:
            l = Link_l()
            # display same currency for all countries: here USD:
            l['link_l'] = 'https://www.numbeo.com/cost-of-living/' + s.get() + '&displayCurrency=USD'
            yield l





