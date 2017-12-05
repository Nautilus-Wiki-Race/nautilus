#!/usr/bin/env python3
"""
wiki race flask app
"""
import json
import requests
from lowercase import LOWERCASE

all_titles = set()
queries = dict()
all_titles_reversed = set()
queries_end = dict()
URL_API = "https://en.wikipedia.org/w/api.php"
URL_WIKI = "https://en.wikipedia.org/wiki/"
ERRORS = [
    "NOT FOUND: Please ensure that you provide a proper Wikipedia Pages",
    "TIMEOUT: Please let us know how to improve our algorithm"
]

def reset():
    """
    resets glabal variables
    """
    global all_titles
    global queries
    global all_titles_reversed
    global queries_end
    all_titles = set()
    queries = dict()
    all_titles_reversed = set()
    queries_end = dict()

def is_not_duplicate(title, direction):
    """
    cleans (i.e. removes) titles that should not be in new titles list
    """
    if direction == "start":
        if title in all_titles:
            return False
    else:
        if title in all_titles_reversed:
            return False
    add_link_to_all_titles(title, direction)
    return True

def add_link_to_all_titles(title, direction):
    """
    adds all new titles to global all_titles
    """
    if direction == "start":
        global all_titles
        all_titles.add(title)
    else:
        global all_titles_reversed
        all_titles_reversed.add(title)


def clean_wiki_page_title(page):
    """
    cleans wikipediat page for synchronicity and validating GET request
    """
    pl = page.split(' ')
    l = len(pl)
    return '_'.join([
        pl[i].capitalize() if (
            i == 0 or i == l - 1 or pl[i].lower() not in LOWERCASE
        ) else pl[i].lower()
        for i in range(l)
    ])


def make_return_object(*args):
    """
    makes a return object based on the input arguments
    """
    results_obj = []
    for wikilink in args:
        results_obj.append('{}{}'.format(URL_WIKI, wikilink))
    reset()
    return results_obj

class WikiRace():
    """
    class to handle wikipedia website and all related links
    """

    def __init__(self, page, direction):
        """
        instantiates a wikipedia node based on the name of the page
        """
        self.page = page
        if direction == "start":
            self.child_links = {}
        else:
            self.parent_links = {}

    def do_handle_titles(self, links, direction):
        """
        handles the titles by adding to self attributes
        """
        if links is None:
            return
        titles = set()
        for link in links:
            this_title = link.get('title').replace(' ', '_')
            if is_not_duplicate(this_title, direction):
                titles.add(this_title)
        if direction == "start":
            for name in titles:
                self.child_links[name] = WikiRace(name, "start")
        else:
            for name in titles:
                self.parent_links[name] = WikiRace(name, "end")

    def get_page_links(self, direction):
        """
        makes GET request to wiki API from self.page
        and finds either titles on the page or
        titles linked to the page
        """
        payload = {
            'action': 'query',
            'format': 'json',
            'titles': self.page
        }
        if direction == "start":
            payload['prop'] = 'links'
            payload['pllimit'] = '500'
        else:
            payload['prop'] = 'linkshere'
            payload['lhlimit'] = '500'
        headers = {
            'User-agent': 'team nautilus'
        }
        r = requests.get(URL_API, headers=headers, params=payload)
        pages = r.json().get("query").get("pages")
        # name changes, so get the value
        for v in pages.values():
            link_val = v
        if direction == "start":
            links = link_val.get("links")
        else:
            links = link_val.get("linkshere")
        self.do_handle_titles(links, direction)

    def match_title_with_self(self, title, direction):
        """
        checks if a title is in any self objects
        """
        if direction == "start":
            if title in self.child_links:
                return True
        else:
            if title in self.parent_links:
                return True
        return None


def initialize_wiki_root(page, direction):
    """
    initializes the root nodes for wiki race
    """
    add_link_to_all_titles(page, direction)
    root = WikiRace(page, direction)
    root.get_page_links(direction)
    return root

def search_wiki(page_start, page_end):
    """
    the wiki search algorithm
    """
    reset()
    global queries
    global queries_end

    page_start = clean_wiki_page_title(page_start)
    page_end = clean_wiki_page_title(page_end)

    start_root = initialize_wiki_root(page_start, "start")
    end_root = initialize_wiki_root(page_end, "end")

    if len(start_root.child_links) == 0 or len(end_root.parent_links) == 0:
        reset()
        return(["error", ERRORS[0]])

    if start_root.match_title_with_self(page_end, "start"):
        return make_return_object(page_start, page_end)

    # Begin Search
    for title, wiki_node in start_root.child_links.items():
        wiki_node.get_page_links("start")
        if wiki_node.match_title_with_self(page_end, "start"):
            return make_return_object(
                page_start, title, page_end)
        else:
            intersect = set(wiki_node.child_links).intersection(set(end_root.parent_links))
            if len(intersect) > 1:
                return make_return_object(
                    page_start, title, intersect.pop(), page_end)
    for title, wiki_node in start_root.child_links.items():
        for title_2, wiki_node_2 in wiki_node.child_links.items():
            wiki_node_2.get_page_links("start")
            if wiki_node_2.match_title_with_self(page_end, "start"):
                return make_return_object(
                    page_start, title, title_2, page_end)
            else:
                intersect = set(wiki_node_2.child_links).intersection(set(end_root.parent_links))
                if len(intersect) > 1:
                    return make_return_object(
                        page_start, title, title_2, intersect.pop(), page_end)
    reset()
    return(["error", ERRORS[0]])



if __name__ == '__main__':
    """
    MAIN APP
    """
    print("Usage:")
    print("import wikirace")
