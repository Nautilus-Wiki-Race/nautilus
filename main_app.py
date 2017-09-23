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
    """
    makes get request to wiki API
    """
    payload = {
        'action': 'query',
        'prop': 'links',
        'pllimit': '500',
        'format': 'json',
        'titles': page1
    }
    headers = {
        'User-agent': 'holberton 0.1'
    }
    url = "https://en.wikipedia.org/w/api.php"
    r = requests.get(url, headers=headers, params=payload)
    pages = r.json().get("query").get("pages")
    for v in pages.values():
        link_val = v
    links = link_val.get("links")
    if links is None:
        return(set())
    titles = set()
    for link in links:
        titles.add(link.get('title'))
    return (titles)


def clean_links(all_titles, titles):
    """
    cleans titles that should not be in new titles list
    """
    return (titles.difference(all_titles))


def search_wiki(page1, page2):
    """
    basic search for pages
    """
    all_titles = {page1}
    queries = {
        page1: {}
    }
    page1 = page1.replace(' ', '_')
    wiki_url = "https://en.wikipedia.org/wiki/"
    titles = get_titles(wiki_url, page1)
    titles = clean_links(all_titles, titles)
    ret_url = None
    if page2 in titles:
        page2 = page2.replace(' ', '_')
        return([
            '{}{}'.format(wiki_url, page1),
            '{}{}'.format(wiki_url, page2),
        ])
    else:
        all_titles = all_titles.union(titles)
        queries[page1] = dict.fromkeys(titles)
    for title in queries[page1]:
        temp_titles = get_titles(wiki_url, title)
        temp_titles = clean_links(all_titles, temp_titles)
        if page2 in temp_titles:
            step2 = title
            page2 = page2.replace(' ', '_')
            ret_url = 'found'
            break
        all_titles = all_titles.union(temp_titles)
        queries[page1][title] = dict.fromkeys(temp_titles)
    if ret_url == 'found':
        return([
            '{}{}'.format(wiki_url, page1),
            '{}{}'.format(wiki_url, step2),
            '{}{}'.format(wiki_url, page2)
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
        return render_template('results.html', results_obj=results_obj)
    # return redirect(url_for('results', results_obj=json.dumps(results_obj)))


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
