# -*- coding: utf-8 -*-
import scrapy
from stockphotos.items import StockphotosItem


class BurstShopifySpider(scrapy.Spider):
    name = 'burst_shopify'
    allowed_domains = ['burst.shopify.com']
    start_urls = ['https://burst.shopify.com/photos']

    def parse(self, response):
        next_page = response.xpath("//span[@class='next']/a/@href").get()

        if next_page:
            yield response.follow(next_page, self.parse)

        photos = response.xpath("//div[@class='photo-tile']//img/@src").extract()
        photos_urls = [p.replace("70x.progressive", "4460x4460") for p in photos]
        item = StockphotosItem()
        item['image_urls'] = photos_urls
        yield item
