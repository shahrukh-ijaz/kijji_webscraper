import scrapy
import re
from datetime import datetime

class FastSearchSpider(scrapy.Spider):
    name = "kijji"
    count = 0
    start_urls = ['https://www.kijiji.ca/b-apartments-condos/ontario/c37l9004']

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.kijiji.ca/",
            callback=self.parse            
        )

    def parse(self, response):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse_ads,            
        )

    def parse_ads(self, response):
        links = response.xpath("//div[@class='title']/a/@href").extract()
        for link in links:
            yield response.follow(
                url=link,
                callback=self.parse_product
            )

        next_btn = response.xpath("//a[@title='Next']/@href").extract_first()
        if next_btn:
             yield response.follow(
                url=next_btn,
                callback=self.parse_ads,
            )

    @staticmethod
    def remove_tags(text):
            TAG_RE = re.compile(r'<[^>]+>')
            return TAG_RE.sub(' ', text)
    
    def parse_product(self, response):
        title = response.xpath("//*[contains(@class, 'title-')]/text()").extract_first()
        
        description = response.xpath("//div[contains(@class,'descriptionContainer')]/div").get()
        description = self.remove_tags(description)
        
        url = response.url
        email = ""
        match = re.search(r'[\w\.-]+@[\w\.-]+', description)
        if match:
            email = match.group(0)
        
        yield {
            'email': email,
            'title': title,
            'description': description,
            'url': url,
            'scrape_time': str(datetime.now().strftime("%d-%B-%Y %H:%M:%S"))
        }
