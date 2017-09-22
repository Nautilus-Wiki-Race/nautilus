#!/usr/bin/python3
"""
vagrant@ubuntu:~$ python3 wiki.py Antarctica "Edward Bransfield"
the link os on the same page
https://en.wikipedia.org/wiki/Edward_Bransfield
"""
import requests
import sys


if __name__ == "__main__":
    page1 = sys.argv[1]
    page1 = page1.replace(' ', '_')
    page2 = sys.argv[2]
    wiki_url = "https://en.wikipedia.org/wiki/"
    url = "https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=500&format=json&titles=" + page1
    r = requests.get(url, headers={'User-agent': 'holberton 0.1'})
    pages = r.json().get("query").get("pages")
    for k, v in pages.items():
        k = k
        v = v
    links = v.get("links")
    titles = []
    for link in links:
        titles.append(link.get('title'))
    if page2 in titles:
        page_2 = page2.replace(' ', '_')
        ret_url = wiki_url + page_2
        print("the link os on the same page")
        print(ret_url)
