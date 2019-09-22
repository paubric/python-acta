import scrapy
import lxml.html
import lxml.etree as et
from lxml.etree import HTMLParser
from io import StringIO 


class Digi24Spider(scrapy.Spider):
    name = 'articles'
    start_urls = [
        'https://www.libertatea.ro/politica',
    ]

    def parse_page(self, response, url):
        text = response.xpath('/html/body/section[3]/div/div[1]/div[2]/div').get()

        parser = HTMLParser(recover=True)
        tree = et.parse(StringIO(text), parser)
        for element in tree.xpath('//script'):
            element.getparent().remove(element)
        for element in tree.xpath('//ul'):
            element.getparent().remove(element)
        for element in tree.xpath('//a[contains(@class, "external-link") or contains(@class, "partner-item")]'):
            element.getparent().remove(element)
        for element in tree.xpath('//div[contains(@class, "latest-video") or contains(@class, "share-buttons")]'):
            element.getparent().remove(element)
        for element in tree.xpath('//p[contains(@class, "article-signature")]'):
            element.getparent().remove(element)

        text = et.tostring(tree, pretty_print=True, xml_declaration=True)
        text = lxml.html.tostring(lxml.html.fromstring(text, parser=parser), method='text', encoding='unicode')
        text = ' '.join(text.split())
        text = text.lower()

        time = response.css('time').xpath('@datetime').get()

        yield {
            'outlet': 'https://www.libertatea.ro',
            'url': url,
            'timestamp': time,
            'text': text
        }

    def parse(self, response):
        for article in response.css('section.category-container').css('a.news-item'):
            url = article.xpath('@href').get()
            if url != None:
                yield scrapy.Request(url, callback=self.parse_page, cb_kwargs=dict(url=url))
        
        next_page = response.css('ul.pagination').xpath('li[position() = last()]/a/@href').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)