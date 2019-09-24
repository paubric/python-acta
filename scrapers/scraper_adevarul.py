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
        text = response.css('div.article-body').get()     

        parser = HTMLParser(recover=True)
        tree = et.parse(StringIO(text), parser)
        for element in tree.xpath('//script'):
            element.getparent().remove(element)

        text = et.tostring(tree, pretty_print=True, xml_declaration=True)
        text = lxml.html.tostring(lxml.html.fromstring(text, parser=parser), method='text', encoding='unicode')
        text = ' '.join(text.split())
        text = text.lower()
        text = text.replace('dacă apreciezi acest articol, te așteptăm să intri în comunitatea de cititori de pe pagina noastră de facebook, printr-un like mai jos:', '')

        time = response.css('time').xpath('@datetime').get()

        yield {
            'outlet': 'https://adevarul.ro',
            'url': url,
            'timestamp': time,
            'text': text
        }

    def parse(self, response):
        for article in response.css('div.mixed-news').css('article'):
            url = article.xpath('h3/a/@href').get()
            if url != None:
                yield scrapy.Request(self.start_urls[0] + url, callback=self.parse_page, cb_kwargs=dict(url=url))
        
        next_page = response.css('div.ctrl-left').xpath('a/@href').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)