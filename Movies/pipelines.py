# -*- coding: utf-8 -*-
import hashlib
# from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

from Movies.PostgreSQL import PostgreSQL
from Movies.items import YupItem
from Movies.settings import db,path

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class MoviesPipeline(object):
#     def process_item(self, item, spider):
#         return item

class YupPipeline(object):
    """docstring for YupPipeline"""
    def __init__(self):
        self.pg = PostgreSQL(db)

    def process_item(self, item, spider):
        data = dict(
                title = item['title'],
                year = item['year'],
                url = item['url'],
                imdb = item['imdb'],
                site = item['site'],
            )
        mid = self.pg.insert('res_site',data)
        for i in item['res']:
            i['mid'] = mid
            self.pg.insert('res_files',i)

        fileName = hashlib.md5(item['poster'].encode('utf8')).hexdigest()

        data = dict(
            site = item['site'],
            resource = item['poster'],
            filename = '%s/%s.jpg' % (item['site'],fileName),
            type = 'poster',
            mid = mid,
            classes = 'resource'
            )
        self.pg.insert('res_img',data)

    def close_spider(self,spider):
        self.pg.closeLink()

class YipImgPopeline(ImagesPipeline):
    """docstring for YipImgPopeline"""

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']

    def get_media_requests(self, item, info):
        yield Request(item['poster'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok,x in results if ok]
        if not image_paths:
            raise DropItem('Item contains no images')
        item['image_paths'] = image_paths
        return item