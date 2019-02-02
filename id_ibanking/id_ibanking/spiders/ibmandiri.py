# -*- coding: utf-8 -*-
import os

import scrapy
from scrapy.loader import ItemLoader

from ..items import IbMandiriBallance, IbMandiriSentence


class IbmandiriSpider(scrapy.Spider):
    name = 'ibmandiri'
    allowed_domains = ['ib.bankmandiri.co.id']
    start_urls = [
        'https://ib.bankmandiri.co.id/retail/Login.do?action=form&lang=in_ID']

    def __init__(self, to_crawl='ballance', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_crawl = to_crawl

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IbmandiriSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(
            spider.spider_idle, signal=scrapy.signals.spider_idle)
        return spider

    def parse(self, response):
        user_id = os.environ['IBMANDIRI_USERID']
        password = os.environ['IBMANDIRI_PASS']
        return scrapy.FormRequest.from_response(
            response,
            formdata={'userID': user_id, 'password': password},
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
        account_ids = response.css(
            'select[name="fromAccountID"] option::attr("value")')
        account_id = None
        for option in account_ids:
            if option.extract():
                account_id = option.extract()
                break
        if account_id:
            if self.to_crawl == 'ballance':
                return scrapy.Request(
                    'https://ib.bankmandiri.co.id/retail/AccountDetail.do?action=result&ACCOUNTID=%s' % account_id,
                    callback=self.parse_check_saldo_page
                )
            else:
                return scrapy.Request(
                    'https://ib.bankmandiri.co.id/retail/TrxHistoryInq.do?action=form',
                    meta={'account_id': account_id},
                    callback=self.post_mutasi_form,
                    dont_filter=True
                )
        raise scrapy.exceptions.CloseSpider('Cannot get account id')

    def post_mutasi_form(self, response):
        account_id = response.meta['account_id']


        data = {
            'fromAccountID': account_id,
            'fromDay': '1',
            'fromMonth': '1',
            'fromYear': '2019',
            'toDay': '31',
            'toMonth': '1',
            'toYear': '2019',
            'action': 'result',
            # 'sortType': 'Date',
            # 'orderBy': 'ASC',
            # 'searchType': 'R',
        }

        return scrapy.FormRequest.from_response(response,
                                                formname='TrxHistoryInqForm',
                                                formdata=data,
                                                callback=self.parse_mutation_page,
                                                # dont_filter=True,
                                                dont_click=True,
                                                meta={'dont_redirect': True}
                                                )

    def parse_mutation_page(self, response):

        # yield {'hello': 'world'}
        # yield {'response': response.text}

        # for row in response.xpath('//table'):
        #     yield {'row': row.extract()}


        for index, row in enumerate(response.xpath('//table[3]//tr')):
            loader = ItemLoader(
                item=IbMandiriSentence(),
                selector=row
            )
            if index == 0:
                continue

            # yield {'hello': row.extract()}
            loader.add_xpath('tanggal', './td[1]/text()')
            loader.add_xpath('keterangan', './td[2]//text()')
            loader.add_xpath('keluar', './td[3]/text()')
            loader.add_xpath('masuk', './td[4]/text()')
            yield loader.load_item()

    def parse_check_saldo_page(self, response):
        il = ItemLoader(item=IbMandiriBallance(), response=response)
        il.add_css('ballance', '#accbal::text')
        return il.load_item()

    def spider_idle(self, spider, *args, **kwargs):
        req = scrapy.Request(
            'https://ib.bankmandiri.co.id/retail/Logout.do?action=result',
            callback=self.parse_logout,
        )
        self.crawler.engine.crawl(req, spider)

    def parse_logout(self, response):
        pass
