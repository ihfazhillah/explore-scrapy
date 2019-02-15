# -*- coding: utf-8 -*-
import scrapy


class JsonResponseSpider(scrapy.Spider):
    name = 'json_response'
    allowed_domains = ['motyar.info']
    start_urls = ['http://motyar.info/webscrapemaster/api/?url=http://testing-ground.scraping.pro/blocks&xpath=//div[@id=case1]//div[@class=%27name%27]']

    def parse(self, response):
        yield from response.json()
