import os
from urllib.parse import urlparse
from datetime import datetime
import pandas as pd
import time
import feedparser
from properties import semi_specific_urls_domains


def check_file_type(file_name: str):
    try:
        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() == '.csv':
            return 'csv'
        elif file_extension.lower() == '.json':
            return 'json'
        else:
            print("file format is not supported")
            return None
    except Exception as e:
        print('file format is not supported: ', str(e))
        return None


def extract_domain(url):
    parsed_url = urlparse(url)
    domain_url = parsed_url.netloc.split('.')
    if domain_url[0] == 'www': return domain_url[1]
    else: return domain_url[0]


def check_link_type(url: str):
    try:
        domain = extract_domain(url)
        if domain == 'wikipedia':
            return 'specific'
        elif domain in semi_specific_urls_domains:
            return 'semi_specific'
        else:
            return 'general'
    except Exception as e:
        print("url is wrong")


def extract_urls_from_rss_feed(rss_feed_url, no_of_url_to_fetch=None, date_published=None):
    """
    :param rss_feed_url: input rss feed url
    :param no_of_url_to_fetch: total no of posts to fetch
    :param date_published: date of publishing after which url to fetch
    :return: list of url extracted
    """

    if date_published is not None:
        date_limit = datetime.strptime(date_published, "%d/%m/%Y")
    else:
        date_limit = None
    feed = feedparser.parse(rss_feed_url)
    urls = []

    for entry in feed.entries[:no_of_url_to_fetch]:
        entry_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
        if entry_date >= date_limit:
            urls.append(entry.link)

    return urls


def read_csv(file_name):
    df = pd.read_csv(file_name)
    rss_feed_links =[]
    specific_urls = []
    semi_specific_urls = []
    general_urls = []
    for index, row in df.iterrows():
        link_type = row['type']
        link = row['url']
        if link_type == 'rss':
            rss_feed_links.append(link)
        elif link_type == 'specific':
            specific_urls.append(link)
        elif link_type == 'semi_specific':
            semi_specific_urls.append(link)
        else:
            general_urls.append(link)














