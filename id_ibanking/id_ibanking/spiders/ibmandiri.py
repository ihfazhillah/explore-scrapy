# -*- coding: utf-8 -*-
import scrapy


class IbmandiriSpider(scrapy.Spider):
    name = 'ibmandiri'
    allowed_domains = ['ib.bankmandiri.co.id']
    start_urls = ['https://ib.bankmandiri.co.id/retail/Login.do?action=form&lang=in_ID']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IbmandiriSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'userID': self.userID, 'password': self.password},
            formname='LoginForm',
            callback=self.after_login
        )

    def after_login(self, response):
        return scrapy.Request(
            'https://ib.bankmandiri.co.id/retail/Welcome.do?action=result',
            callback=self.parse_welcome
        )

    def parse_welcome(self, response):
        if 'SELAMAT DATANG' not in response.text:
            raise scrapy.exceptions.CloseSpider('Login failed')
        return scrapy.Request(
            'https://ib.bankmandiri.co.id/retail/TrxHistoryInq.do?action=form',
            callback=self.parse_account_id
        )

    def parse_account_id(self, response):
        """parse account id, get the first account id

        :response: TODO
        :returns: TODO

        """
        account_ids = response.css('select[name="fromAccountID"] option::attr("value")')
        account_id = None
        for option in account_ids:
            if option.extract():
                account_id = option.extract()
                break
        if account_id:
            return scrapy.Request(
                'https://ib.bankmandiri.co.id/retail/AccountDetail.do?action=result&ACCOUNTID=%s' % account_id,
                callback=self.parse_check_saldo_page
            )
        raise scrapy.exceptions.CloseSpider('Cannot get account id')

    def parse_check_saldo_page(self, response):
        return {'saldo': response.css('#accbal::text').extract()[0].strip().replace('\xa0', ' ')}

    def spider_idle(self, spider):
        req = scrapy.Request(
            'https://ib.bankmandiri.co.id/retail/Logout.do?action=result',
            callback=self.parse_logout
        )
        self.crawler.engine.crawl(req, spider)

    def parse_logout(self, response):
        pass
