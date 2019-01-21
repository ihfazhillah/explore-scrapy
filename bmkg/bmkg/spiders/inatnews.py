# -*- coding: utf-8 -*-
import scrapy


class InatnewsSpider(scrapy.Spider):
    name = 'inatnews'
    allowed_domains = ['inatnews.bmkg.go.id']
    start_urls = ['https://inatews.bmkg.go.id/light/?act=realtimeev']

    def parse(self, response):
        rows = response.css('table.table tbody tr')

        for row in rows:
            status, tanggal, jam, lintang, bujur, kedalaman, m, mt, region = [
                td.extract() for td in row.css('td *::text')
            ]

            if self.min_magnitude:
                try:
                    min_magnitude = float(self.min_magnitude)
                except Exception as e:
                    print(e)
                if float(m) < min_magnitude:
                    continue

            if self.max_magnitude:
                try:
                    max_magnitude = float(self.max_magnitude)
                except Exception as e:
                    print(e)
                if float(m) > max_magnitude:
                    continue

            yield dict(
                status=status,
                tanggal=tanggal,
                jam=jam,
                lintang=lintang,
                bujur=bujur,
                kedalaman=kedalaman,
                magnitude=m,
                mt=mt,
                region=region
            )
