import scrapy
from ArticleSpider.utils import zhihu_login_sel
from ArticleSpider.settings import USER, PASSWORD
class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']
    custom_settings = {
        "COOKIES_ENABLE": True
    }

    # logic: use automatic mobile verification code func to login,
    # then get the cookie from the website
    def start_requests(self):
        # automatic mobile verification code to log in
        l = zhihu_login_sel.Login(USER, PASSWORD, 6)
        cookie_dict = l.login()
        for url in self.start_urls:
            headers = {
                'User-Agent': 'Mozilla/4.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/104.0.0.0 Safari/537.36 '
            }
            yield scrapy.Request(url, cookies=cookie_dict, headers=headers, dont_filter=True)

    def parse(self, response, **kwargs):
        pass
