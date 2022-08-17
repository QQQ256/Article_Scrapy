import scrapy

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']
    custom_settings = {
        "COOKIES_ENABLE": True
    }

    def start_requests(self):
        pass
