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
ERRORS = [
    "NOT FOUND: Please ensure that you provide a proper Wikipedia Pages",
    "TIMEOUT: Please let us know how to improve our algorithm"
]

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


def remove_duplicate_links(titles, from_start):
    """
    cleans (i.e. removes) titles that should not be in new titles list
    """
    if from_start is True:
        global all_titles
        return (titles.difference(all_titles))
    else:
        global all_titles_reversed
        return (titles.difference(all_titles_reversed))


def make_return_object(*args):
    """
    makes a return object based on the input arguments
    """
    results_obj = []
    wiki_url = "https://en.wikipedia.org/wiki/"
    for wikilink in args:
        results_obj.append('{}{}'.format(wiki_url, wikilink))
    reset()
    return results_obj


def search_wiki(page_start, page_end):
    """
    the wiki search algorithm
    """
    reset()
    global all_titles
    global queries
    global all_titles_reversed
    global queries_end

    # Build string replacements for links
    page_start = page_start.replace(' ', '_')
    check_one = get_titles_on_page(page_start)
    page_end_replaced = page_end.replace(' ', '_')
    check_two = get_titles_on_page(page_end_replaced)

    # error check to see if links are valide
    if len(check_one) == 0 or len(check_two) == 0:
        reset()
        return(["error", ERRORS[0]])
    all_titles.add(page_start)
    page_start_titles = check_one

    # check 1 degree of separation
    if page_end in page_start_titles:
        return make_return_object(page_start, page_end_replaced)

    # Begin build queries start search object (dict of dict)
    page_start_titles = remove_duplicate_links(page_start_titles, True)
    all_titles = all_titles.union(page_start_titles)
    queries[page_start] = dict.fromkeys(page_start_titles)

    # Begin build queries end search object (dict of dict)
    # all_titles_reversed.add(page_end)
    # all_titles_reversed = all_titles_reversed.union(page_end_links)
    page_end_links = get_titles_linked_to_page(page_end_replaced)
    queries_end[page_end_replaced] = dict.fromkeys(page_end_links)

    # Begin Search
    for title in queries[page_start]:
        temp_titles = get_titles_on_page(title)
        temp_titles = remove_duplicate_links(temp_titles, True)
        if page_end in temp_titles:
            return make_return_object(
                page_start, title.replace(' ', '_'), page_end_replaced)
        else:
            for page_end_link in queries_end[page_end_replaced]:
                if page_end_link in temp_titles:
                    return make_return_object(
                        page_start,
                        title.replace(' ', '_'),
                        page_end_link.replace(' ', '_'),
                        page_end_replaced)
                # temp_end_titles = get_titles_linked_to_page(page_end_link)
                # temp_end_titles = remove_duplicate_links(temp_end_titles, False)
                # all_titles_reversed = all_titles_reversed.union(temp_end_titles)
                # queries_end[page_end_replaced][page_end_link] = dict.fromkeys(temp_end_titles)
        all_titles = all_titles.union(temp_titles)
        queries[page_start][title] = dict.fromkeys(temp_titles)
    for title in queries[page_start]:
        for second_title in queries[page_start][title]:
            temp_titles = get_titles_on_page(second_title)
            temp_titles = remove_duplicate_links(temp_titles, True)
            if page_end in temp_titles:
                return make_return_object(
                    page_start, title.replace(' ', '_'),
                    second_title.replace(' ', '_'), page_end_replaced)
            else:
                for page_end_link in queries_end[page_end_replaced]:
                    if page_end_link in temp_titles:
                        return make_return_object(
                            page_start, title.replace(' ', '_'),
                            second_title.replace(' ', '_'),
                            page_end_link.replace(' ', '_'),
                            page_end_replaced)
    reset()
    return(["error", ERRORS[0]])

if __name__ == '__main__':
    """
    MAIN APP
    """
    print("Usage:")
    print("import wikirace")
