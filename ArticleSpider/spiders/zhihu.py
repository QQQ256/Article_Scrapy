import scrapy
from ArticleSpider.utils import zhihu_login_sel
from ArticleSpider.settings import USER, PASSWORD
from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']
    custom_settings = {
        "COOKIES_ENABLE": True
    }

    def start_requests(self):

        import undetected_chromedriver as uc
        browser = uc.Chrome()
        # cnBlog's login link
        browser.get("https://account.cnblogs.com/signin")
        input("input enter to continue")
        cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            # Give the cookie directly to scrapy,
            # will subsequent requests use the previously requested cookie? No, scrapy will be closed
            headers = {
                'User-Agent': 'Mozilla/4.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(url, cookies=cookie_dict, headers=headers, dont_filter=True)

    def parse(self, response):
        """
        1. get all urls from one page and keep tracking on such urls
        2. if the format of the url is like: /question/xx, then go to the parse func after it's downloaded
        :param response:
        :return:
        """
        all_urls = response.css("a:attr(href)").extract

        pass
