import re
from multiprocessing import freeze_support
import urllib
from urllib import parse
from urllib.request import Request

import scrapy
import requests
import json

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils import common


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']
    custom_settings = {
        "COOKIES_ENABLE": True
    }

    # 模拟登陆
    def start_requests(self):

        import undetected_chromedriver as uc

        browser = uc.Chrome()
        # cnBlog的登陆link
        browser.get("https://account.cnblogs.com/signin")
        input("input enter to continue")
        cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            # 将 cookie 直接给scrapy，后续的请求会沿用之前请求的cookie嘛？不会，scrapy会关了
            headers = {
                'User-Agent': 'Mozilla/4.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(url, cookies=cookie_dict, headers=headers, dont_filter=True)

    # parse的功能，下载列表页面中的url并进行解析 + 获取下一页的url并交给scrapy进行下载
    # 所以parse是用来写解析策略的

    def parse(self, response):
        """
        1. 获取新闻列表内的新闻url，交给scrapy下载并调用解析方法
        2. 获取下一页的url并交给scrapy进行下载；下载完成后交给parse继续跟进
        """

        post_nodes = response.css('#news_list .news_block')[:1]
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            post_url = post_node.css('h2 a::attr(href)').extract_first("")

            yield scrapy.Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                                 callback=self.parse_detail)
            break

        # # 提取下一页并交给scrapy下载
        # # 先拿切换页面的div中最后的那个值，判断是不是next，会出现到最后页next消失的情况，需要做特判
        # next_url = response.css('div.pager a:last-child::text').extract_first("")
        # # 或直接使用下面这行的xpath的方法，比css选择器更简单
        # # next_url = response.xpath("//a[contains(text(), 'Next >')/@href]")
        # if next_url == "Next >":
        #     next_url = response.css('div.pager a:last-child::attr(href)').extract_first("")
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):

        # 之后值的内容无法从html端获取，它们是通过js代码获取的，或是通过GET从服务器端拿的
        # 由于拿过来的值是JSON的格式，可以用requests包中的代码来解码JSON，拿需要的值（前提是找到了对应的GET link）
        # 获取url最后面的id，也就是每个详细网页的ID
        # 使用正则表达式
        match_re = re.match(".*?(\d+)", response.url)
        # 完善逻辑缜密性，必须是有匹配到最后面的id，才去爬html中的内容
        if match_re:
            # 使用自定义的item
            article_item = JobBoleArticleItem()

            post_id = match_re.group(1)

            title = response.css("#news_title a::text").extract_first("")

            created_date = response.css("#news_info span.time::text").extract_first("")
            match_re = re.match(".*?(\d+.*)", created_date)
            if (match_re):
                created_date = match_re.group(1)

            content = response.css("#news_content").extract()[0]

            tag_list = response.css(".news_tag a::text").extract()

            tags = ",".join(tag_list)

            article_item["title"] = title
            article_item["created_date"] = created_date
            article_item["content"] = content
            article_item["tags"] = tags
            article_item["url"] = response.url
            # front_image_url需要从parse方法中的request中获取，直接可以用response.meta进行获取
            if response.meta.get("front_image_url", ""):
                article_item["front_image_url"] = [response.meta.get("front_image_url", "")]  # 这么写get会避免空值的exception
            else:
                article_item["front_image_url"] = []
            # 天坑：将url用list包装，不然scrapy会将其使用for循环来做，拿到的值为http中的h
            # html = requests.get(parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            """
            {
            "ContentID": 726533,
            "CommentCount": 0,
            "TotalView": 240,
            "DiggCount": 5,
            "BuryCount": 0
            }
            """
            # 使用的requests是同步的，对于该框架来说不好；解决方案是直接将获取到的值都给他yield出去
            # 通过新回调来做一个异步的操作以此抵消自己做的同步操作吧？
            url = parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id))
            yield scrapy.Request(
                url=url,
                meta={"article_item":article_item},
                callback=self.parse_nums)

        pass

    @staticmethod
    def parse_nums(response):
        # 两层回调
        j_data = json.loads(response.text)

        article_item = response.meta.get("article_item", "")

        praise_nums = j_data["DiggCount"]
        view_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

        article_item["praise_nums"] = praise_nums
        article_item["view_nums"] = view_nums
        article_item["comment_nums"] = comment_nums
        # 将url转换成md5进行存储，节约空间；这里的md5转法写在util的common中定义方法
        article_item["url_object_id"] = common.get_md5(article_item["url"])

        yield article_item

        pass
