#!/usr/bin/env python3
"""
wiki race flask app
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import requests
import signal

app = Flask(__name__)
app.url_map.strict_slashes = False
host = '0.0.0.0'
port = 5000
all_titles = set()
queries = dict()
registered_signal_status = False
ERRORS = [
    "NOT FOUND: Please ensure that you provide a proper Wikipedia Pages",
    "TIMEOUT: Please let us know how to improve our algorithm"
]


def signal_handler(signum, frame):
    """
    signal handler for timeout function
    """
    raise Exception("function timeout, not enough resources")


def register_signal_handler():
    """
    this registers the signal handler function and timeout
    """
    global registered_signal_status
    registered_signal_status = True
    signal.signal(signal.SIGALRM, signal_handler)


def reset():
    """
    resets
    """
    global all_titles
    global queries
    all_titles = set()
    queries = dict()


def get_titles_on_page(page):
    """
    makes get request to wiki API from given page
    for titles on the input page
    """
    payload = {
        'action': 'query',
        'prop': 'links',
        'pllimit': '500',
        'format': 'json',
        'titles': page
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

def get_titles_linked_to_page(page):
    """
    makes get request to wiki API from given page
    for titles linking to the input page
    """
    payload = {
        'action': 'query',
        'prop': 'linkshere',
        'lhlimit': '500',
        'format': 'json',
        'titles': page
    }
    headers = {
        'User-agent': 'holberton 0.1'
    }
    url = "https://en.wikipedia.org/w/api.php"
    r = requests.get(url, headers=headers, params=payload)
    pages = r.json().get("query").get("pages")
    for v in pages.values():
        link_val = v
    links = link_val.get("linkshere")
    if links is None:
        return(set())
    titles = set()
    for link in links:
        titles.add(link.get('title'))
    return (titles)


def clean_links(titles):
    """
    cleans (i.e. removes) titles that should not be in new titles list
    """
    global all_titles
    return (titles.difference(all_titles))


def make_return_object(*args):
    """
    makes a return object based on the input arguments
    """
    results_obj = []
    wiki_url = "https://en.wikipedia.org/wiki/"
    for wikilink in args:
        results_obj.append('{}{}'.format(wiki_url, wikilink))
    return results_obj


def search_wiki(page_start, page_end):
    """
    the wiki search algorithm
    """
    global all_titles
    global queries
    all_titles.add(page_start)
    queries[page_start] = {}
    page_start = page_start.replace(' ', '_')
    check_one = get_titles_on_page(page_start)
    check_two = get_titles_on_page(page_end.replace(' ', '_'))
    if len(check_one) == 0 or len(check_two) == 0:
        return(["error", ERRORS[0]])
    titles = check_one
    titles = clean_links(titles)
    page_end_links = get_titles_linked_to_page(page_end.replace(' ', '_'))
    if page_end in titles:
        return make_return_object(page_start, page_end.replace(' ', '_'))
    all_titles = all_titles.union(titles)
    queries[page_start] = dict.fromkeys(titles)
    for title in queries[page_start]:
        temp_titles = get_titles_on_page(title)
        temp_titles = clean_links(temp_titles)
        if page_end in temp_titles:
            return make_return_object(
                page_start, title.replace(' ', '_'), page_end.replace(' ', '_'))
        else:
            for page_end_link in page_end_links:
                if page_end_link in temp_titles:
                    return make_return_object(
                        page_start,
                        title.replace(' ', '_'),
                        page_end_link.replace(' ', '_'),
                        page_end.replace(' ', '_'))
        all_titles = all_titles.union(temp_titles)
        queries[page_start][title] = dict.fromkeys(temp_titles)
    for title in queries[page_start]:
        for second_title in queries[page_start][title]:
            temp_titles = get_titles_on_page(second_title)
            temp_titles = clean_links(temp_titles)
            if page_end in temp_titles:
                return make_return_object(
                    page_start, title.replace(' ', '_'),
                    second_title.replace(' ', '_'), page_end.replace(' ', '_'))
            else:
                for page_end_link in page_end_links:
                    if page_end_link in temp_titles:
                        return make_return_object(
                            page_start, title.replace(' ', '_'),
                            second_title.replace(' ', '_'),
                            page_end_link.replace(' ', '_'),
                            page_end.replace(' ', '_'))
    return(["error", ERRORS[0]])


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    renders template for main index
    """
    if request.method == 'GET':
        if not registered_signal_status:
            register_signal_handler()
        return render_template('index.html')
    if request.method == 'POST':
        page_one = request.form['PAGE_ONE']
        page_two = request.form['PAGE_TWO']
        signal.alarm(30)
        try:
            reset()
            results_obj = search_wiki(page_one, page_two)
        except Exception as e:
            results_obj = ["error", ERRORS[1]]
        signal.alarm(0)
        reset()
        return render_template('results.html', results_obj=results_obj)


@app.route('/results/<results_obj>', methods=['GET', 'POST'])
def results(results_obj):
    """
    renders template for main index
    """
    return render_template('results.html', results_obj=json.loads(results_obj))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    """
    MAIN APP
    """
    app.run(host=host, port=port)
