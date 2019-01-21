# -*- coding: utf-8 -*-
import scrapy


class InfokomputerGridSpider(scrapy.Spider):
    name = 'infokomputer_grid'
    allowed_domains = ['infokomputer.grid.id']
    start_urls = ['http://infokomputer.grid.id/']

    def parse(self, response):
        articles = response.css('.main__content--title::text').extract()
        yield {'articles': articles}
        pass
