#!/usr/bin/python3
"""
wiki race flask app
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
app.url_map.strict_slashes = False
host = '0.0.0.0'
port = 5000


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
        return redirect(url_for('results.html', results_object=results_object))


@app.route('/results/<results_object>', methods=['GET'])
def results(results_object):
    """
    renders template for main index
    """
    if request.method == 'GET':
        return render_template('results.html', results_object=results_object)


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
