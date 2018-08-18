# -*- coding: utf-8 -*-
import scrapy
import re


def add_backslash(query):
    special_key = ['+', '-', '&', '|', '!', '(', ')', '{', '}', '[', ']', '^', '*', '\"', '~', '?', ':', '\\']
    escaped_query = ''
    for c in query:
        if c not in special_key:
            escaped_query = escaped_query + c
        else:
            escaped_query = escaped_query + '\\' + c
    return escaped_query


class Query:
    def __init__(self, **kwargs):
        self.params = kwargs
        if 'size' not in kwargs.keys():
            self.params['size'] = 10
        if 'offset' not in kwargs.keys():
            self.params['offset'] = 0

    def next(self):
        self.params['offset'] = self.params['offset'] + self.params['size']


class UniportUrls:
    base = "https://www.ebi.ac.uk/proteins/api"
    target_databases = ['/proteins?',  '/features?', '/variation?']
    required_keys = ['accession', 'isoform', 'goterms', 'keywords', 'ec', 'gene', 'protein', 'organism', 'taxid', 'pubmed']

    def gen(self, query):
        if not isinstance(query, Query):
            raise TypeError
        valid_params = False
        for key in query.params:
            if key in self.required_keys:
                valid_params = True
                break
        if not valid_params:
            raise ValueError
        params = ''
        for key, value in query.params.items():
            params = params + key + '=' + str(value) + '&'
        params = params[0:-1]
        for database in self.target_databases:
            yield self.base + database + params


class UniprotSpider(scrapy.Spider):
    name = 'uniprot'
    allowed_domains = ['www.ebi.ac.uk']

    def __init__(self, *args, **kwargs):
        self.query = Query(**kwargs)
        super(UniprotSpider, self).__init__()

    def start_requests(self):
        headers = {'User-Agent': 'Python', 'email': 'guanxiux@mail.ustc.edu.cn', "Accept": 'application/xml'}
        for url in UniportUrls().gen(self.query):
            self.log('Request for %s' % url)
            yield scrapy.FormRequest(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        with open('%s_%s.xml' % (re.split('[?/]', response.url)[-2], re.split('[?/]', response.url)[-1]), 'wb') as f:
            f.write(response.body)
