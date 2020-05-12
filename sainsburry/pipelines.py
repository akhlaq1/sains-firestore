# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from . import helper_functions
from .settings import db, main_node
from .middlewares import client
from scrapy.selector import Selector



# noinspection SpellCheckingInspection,PyMethodMayBeStatic,PyUnusedLocal
class SainsburryPipeline(object):
    
    def open_spider(self, spider):
        
        try:        
            docs = db.collection(main_node).stream()
            for doc in docs:
                doc_ref = db.collection(main_node).document(doc.id)
                doc_ref.update(
                        {
                "analyzed":0,
                "update":False
            }
                )
        except :
            pass
        spider.logger.info('Spider opened: %s' % spider.name)

    def close_spider(self, spider):
        try:
            
            skus_delete = db.collection(main_node).where(u'analyzed', u'==', 0).stream()
            for item in skus_delete:
                db.collection(main_node).document(item.id).delete()
                
            # if skus_delete and len(skus_delete) <= 100:
            #     for item in skus_delete:
            #         db.collection(main_node).document(item.id).delete()
            # elif skus and len(skus) > 100:
            #     for x in skus[:100]:
            #         db.child(main_node).child(x).remove()A
        except:
            pass
        spider.logger.info('Spider closed: %s' % spider.name)
            
    def process_item(self, item, spider):
        db_item = helper_functions.get(item['sku'])
        if db_item:
            helper_functions.mark_analyzed(item['sku'])
            if db_item['product_price'] == item['price']:
                raise DropItem(f'sku %(sku)s has same price %(price)s in firebase' % item)
            else:
                spider.logger.debug(f'sku %(sku)s price %(price)s is diferent in firebase' % item)
                item['update'] = True
        else:
            spider.logger.debug(f'sku %(sku)s does not exists in firebase' % item)

        #if 'cat.hlserve.com/beacon' in item['href']:
            # raise DropItem('item %(sku)s ignored bad url' % item)
           
        try:
            response = client.get(url=item['api_url'])
            if not response.ok:
                raise DropItem(
                    f'sku %s API response not ok status code=> %s content=>\n%s' % (
                        item['sku'], response.status_code, response.text
                    )
                )
            # print(response.text)
            prod_data = helper_functions.product_data_scrapper(response.json()['products'][0],item['sku'],item['price'])
            
            if item.get('update'):
                    spider.logger.info(f"Updating the Item {item['sku']}")
                # db.child(main_node).child(item['sku']).update(item)
                    db.collection(main_node).document(item['sku']).update(prod_data)
            else:
                spider.logger.info(f"Creating the Item {item['sku']}")
                # db.child(main_node).child(item['sku']).set(item)
                db.collection(main_node).document(item['sku']).set(prod_data)
            
            
            
        except Exception as e:
            raise DropItem(f' Failed to process sku {item["sku"]} URL => {item["api_url"]} due to exception {e}')
        
        return item

