# -*- coding: utf-8 -*-
import scrapy


class KompasComSpider(scrapy.Spider):
    name = 'kompas_com'
    allowed_domains = ['kompas.com']
    start_urls = ['https://www.kompas.com/']

    def parse(self, response):
        articles = response.css('.latest .article__list::text').extract()
        yield {'articles': articles}
