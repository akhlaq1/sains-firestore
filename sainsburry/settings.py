BOT_NAME = 'sainsburry'

SPIDER_MODULES = ['sainsburry.spiders']
NEWSPIDER_MODULE = 'sainsburry.spiders'




#main_node="sainsTest"
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./ooder.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

main_node = "sainsburry"  # firebase Main Node

# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'


CRAWLERA_API_KEY = '87e2fac2372640a59b7b2aad0e84c996'

# noinspection SpellCheckingInspection
SCRAPER_API_KEY = '104d3a4dbb0aba214db87cdbf45642c7'
URLLENGTH_LIMIT = 10000

# CRAWLERA_ENABLED = True
# CRAWLERA_APIKEY = '87e2fac2372640a59b7b2aad0e84c996'
# AUTOTHROTTLE_ENABLED = False
# DOWNLOAD_TIMEOUT = 600


ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
   
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    # 'scrapy_cookies.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    #  'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 350,
    # 'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 360,
    # 'scrapy_crawlera.CrawleraMiddleware': 610
}

DNS_TIMEOUT = 120

COOKIES_ENABLED = True
COOKIES_PERSISTENCE = True
COOKIES_PERSISTENCE_DIR = 'cookies'
# ------------------------------------------------------------------------------
# IN MEMORY STORAGE
# ------------------------------------------------------------------------------
COOKIES_STORAGE = 'scrapy_cookies.storage.in_memory.InMemoryStorage'
CONCURRENT_REQUESTS = 5

# PROXY_POOL_ENABLED = True

ITEM_PIPELINES = {
    'sainsburry.pipelines.SainsburryPipeline': 300,
}







