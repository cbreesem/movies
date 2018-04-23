# -*- coding: utf-8 -*-
import os,sys
import hashlib
import re
from bs4 import BeautifulSoup

import scrapy
from scrapy import Request

from Movies.PostgreSQL import PostgreSQL
from Movies.items import YupItem
from Movies.settings import db,path

class YupTorrents(scrapy.Spider):
    name = 'YupTorrents'
    domain = 'https://yuptorrents.com/'
    urls = []
    # custom_settings = {
    #     'ITEM_PIPELINES':{'pipelineClass1': 300,'pipelineClass2': 400},
    # }

    def start_requests(self):
        pg = PostgreSQL(db)
        self.urls = pg.select('res_site',['url'])
        self.urls = [i[0] for i in self.urls]

        yield Request(url=self.domain, callback=self.parse)

    def parse(self,response):
        index = BeautifulSoup(response.body, 'html.parser')
        classes = index.find('ul',{'class':'nav navbar-nav navbar-left'}).findAll('li')
        classes = [i.find('a').getText() for i in classes]
        for i in classes:
            yield Request(url='%sbrowse?genre=%s' % (self.domain,i), callback=self.getPage)
            # break

    def getPage(self,response):
        url = response.url
        html = BeautifulSoup(response.body,'html.parser')
        count = html.find('li',{'class':'page_info'})
        count = int(count.getText().split()[-1])
        for i in range(1,count+1):
            yield Request(url='%s&page=%d' % (url,i), callback=self.getLinks)
            # break

    def getLinks(self,response):
        html = BeautifulSoup(response.body,'html.parser')
        links = html.findAll('div',{'class':'col-md-2 item top-padding'})
        for i in links:
            uri = i.find('a').get('href')
            if uri not in self.urls: yield Request(url=uri, callback=self.getInfo)
            # break

    def getInfo(self,response):
        fields = YupItem()

        html = BeautifulSoup(response.body,'html.parser')
        name = html.find('h1',{'class':'text-center col-sm-5'}).getText().split()
        poster = html.find('img',{'id':'cover'}).get('src')
        divs = html.findAll('div',{'class':'row'})
        for i in divs:
            if i.find('label',{'class':'col-xs-3 no-margin no-padding'}) is not None:
                if i.find('a') is not None: imdb = i.find('a').get('href')

        fields['site'] = self.name
        fields['url'] = response.url
        fields['title'] = ' '.join(name[:-2])
        fields['year'] = re.sub('\D', '', name[-2])
        fields['poster'] = self.domain+poster
        fields['imdb'] = imdb
        fields['res'] = []

        downTable = html.find('table',{'class':'table table-striped table-hover'})
        mainbody = downTable.findAll('td')
        for i in range(0,len(mainbody),6):

            links = dict()
            label = []
            fileName = mainbody[i].getText().strip()
            if re.search(r'4k|4K', fileName): label.append('4K')
            if re.search(r'1080p|1080P', fileName): label.append('1080P')
            if re.search(r'720p|720P', fileName): label.append('720P')
            if re.search(r'480p|480P', fileName): label.append('480P')
            if re.search(r'aac|AAC', fileName): label.append('AAC')
            if re.search(r'avc|AVC', fileName): label.append('AVC')
            if re.search(r'dts|DTS', fileName): label.append('DTS')
            if re.search(r'3d|3D', fileName): label.append('3D')
            if re.search(r'ac3|AC3', fileName): label.append('AC3')
            if re.search(r'REMUX|Remux|remux', fileName): label.append('REMUX')
            if re.search(r'iso|ISO', fileName): label.append('原盘')
            if re.search(r'dvdrip|DVDRip', fileName): label.append('DVDRip')
            if re.search(r'cam|CAM', fileName): label.append('CAM')
            if re.search(r'web-dl|WEB-DL', fileName):label.append('WEB-DL')
            if re.search(r'webdl|WEBDL', fileName):label.append('WEBDL')
            if re.search(r'webrip|WEBRip', fileName):label.append('WEBRip')
            if re.search(r'Screener', fileName):label.append('Screener')
            if re.search(r'brrip|BRRip', fileName):label.append('BRRip')
            if re.search(r'dvdscr|DVDScr', fileName):label.append('DVDScr')
            if re.search(r'hdrip|HDRip', fileName):label.append('HDRip')
            if re.search(r'ts|TS', fileName): label.append('TS')
            if re.search(r'hdts|HDTS', fileName): label.append('HDTS')
            if re.search(r'hdcam|HDCAM', fileName): label.append('HDCAM')
            if re.search(r'hd-ts|HD-TS', fileName): label.append('HD-TS')
            if re.search(r'bluray|BluRay', fileName): label.append('BluRay')
            if re.search(r'bdrip|BDRip', fileName): label.append('BDRip')

            links['resource'] = fileName
            links['size'] = ''.join(mainbody[i+1].getText().split())
            links['btlink'] = self.domain + mainbody[i+4].find('a').get('href')
            links['malink'] = mainbody[i+5].find('a').get('href')
            links['label'] = label

            md5 = hashlib.md5(links['btlink'].encode('utf8')).hexdigest()

            links['filename'] = '%s/%s/%s/%s.torrent' % (path,'Torrent',self.name,md5)

            fields['res'].append(links)

            yield Request(url=links['btlink'], callback=self.getTorrent)

        yield fields
        yield Request(url=fields['poster'], callback=self.getPoster)

    def getPoster(self, response):

        imgPath = '%s/%s' % (path,'Picture')
        if not os.path.exists(imgPath): os.mkdir(imgPath)
        imgPath = '%s/%s' % (imgPath,self.name)
        if not os.path.exists(imgPath): os.mkdir(imgPath)

        fileName = hashlib.md5(response.url.encode('utf8')).hexdigest()

        with open('%s/%s.jpg' % (imgPath, fileName), 'wb') as f:
            f.write(bytes(response.body))

    def getTorrent(self, response):

        torPath = '%s/%s' % (path,'Torrent')
        if not os.path.exists(torPath): os.mkdir(torPath)
        torPath = '%s/%s' % (torPath,self.name)
        if not os.path.exists(torPath): os.mkdir(torPath)

        fileName = hashlib.md5(response.url.encode('utf8')).hexdigest()

        with open('%s/%s.torrent' % (torPath, fileName), 'wb') as f:
            f.write(bytes(response.body))

        # print(self.urls,1111111111111111111111111)
