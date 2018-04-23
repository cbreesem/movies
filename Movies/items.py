# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MoviesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class YupItem(scrapy.Item):
    """docstring for YupItem"""
    site = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    imdb = scrapy.Field()
    poster = scrapy.Field()
    res = scrapy.Field()
    pass

class DoubanItem(scrapy.Item):
    """docstring for DoubanItem"""
    title = scrapy.Field()
    year = scrapy.Field()
    href = scrapy.Field()
