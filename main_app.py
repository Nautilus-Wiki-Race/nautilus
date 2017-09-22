#!/usr/bin/python3
"""
wiki race flask app
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import requests

app = Flask(__name__)
app.url_map.strict_slashes = False
host = '0.0.0.0'
port = 5000


def get_titles(wiki_url, page1):
    url = "https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=500&format=json&titles=" + page1
    r = requests.get(url, headers={'User-agent': 'holberton 0.1'})
    pages = r.json().get("query").get("pages")
    for k, v in pages.items():
        k = k
        v = v
    links = v.get("links")
    if links is None:
        return([])
    titles = []
    for link in links:
        titles.append(link.get('title'))
    return (titles)


def search_wiki(page1, page2):
    """
    basic search for pages
    """
    page1 = page1.replace(' ', '_')
    wiki_url = "https://en.wikipedia.org/wiki/"
    titles1 = []
    titles1 = get_titles(wiki_url, page1)
    ret_url = None
    if page2 in titles1:
        page2 = page2.replace(' ', '_')
        ret_url = wiki_url + page2
    else:
        titles2 = []
        for title in titles1:
            titles2 += get_titles(wiki_url, title)
            if page2 in titles2:
                page2 = page2.replace(' ', '_')
                ret_url = wiki_url + page2
                break
    if ret_url:
        return([
            page1,
            page2
        ])
    else:
        return([
            "error",
            "link not found"
        ])


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    renders template for main index
    """
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        page_one = request.form['PAGE_ONE']
        page_two = request.form['PAGE_TWO']
        results_obj = search_wiki(page_one, page_two)
        return redirect(url_for('results', results_obj=json.dumps(results_obj)))


@app.route('/results/<results_obj>', methods=['GET', 'POST'])
def results(results_obj):
    """
    renders template for main index
    """
    return render_template('results.html', results_obj=json.loads(results_obj))


"""
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
"""


if __name__ == '__main__':
    """
    MAIN APP
    """
    app.run(host=host, port=port)
