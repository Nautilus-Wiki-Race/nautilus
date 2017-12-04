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
    global all_titles
    all_titles = all_titles.union(titles)


def clean_wiki_page_title(page):
    """
    cleans wikipediat page for synchronicity and validating GET request
    """
    return '_'.join([word.capitalize() for word in page.split(' ')])


class WikiRace():
    """
    class to handle wikipedia website and all related links
    """

    def __init__(self, direction, page, steps=0):
        """
        instantiates a wikipedia node based on the name of the page
        """
        self.page = page
        if direction == "start":
            self.child_links = {}
            self.furthest_parent = steps
        else:
            self.parent_links = {}
            self.furthest_child = steps

    def do_handle_titles(self, links, direction):
        """
        handles the titles by adding to self attributes
        """
        if links is None:
            return
        titles = set()
        for link in links:
            this_title = clean_wiki_page_title(link.get('title'))
            titles.add(this_title)
        titles = remove_duplicate_links(titles, direction)
        add_links_to_all_titles(titles, direction)
        if direction == "start":
            for name in titles:
                self.child_links[name] = WikiRace(
                    "start", name, self.furthest_parent + 1)
        else:
            for name in titles:
                self.parent_links[name] = WikiRace(
                    "end", name, self.furthest_child + 1)

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
            'User-agent': 'holberton 0.1'
        }
        url = "https://en.wikipedia.org/w/api.php"
        r = requests.get(url, headers=headers, params=payload)
        pages = r.json().get("query").get("pages")
        # unknown name so get the value
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
        variations = [
            title,
            title.lower(),
            title.capitalize()
        ]
        if direction == "start":
            for word in variations:
                if word in self.child_links:
                    return True
        else:
            for word in variations:
                if word in self.parent_links:
                    return True
        return False

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
    page_start = clean_wiki_page_title(page_start)
    all_titles.add(page_start)
    # build start root WikiRace Node
    start_root = WikiRace("start", page_start, 0)
    start_root.get_page_links("start")

    # build end root WikiRace Node
    page_end = clean_wiki_page_title(page_end)
    end_root = WikiRace("end", page_end, 0)
    end_root.get_page_links("end")

    # error check to see if links are valid
    if len(start_root.child_links) == 0 or len(end_root.parent_links) == 0:
        reset()
        return(["error", ERRORS[0]])

    page_start_titles = check_one

    # check 1 degree of separation
    if start_root.match_title_with_self(page_end, "start"):
        return make_return_object(start_root.page, page_end)

    # Begin Search
    for title, wiki_node in start_root.child_links.items():
        wiki_node.get_page_links("start")
        if wiki_node.match_title_with_self(page_end, "start"):
            return make_return_object(
                page_start, title, page_end)
        else:
            for page_end_title, wiki_node_end in end_root.parent_links.items():
                if wiki_node.match_title_with_self(page_end_title, "end"):
                    return make_return_object(
                        page_start,
                        title,
                        page_end_title,
                        page_end)
    # search new step
    for title, wiki_node in start_root.child_links.items():
        for second_title in queries[page_start][title]:
            temp_titles = get_titles_on_page(second_title)
            if page_end in temp_titles:
                return make_return_object(
                    page_start, title.replace(' ', '_'),
                    second_title.replace(' ', '_'), page_end)
            else:
                for page_end_link in queries_end[page_end]:
                    if page_end_link in temp_titles:
                        return make_return_object(
                            page_start, title.replace(' ', '_'),
                            second_title.replace(' ', '_'),
                            page_end_link.replace(' ', '_'),
                            page_end)
    reset()
    return(["error", ERRORS[0]])



if __name__ == '__main__':
    """
    MAIN APP
    """
    print("Usage:")
    print("import wikirace")
