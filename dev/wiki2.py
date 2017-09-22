#!/usr/bin/python3
"""
vagrant@ubuntu:~$ python3 wiki.py Antarctica "Edward Bransfield"
the link os on the same page
https://en.wikipedia.org/wiki/Edward_Bransfield
"""
import requests
import sys


def get_titles(wiki_url, page1):
    url = "https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=500&format=json&titles=" + page1
    r = requests.get(url, headers={'User-agent': 'holberton 0.1'})
    pages = r.json().get("query").get("pages")
    for k, v in pages.items():
        k = k
        v = v
    links = v.get("links")
    if links is None:
        return ([])
    titles = []
    for link in links:
        titles.append(link.get('title'))
    return (titles)

if __name__ == "__main__":
    page1 = sys.argv[1]
    page1 = page1.replace(' ', '_')
    page2 = sys.argv[2]
    wiki_url = "https://en.wikipedia.org/wiki/"
    titles1 = []
    titles1 = get_titles(wiki_url, page1)
    if page2 in titles1:
        page_2 = page2.replace(' ', '_')
        ret_url = wiki_url + page_2
        print(ret_url)
    else:
        titles2 = []
        for title in titles1:
            titles2 += get_titles(wiki_url, title)
            if page2 in titles2:
                page_2 = page2.replace(' ', '_')
                ret_url = wiki_url + page_2
                print("stage 2: ", ret_url)
                break
