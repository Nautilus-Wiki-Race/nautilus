#!/usr/bin/env python3
"""
wiki race flask app
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import requests
import signal
import wikirace

app = Flask(__name__)
app.url_map.strict_slashes = False
host = '0.0.0.0'
port = 5000
registered_signal_status = False

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
            results_obj = wikirace.search_wiki(page_one, page_two)
        except Exception as e:
            results_obj = ["error", wikirace.ERRORS[1]]
        signal.alarm(0)
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
