# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib


class IdIbankingPipeline(object):
    def process_item(self, item, spider):
        return item


class IdIbankingHashPipeline(object):
    def process_item(self, item, spider):
        to_hash = '%s;%s;%s;%s' %(item['tanggal'], item['keterangan'], item['keluar'], item['masuk'])
        item['hash_id'] = hashlib.md5(to_hash.encode()).hexdigest()
        return item


class IdIbankingParseFloatPipeline(object):
    def process_item(self, item, spider):

        """parse masuk & keluar to be float"""
        def parse_(string):
            return float(string.replace('.', '').replace(',', '.'))


        item['masuk'] = parse_(item['masuk'])
        item['keluar'] = parse_(item['keluar'])

        item['ballance'] = spider.last_ballance
        return item


class AddBallancePipeline(object):
    def process_item(self, item, spider):
        spider.last_ballance -= item['keluar']
        spider.last_ballance += item['masuk']
        item['ballance'] = spider.last_ballance
        return item

