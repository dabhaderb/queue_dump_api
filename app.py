from flask import Flask, request, jsonify
import feedparser
from queue import Queue
from datetime import datetime

app = Flask(__name__)

url_que = Queue()


# API to extract url from RSS feed
@app.route('/rss_feed', methods=['POST', 'GET'])
def extract_url_from_rss():
    try:
        rss_feed_url = request.json['rss_feed']
        no_of_post = request.json.get('no_of_post', None)
        update_date_input = request.json.get('updated_date', None)
        if no_of_post is not None:
            total_post = no_of_post
        else:
            total_post = None
        if update_date_input is not None:
            update_date = datetime.strptime(update_date_input, "%Y-%m-%d")
        else:
            update_date = None

        feed = feedparser.parse(rss_feed_url)

        urls = []

        for entry in feed.entries[:total_post]:
            entry_date = datetime.fromtimestamp(entry.updated_parsed)
            if update_date is None or entry_date >= update_date:
                urls.append(entry.link)
                print(entry.link)

        return jsonify({"no of urls pushed to queue", len(urls)})

    except Exception as e:
        return jsonify({"error", str(e)}), 400


# API to que url from user provided url list
@app.route("/url_list", methods = ['POST'])
def que_url_from_list():
    try:
        # url_list = request.json['url_list']
        url_list = request.json.get('url_list')

        for url in url_list:
            print(url)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
