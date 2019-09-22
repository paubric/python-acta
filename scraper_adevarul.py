import scrapy
import lxml.html
import lxml.etree as et
from lxml.etree import HTMLParser
from io import StringIO 


class AdevarulSpider(scrapy.Spider):
    name = 'articles'
    start_urls = [
        'https://adevarul.ro/news/politica/',
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
        for article in response.css('div.mixed-news').css('article'):
            url = article.xpath('h3/a/@href').get()
            if url != None:
                yield {
                    'url': url
                }
        
        next_page = response.css('div.ctrl-left').xpath('a/@href').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)