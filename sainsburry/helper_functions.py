import requests
import json
from datetime import datetime
from .settings import db, main_node

def get(sku):
    result = db.collection(main_node).document(sku).get().to_dict()
    # result = db.child('tesco').child(sku).get().val()
    if result:
        return result
    else:
        None
        
# def get_start_urls():
#     url = "https://www.sainsburys.co.uk/shop/AjaxGetImmutableZDASView?requesttype=ajax&storeId=10151&langId=44&catalogId=10241&slot="
#     res = requests.get(url,stream=True)
#     json_res = json.loads(res.text)
        
#     seeAllUrls = []
#     for i in json_res['navList']:
#         if i['parentId'] == 0 :
#             if "working-to-feed" not in i['seeAllUrl']:
#                 if "trending" not in i['seeAllUrl']:
#                     seeAllUrls.append(i['seeAllUrl'])
#     return seeAllUrls
    
def simpleitem(product):
    href = product.xpath('div/div[1]/div/h3/a/@href').extract()
    price = product.xpath('div/div[3]/div/div/div/div[1]/p[1]/text()').get()
    availability = bool(price)
    price = float(price) if availability else float(0)
    return href,price,availability


def product_data_scrapper(response,sku,price):
    
    col_dict = {'name_tesco': {0: 'Fresh Food',
  1: 'Fresh Food',
  2: 'Fresh Food',
  3: 'Fresh Food',
  4: 'Bakery',
  5: 'Frozen Food',
  6: 'Food Cupboard',
  7: 'Food Cupboard',
  8: 'Drinks',
  9: 'Drinks',
  10: 'Baby',
  11: 'Health & Beauty',
  12: 'Health & Beauty',
  13: 'Health & Beauty',
  14: 'Pets',
  15: 'Household',
  16: 'Home & Entertainment'},
 'name_mor': {0: 'Fruit & vegetables',
  1: 'Meat & Fish',
  2: 'Dairy, eggs & chilled',
  3: 'Dietary & Lifestyle - Vegan, Vegetarian, Organic',
  4: 'Bakery',
  5: 'Frozen',
  6: 'Food cupboard',
  7: 'Dietary & lifestyle',
  8: 'Drinks',
  9: 'Dietary & Lifestyle - Low & no alcohol',
  10: 'Baby & toddler',
  11: 'Toiletries & Health',
  12: 'Dietary & Lifestyle - Vitamins & supplements, Sports Nutrition',
  13: 'Beauty & cosmetics',
  14: 'Pet',
  15: 'Household',
  16: 'Homeware & outdoor'}}
    # product_category = 'N/A'
    # try:
    #     product_category = response.xpath("//ol[contains(@class,'ln-c-breadcrumbs') or contains(@class,'ln-o-inline-list')]/li//text()").extract() 
    # except :
    #     pass
    # our_category = "N/A"
    # try:
    #     for i,v in col_dict['name_mor'].items():
    #         if v.lower() ==  product_category[0].lower():
                
    #             our_category = col_dict['name_tesco'][i]
    # except :
    #     pass

    
    
    # product_detail =  response.xpath('//div[@id="mainPart"]//*[self::h3 or self::p]/text()').extract() or None
    # try:
    #     product_price = response.xpath('//div[@data-test-id="pd-retail-price"]/text()').extract() or None
    #     if product_price:
    #         product_price = product_price
    #         product_availability = "Available"
    #     else:
    #         product_price = "N/A"
    #         product_availability = "N/A"
    # except :
    #         product_price = "N/A"
    #         product_availability = "N/A"       
    
    # images_url = response.xpath('//img[@class="pd__image"]/@srcset').extract() or "N/A"
    # product_package_size = 'N/A'
    # try:
    #     product_package_size = response.xpath('//h1[@class="pd__header"]/text()').get().split(' ')[-1]
    # except :
    #     pass
    # prod_dict = {
    #         'product_description': response.xpath('//div[@id="mainPart" or @class="productText"]//*[self::h3 or self::p]/text()').get() or None,
    #         'product_name': response.xpath('//h1[@class="pd__header"]/text()').get() or "N/A",
    #         'product_price': product_price,
    #         'product_package_size': product_package_size,
    #         'images_url': images_url,
    #         'product_nutritiontable_header': response.xpath('//table[@class="nutritionTable"]/thead/tr/th/text()').extract() or "N/A",
    #         'table_rows': response.xpath('//table[@class="nutritionTable"]/tbody/tr/*[self::th or self::td]/text()').extract() or "NA",
    #         'product_ingredients': str(response.xpath('//ul[@class="productIngredients"]/li/text()').extract()) or "N/A",
    #         'sku': sku ,
    #         'product_category':product_category  or "N/A",
    #         'product_availability': product_availability,
    #         # 'date_OnOffer': response.xpath('//*[@id="main"]/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[1]/div[4]/ul/li/div/a/div/span/text()').extract() or "NA",
    #         "created":str(datetime.now()),
    #         "modified":str(datetime.now()),
    #         "analyzed":1
    # }
    
    product_category = 'N/A'
    try:
        product_category = response.get('breadcrumbs', "N/A")[0]['label']
    except :
        pass
    our_category = "N/A"
    try:
        for i,v in col_dict['name_mor'].items():
            if v.lower() ==  product_category.lower():
                
                our_category = col_dict['name_tesco'][i]
    except :
        pass

    
 
    product_detail = response.get('description')
    product_detail_cont = response.get('important_information')

    if product_detail and product_detail_cont:
        product_description = product_detail + product_detail_cont
    elif product_detail or product_detail_cont:
        product_description = product_detail or product_detail_cont
    else:
        product_description = "N/A"

    ingredients = "Contains Alcohol" if response.get('is_alcoholic') else "Nonalcoholic Ingredients"
    img_all = 'N/A'
    try:
        img_all = response.get('assets', {}).get('images', [{}])[0].get('sizes')
    except :
        img_all = 'N/A'
        
    package_size = "N/A"
    package_size_string = response.get('name', "N/A").split(' ')[-1]
    try:
        for i in list(package_size_string): 
            if i.isnumeric(): 
                package_size = package_size_string
                break
    except :
        pass

    prod_dict = {
            'our_category': our_category,
            'product_description': product_description or None,
            'product_name': response.get('name', "N/A"),
            'product_price': price,
            'product_package_size': package_size or "N/A",
            'images_url': response.get('image'),
            # 'image_all_sizes':img_all response.get('assets', {}).get('images', [{}])[0].get('sizes'),
            'image_all_sizes':img_all,
            'product_nutritiontable_header':  "N/A",
            'table_rows':  "NA",
            'product_ingredients': ingredients or "N/A",
            'sku': sku,
            'product_category': product_category,
            'product_availability': response.get('is_available'),
            # 'date_OnOffer': response.xpath('//*[@id="main"]/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[1]/div[4]/ul/li/div/a/div/span/text()').extract() or "NA",
            "created": str(datetime.now()),
            "modified": str(datetime.now()),
            "analyzed": 1
     }
    return prod_dict


def mark_analyzed(sku_item):
    
    analyzed_dict = {
        "analyzed":1
    }
    db.collection(main_node).document(sku_item).update(analyzed_dict)
    
    

def count_collection(coll_ref, count, cursor=None):
    
    if cursor is not None:
        docs = [snapshot.reference for snapshot
                in coll_ref.limit(1000).start_after(cursor).stream()]
    else:
        docs = [snapshot.reference for snapshot
                in coll_ref.limit(1000).stream()]
    
    for i in docs:
        doc_ref = db.collection(main_node).document(docs[0].id)
        doc_ref.update(
                    {
            "analyzed":0,
            "update":False})

    count = count + len(docs)

    if len(docs) == 1000:
        return count_collection(coll_ref, count, docs[999].get())
    else:
        print(f"Products at starting of spider {str(count)}")