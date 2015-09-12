'''
App that parses the feed from arxiv.org.
Collects titles, authors, and abstracts from the updated feed.

Hard coded for hep-th RSS:

http://export.arxiv.org/rss/hep-th

but the others can be accessed by the same schema.
'''
from __future__ import division

from pyparsing import nestedExpr
import feedparser

def parse_feed(feed_path):
    '''
    Takes path to an RSS feed for an arXiv subject and builds a list of
    dictionaries with parsed information like title, authors, whether the entry
    was updated or not and returns the dictionary.
    '''
    ## parse feed
    feed = feedparser.parse(feed_path)

    parsed_feed = list()

    for preprint in feed['entries']:

        preprint_parsed = dict()
        title, updated, subject = parse_title(preprint['title'])
        authors, authors_html_string = parse_authors(preprint['authors'])
        link = preprint['id']
        abstract = preprint['summary']

        preprint_parsed['link'] = link
        preprint_parsed['title'] = title
        preprint_parsed['authors'] = authors
        preprint_parsed['authors_html_string'] = authors_html_string
        preprint_parsed['abstract'] = abstract
        preprint_parsed['subject'] = subject
        preprint_parsed['updated'] = updated

        parsed_feed.append(preprint_parsed)

    return parsed_feed

def parse_title(title):
    '''
    Parses the title returned from the arxiv RSS

    Returns a triple (parse_title, updated, subject)
    with the parsed title, a boolean indicating if the preprint is new or
    updated, and the parsed subject (i.e. [hep-th]). This lets us identify
    cross-lists if we want.
    '''

    ## gets the index of where the metadata begins
    end_idx = title.rfind('(')

    metadata_parsed_list = nestedExpr('(',')').parseString(title[end_idx:])

    ## the output is a doubly nested list. The last token indicates
    ## whether the preprint was updated or not
    updated = metadata_parsed_list[-1][-1] == u'UPDATED'

    if updated:
        subject = metadata_parsed_list[-1][-2]
    else:
        subject = metadata_parsed_list[-1][-1]

    subject = subject[1:-1] ## trim the bracket

    return title[:end_idx], updated, subject

def parse_authors(authors):
    '''
    Parses the author list returned from the arxiv RSS.

    Returns a list of the authors.
    '''

    authors_string = authors[0]['name']
    authors_with_tags = authors_string.split(',')

    authors = list()

    ## strip HTML
    for author_tagged in authors_with_tags:
        left_idx = author_tagged.find('>') + 1
        author = author_tagged[left_idx:-4]
        authors.append(author)

    return authors, authors_string

if __name__ == '__main__':
    ## hard coded for hep-th channel
    feed_path = 'http://export.arxiv.org/rss/hep-th'
    parsed = parse_feed(feed_path)

    for idx, preprint in enumerate(parsed):
        if not preprint['updated'] and preprint['subject'] == 'hep-th':
            print '%d. %s' % (idx, preprint['title'])
            print preprint['authors']
            print
