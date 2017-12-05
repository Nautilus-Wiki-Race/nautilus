#!/usr/bin/env python3
"""
wiki race flask app
"""
import json
import requests

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


def remove_duplicate_links(titles, direction):
    """
    cleans (i.e. removes) titles that should not be in new titles list
    """
    if direction == "start":
        global all_titles
        return (titles.difference(all_titles))
    else:
        global all_titles_reversed
        return (titles.difference(all_titles_reversed))


def add_links_to_all_titles(titles, direction):
    """
    adds all new titles to global all_titles
    """
    if direction == "start":
        global all_titles
        all_titles = all_titles.union(titles)
    else:
        global all_titles_reversed
        all_titles_reversed = all_titles_reversed.union(titles)


def do_handle_titles(links, direction):
    """
    handles the titles by adding to self attributes
    """
    if links is None:
        return set()
    titles = set()
    for link in links:
        this_title = link.get('title').replace(' ', '_')
        #if is_not_duplicate(this_title, direction):
        titles.add(this_title)
    titles = remove_duplicate_links(titles, direction)
    add_links_to_all_titles(titles, direction)
    return titles

def get_page_links(page, direction):
    """
    makes GET request to wiki API from self.page
    and finds either titles on the page or
    titles linked to the page
    """
    payload = {
        'action': 'query',
        'format': 'json',
        'titles': page
    }
    if direction == "start":
        payload['prop'] = 'links'
        payload['pllimit'] = '500'
    else:
        payload['prop'] = 'linkshere'
        payload['lhlimit'] = '500'
    headers = {
        'User-agent': 'team nuatilus'
    }
    r = requests.get(URL_API, headers=headers, params=payload)
    pages = r.json().get("query").get("pages")
    # unknown name so get the value
    for v in pages.values():
        link_val = v
    if direction == "start":
        links = link_val.get("links")
    else:
        links = link_val.get("linkshere")
    return do_handle_titles(links, direction)

def make_return_object(*args):
    """
    makes a return object based on the input arguments
    """
    results_obj = []
    for wikilink in args:
        results_obj.append('{}{}'.format(URL_WIKI, wikilink))
    reset()
    return results_obj

def initialize_wiki_check(page, direction):
    """
    initializes the first checks for wiki race
    """
    add_links_to_all_titles(page, direction)
    check = get_page_links(page, direction)
    return check

def search_wiki(page_start, page_end):
    """
    the wiki search algorithm
    """
    reset()
    global queries
    global queries_end

    page_start = page_start.replace(' ', '_')
    check_one = initialize_wiki_check(page_start, "start")

    page_end = page_end.replace(' ', '_')
    check_two = initialize_wiki_check(page_end, "end")

    # error check to see if links are valide
    if len(check_one) == 0 or len(check_two) == 0:
        reset()
        return(["error", ERRORS[0]])

    page_start_titles = check_one

    if page_end in page_start_titles:
        return make_return_object(page_start, page_end)

    # Begin build queries start search object (dict of dict)
    queries[page_start] = dict.fromkeys(page_start_titles)
    page_end_links = get_page_links(page_end, "end")
    queries_end[page_end] = page_end_links

    # Begin Search
    for title in queries[page_start]:
        temp_titles = get_page_links(title, "start")
        if page_end in temp_titles:
            return make_return_object(
                page_start, title, page_end)
        else:
            intersect = temp_titles.intersection(queries_end[page_end])
            if len(intersect) > 1:
                return make_return_object(
                    page_start, title, intersect.pop(), page_end)
        queries[page_start][title] = dict.fromkeys(temp_titles)
    for title in queries[page_start]:
        for second_title in queries[page_start][title]:
            temp_titles = get_page_links(second_title, "start")
            if page_end in temp_titles:
                return make_return_object(
                    page_start, title, second_title, page_end)
            else:
                intersect = temp_titles.intersection(queries_end[page_end])
                if len(intersect) > 1:
                    return make_return_object(
                        page_start, title, second_title,
                        intersect.pop(), page_end)
    reset()
    return(["error", ERRORS[0]])

if __name__ == '__main__':
    """
    MAIN APP
    """
    print("Usage:")
    print("import wikirace")
