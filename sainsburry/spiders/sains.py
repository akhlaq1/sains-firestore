import re
import scrapy
from scrapy.exceptions import CloseSpider

from ..middlewares import client
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin

import logging
from scrapy.utils.log import configure_logging 


from urllib.parse import parse_qs

# noinspection SpellCheckingInspection
class SimpleItem:
    def __init__(self, response):
        
        self.sku = response.xpath(
            './/input[@name="SKU_ID"]/@value'
        ).get()
        # self.availability = bool(self.price)
        self.href = response.xpath('.//*[@class="productInfo"]//a/@href').get()
        
        if 'cat.hlserve.com' in self.href:
            new_url = parse_qs(urlparse(self.href).query)['dest'][0]
            if "productId" in new_url:
                prod_id = parse_qs(urlparse(new_url).query)['productId'][0]
                self.api_url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?cat_entry_id=%s&filter[available]=true&include=ASSOCIATIONS&include=DIETARY_PROFILE&minimised=false" % prod_id 

            else:    
                self.api_url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter" \
                        "[product_seo_url]=gb%2Fgroceries%2F" + new_url.rsplit('/', 1)[-1] + \
                    "&include[ASSOCIATIONS]=true&include[DIETARY_PROFILE]=true"
            self.href = new_url
        #    print("%s has cat url processing" % str(self.sku))
        # else:
        #     self.href = urljoin("https://www.sainsburys.co.uk/",self.href)
        
        elif "productId" in self.href:
            print("Inside ProductID href: ",self.href)
            prod_id = parse_qs(urlparse(self.href).query)['productId'][0]
            self.api_url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?cat_entry_id=%s&filter[available]=true&include=ASSOCIATIONS&include=DIETARY_PROFILE&minimised=false" % prod_id 
        
        else:
            print("Inside else href: ",self.href)    
            self.api_url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter" \
                       "[product_seo_url]=gb%2Fgroceries%2F" + self.href.rsplit('/', 1)[-1] + \
                       "&include[ASSOCIATIONS]=true&include[DIETARY_PROFILE]=true"
    

        try:
            price = response.xpath(
                './/*[@class="pricePerUnit"]/text()'
            ).get()
            price = price.replace(" ", "").replace("\r\n", "")
        except Exception as e:
            # self.logger.info(f"NEXT PAGE NOT FOUND OF URL => {self.href} exception =>{e}")
            logging.warning(f"Price Not foung of following item URL => {self.href} exception =>{e}")
            price = 'N/A'
        self.price = price
        # self.price = float(re.findall(r'\d*\.?\d+', price)[0])
        
        
    # def parse_cat_url(self,href):
    #     user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    #     headers = {'User-Agent': user_agent}
    #     new_url = urljoin("https://cat.hlserve.com",href)
    #     r = requests.get(client.scrapyGet(new_url),headers=headers)
    #     url =  urlparse(r.url)
    #     return url.path

# noinspection SpellCheckingInspection,PyMethodMayBeStatic
class Sainsburry(scrapy.Spider):
    
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log-complete-categories.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    
    allowed_domains = ["sainsburys.co.uk", "api.scraperapi.com"]
    name = 'sainsSpider'
    
    
    categories = ['dietary-and-lifestyle','fruit-veg','meat-fish','dairy-eggs-and-chilled','bakery','frozen-','food-cupboard','drinks','household','beauty-and-cosmetics','health-beauty','baby-toddler-products','pet','home']
    
    # categories = ['dietary-and-lifestyle','fruit-veg','meat-fish','bakery',
    #             'frozen-','drinks',
    #             'baby-toddler-products','pet']
    # categories = ['health-beauty']
    # categories =['household']
    start_urls = ['https://www.sainsburys.co.uk/shop/gb/groceries/%s/seeall?fromMegaNav=1' % i for i in categories]
    error_count = 0
    page_number = 1
    product_num = 0
    def start_requests(self):
        for url in self.start_urls:
            # for i,item in enumerate(cat):
                #self.page_number = 1
                # url = 'https://www.sainsburys.co.uk/shop/gb/groceries/%s/seeall?fromMegaNav=1' % item

            yield scrapy.Request(client.scrapyGet(url), callback=self.parse)
                
    def parse(self, response):
        
        # get all products

        self.page_number = self.page_number+1
        self.logger.info(f"CURRENT PAGE NUMBER {str(self.page_number)}" )
        
        
        products = response.xpath("//li[contains(@class, 'gridItem')]")
        self.logger.info("this response of url has %s items, url=> %s" % (len(products), response.url))

        self.product_num = self.product_num + len(products)
        self.logger.info("Total products Scraped %s " % str(self.product_num))
        if products:
            self.error_count = 0

        # if no product was found we will try to reprocess the last request
        if not products and 'Please enable cookies or JavaScript' in response.text:
            with open('crawled_page.html', "w") as f:
                f.write(response.text)

            if self.error_count > 20:
                raise CloseSpider(f'could not reprocess url {response.request.url}')

            self.logger.info("trying to reprocess url")
            self.error_count += 1
            request = response.request.replace(dont_filter=True)
            yield request

        # yield items
        
        for item in products:
            # noinspection PyBroadException
            try:
                href1 = item.xpath('.//*[@class="productInfo"]//a/@href').get()
                self.logger.info(f"HREF of the product {href1}")
                minor_prod = SimpleItem(item).__dict__
                self.logger.info(minor_prod)
                yield minor_prod
            except Exception as e:
                self.logger.exception(f'Exception when yielding item {item.text} exception=>{e}')

        # We dont want to search new page if we are trying to reprocess the previous one
        try:
            # if not self.error_count:
            next_page_url = response.xpath('//li[@class="next"]/a/@href').get()
            self.logger.debug("current page url=> %s" % response.url)
            self.logger.debug("next page url=> %s" % next_page_url)
            if next_page_url:
                yield scrapy.Request(client.scrapyGet(next_page_url), callback=self.parse)
        except Exception as e:
            self.logger.info(f"NEXT PAGE NOT FOUND OF URL => {response.url} exception =>{e}")
