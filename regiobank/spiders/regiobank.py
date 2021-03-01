import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from regiobank.items import Article


class RegiobankSpider(scrapy.Spider):
    name = 'regiobank'
    start_urls = ['https://www.regiobank.ch/regiobank-solothurn/news-archiv']

    def parse(self, response):
        links = response.xpath('//a[@class="link_kasten"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//i/text()').get()
        if date:
            date = date.strip().split()[-1]
        else:
            return

        content = response.xpath('//div[@class="news-list-view"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
