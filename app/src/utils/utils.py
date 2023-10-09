import os
from urllib.parse import urlparse
from datetime import datetime
import pandas as pd
import time
import feedparser
import json
import logging
from flask import jsonify
from ..properties.properties import *


root_dir = os.getcwd()
log_dir = os.path.join(root_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'utils.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='Line %(lineno)d - %(asctime)s - %(levelname)s - %(message)s ')

GENERAL_QUEUE = QueueCollection.GENERAL_QUEUE.value
SPECIFIC_QUEUE = QueueCollection.SPECIFIC_QUEUE.value
SEMI_SPECIFIC_QUEUE = QueueCollection.SEMI_SPECIFIC_QUEUE.value


def check_file_type(file_name: str):
    try:
        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() == '.csv':
            return 'csv'
        elif file_extension.lower() == '.json':
            return 'json'
        else:
            logging.error("file format is not supported")
            return jsonify({"file format is not supported"})
    except Exception as e:
        logging.error("ERROR: while checking file type", str(e))
        return jsonify({"ERROR: while checking file type": str(e)})


def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        domain_url = parsed_url.netloc.split('.')
        if domain_url[0] == 'www':
            return domain_url[1]
        elif domain_url[1] == 'wikipedia':
            return domain_url[1]
        else:
            return domain_url[0]
    except Exception as e:
        logging.error("ERROR: while extracting domain", str(e))
        return jsonify({"ERROR: while extracting domain": str(e)})


def check_link_type(url: str):
    try:
        domain = extract_domain(url)
        if domain in SPECIFIC_DOMAINS:
            return 'specific'
        elif domain in SEMI_SPECIFIC_DOMAIN_NAMES:
            return 'semi_specific'
        else:
            return 'general'

    except Exception as e:
        logging.error("ERROR: while checking link type", str(e))
        return jsonify({"ERROR: while checking link type": str(e)})


def extract_urls_from_rss_feed(rss_feed_url: str, no_of_url_to_fetch: int = None, date_published: str = None):
    """
    :param rss_feed_url: input rss feed url
    :param no_of_url_to_fetch: total no of posts to fetch
    :param date_published: date of publishing after which url to fetch
    :return: list of url extracted
    """
    try:
        date_limit = None
        if isinstance(date_published, str):
            date_limit = datetime.strptime(date_published, "%d/%m/%Y")

        feed = feedparser.parse(rss_feed_url)
        urls = []

        for entry in feed.entries[:no_of_url_to_fetch]:
            entry_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            if date_limit:
                if entry_date >= date_limit:
                    urls.append(entry.link)
            else:
                urls.append(entry.link)

        return urls
    except Exception as e:
        logging.error("ERROR: while extracting url from rss", str(e))
        return jsonify({"ERROR: while extracting url from rss": str(e)})


def read_csv(file_name: str):
    """
    the function will read csv file and extract all the links from the file
    :param file_name: csv file
    :return: list of urls
    """
    try:
        if not isinstance(file_name, str):
            file_name = str(file_name)

        df = pd.read_csv(file_name)
        all_links = []

        for index, row in df.iterrows():
            if row['type'] == 'rss':
                no_posts = None
                date_published = None

                try:
                    no_posts = row['no_posts']
                    date_published = row['date_published']
                    if not isinstance(no_posts, int):
                        no_posts = int(no_posts)
                    if not isinstance(date_published, str):
                        date_published = str(date_published)
                except:
                    pass

                post_urls = extract_urls_from_rss_feed(row['url'], no_posts, date_published)
                all_links.extend(post_urls)
            else:
                all_links.append(row['url'])

        return all_links
    except Exception as e:
        logging.error("ERROR: while reading csv_file ", str(e))
        return jsonify({"ERROR: while reading csv_file ": str(e)})


def read_json(file_name: str):
    try:
        if not isinstance(file_name, str):
            file_name = str(file_name)
        with open(file_name, 'r') as file:
            data = json.load(file)
        all_links = []

        for item in data:
            if item['type'] == 'rss':
                no_posts = None
                date_published = None
                try:
                    no_posts = item['params']['no_posts']
                    date_published = item['params']['date_published']
                    if not isinstance(no_posts, int):
                        no_posts = int(no_posts)
                    if not isinstance(date_published, str):
                        date_published = str(date_published)
                except:
                    pass

                post_urls = extract_urls_from_rss_feed(item['url'], no_posts, date_published)
                all_links.extend(post_urls)
            else:
                all_links.append(item['url'])

        return all_links

    except Exception as e:
        logging.error("error while reading json", str(e))
        return jsonify({"ERROR: while reading json file": str(e)})


def queue_dump(rmq, link_list: list):
    try:
        for link in link_list:
            link_type = check_link_type(link)
            if link_type == 'specific':
                rmq.send_one_to_queue(SPECIFIC_QUEUE, link)
            elif link_type == 'semi_specific':
                rmq.send_one_to_queue(SEMI_SPECIFIC_QUEUE, link)
            else:
                rmq.send_one_to_queue(GENERAL_QUEUE, link)

    except Exception as e:
        logging.error("ERROR: while dumping url to queue", str(e))
        return jsonify({"ERROR: while dumping url to queue": str(e)})
