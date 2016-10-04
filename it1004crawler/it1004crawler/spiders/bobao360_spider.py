#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 * Created by kevin on 9/25/16.
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 * Created by kevin on 9/23/16.
"""
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

from .utils import encode_utf8, get_md5_digest
from ..items import ArticleItem
from web.models import Author, Article


class FreeBufSpider(scrapy.Spider):
    name = "安全客"

    def start_requests(self):
        self.author = Author.query_objects.get(name=self.name)
        self.time_format = '%Y-%m-%d %H:%M:%S'

        urls = [
            'http://bobao.360.cn/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        news = response.css('#merge-list > li')
        for new in news:
            new_url = new.css('h3 a::attr(href)').extract_first()
            articles = Article.query_objects.filter(
                url_md5=get_md5_digest(new_url))
            if not articles:
                yield scrapy.Request(
                    new_url, callback=self.parse_article_link)

    def parse_article_link(self, response):
        article_item = ArticleItem()
        article = response.xpath('//*[@id="article_box"]')
        article_item['title'] = article.xpath(
            '//*[@id="article_box"]/h2/text()').extract()[0]
        # time format 2010-04-20 10:07:30
        # //*[@id="article_box"]/p[1]/span[1]
        # article_time = article.css('span[class=time] ::text').extract_first()
        # print(article_time)
        # article_item['issue_time'] = datetime.strptime(
        #     article_time, self.time_format)
        article_item['url'] = encode_utf8(response.url)
        article_item['url_md5'] = get_md5_digest(response.url)
        article_item['author'] = self.author

        content = response.xpath(
            '/html/body/div[2]/div[2]/div[2]/div[1]/div'
        ).extract()[0]
        soup = BeautifulSoup(content, 'html.parser')
        # delete some div
        soup.h2.extract()
        soup.find('div', class_='article-msg').extract()
        article_item['content'] = str(soup)
        yield article_item
