# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name='sainsburry',
    version='3.0.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = sainsburry.settings']},
    include_package_data=True,
    zip_safe=False,
)
