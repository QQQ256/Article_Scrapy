# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import MapCompose, TakeFirst, Identity, Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 对所有的output_processor采取统一的TakeFirst()
# 自定义ItemLoader
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def date_convert(value):  # value 自动传递进来
    match_re = re.match(".*?(\d+.*)", value)
    if (match_re):
        return match_re.group(1)
    else:
        return "1900-00-00"

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    created_date = scrapy.Field(
        input_processor=MapCompose(date_convert)  # 做正则表达式的提取
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()  # output为takeFirst会将所有的值段变成str，然鹅img要下载，必须是保持之前的url状态，这里将output设置为Identity()保持不变
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    view_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")  # tags是list，用，隔开
    )
    content = scrapy.Field()
