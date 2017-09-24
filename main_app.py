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
all_titles = set()
queries = dict()


def reset():
    """
    resets
    """
    global all_titles
    global queries
    all_titles = set()
    queries = dict()


def get_titles(wiki_url, page_start):
    """
    makes get request to wiki API
    """
    payload = {
        'action': 'query',
        'prop': 'links',
        'pllimit': '500',
        'format': 'json',
        'titles': page_start
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


def clean_links(titles):
    """
    cleans titles that should not be in new titles list
    """
    global all_titles
    return (titles.difference(all_titles))


def search_wiki(page_start, page_end):
    """
    basic search for pages
    """
    global all_titles
    global queries
    all_titles.add(page_start)
    queries[page_start] = {}
    page_start = page_start.replace(' ', '_')
    wiki_url = "https://en.wikipedia.org/wiki/"
    check_one = get_titles(wiki_url, page_start)
    check_two = get_titles(wiki_url, page_end.replace(' ', '_'))
    if len(check_one) == 0 or len(check_two) == 0:
        reset()
        return([
            "error",
            "link not found"
        ])
    titles = check_one
    titles = clean_links(titles)
    ret_url = None
    if page_end in titles:
        page_end = page_end.replace(' ', '_')
        reset()
        return([
            '{}{}'.format(wiki_url, page_start),
            '{}{}'.format(wiki_url, page_end),
        ])
    else:
        all_titles = all_titles.union(titles)
        queries[page_start] = dict.fromkeys(titles)
    for title in queries[page_start]:
        temp_titles = get_titles(wiki_url, title)
        temp_titles = clean_links(temp_titles)
        if page_end in temp_titles:
            step2 = title.replace(' ', '_')
            page_end = page_end.replace(' ', '_')
            ret_url = 'found'
            break
        all_titles = all_titles.union(temp_titles)
        queries[page_start][title] = dict.fromkeys(temp_titles)
    if ret_url == 'found':
        reset()
        return([
            '{}{}'.format(wiki_url, page_start),
            '{}{}'.format(wiki_url, step2),
            '{}{}'.format(wiki_url, page_end)
        ])
    else:
        for title in queries[page_start]:
            for second_title in queries[page_start][title]:
                # print('checking path: {} -> {}'.format(title, second_title))
                temp_titles = get_titles(wiki_url, second_title)
                temp_titles = clean_links(temp_titles)
                if page_end in temp_titles:
                    step2 = title.replace(' ', '_')
                    step3 = second_title.replace(' ', '_')
                    page_end = page_end.replace(' ', '_')
                    ret_url = 'found'
                    break
                all_titles = all_titles.union(temp_titles)
                queries[page_start][title][second_title] = (
                    dict.fromkeys(temp_titles))
    if ret_url == 'found':
        reset()
        return([
            '{}{}'.format(wiki_url, page_start),
            '{}{}'.format(wiki_url, step2),
            '{}{}'.format(wiki_url, step3),
            '{}{}'.format(wiki_url, page_end)
        ])
    else:
        reset()
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
