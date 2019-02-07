# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import json
from ibanking.models import ScrapyItem


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


class DjangoItemPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                unique_id=crawler.settings.get('unique_id')
        )

    def close_spider(self, spider):
        item = ScrapyItem()
        item.unique_id = self.unique_id
        item.data = json.dumps(self.items)
        item.save()

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

