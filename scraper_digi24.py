import scrapy
import lxml.html
import lxml.etree as et
from lxml.etree import HTMLParser
from io import StringIO 


class Digi24Spider(scrapy.Spider):
    name = 'articles'
    start_urls = [
        'https://www.digi24.ro/stiri/actualitate/politica',
    ]

    def parse_page(self, response, url):
        text = response.xpath('/html/body/main/article/div/div[2]/div[2]/div/div').get()     
        
        parser = HTMLParser(recover=True)
        tree = et.parse(StringIO(text), parser)
        for element in tree.xpath('//script'):
            element.getparent().remove(element)

        text = et.tostring(tree, pretty_print=True, xml_declaration=True)
        text = lxml.html.tostring(lxml.html.fromstring(text, parser=parser), method='text', encoding='unicode')
        text = ' '.join(text.split())
        text = text.lower()

        time = response.css('time').xpath('@datetime').get()

        yield {
            'outlet': 'https://www.digi24.ro',
            'url': url,
            'timestamp': time,
            'text': text
        }

    def parse(self, response):
        for article in response.css('article'):
            url = article.xpath('div/h4/a/@href').get()
            if url != None:
                yield scrapy.Request(self.start_urls[0] + url, callback=self.parse_page, cb_kwargs=dict(url=url))
        
        next_page = response.css('a.pagination-link-next').xpath('@href').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)