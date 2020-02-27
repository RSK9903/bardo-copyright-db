from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from lccnorm import is_valid, normalize, InvalidLccnError

from helpers.errors import DataError


class Elastic():
    def __init__(self):
        self.client = None
    
    def init_app(self, app):
        self.client = Elasticsearch(app.config['ELASTICSEARCH_INDEX_URI'])
    
    def create_search(self, index):
        return Search(using=self.client, index=index)

    def query_regnum(self, regnum, page=0, perPage=10):
        startPos, endPos = Elastic.getFromSize(page, perPage)
        search = self.create_search('cce')
        nestedQ = Q('term', registrations__regnum=regnum)
        nestedSearch = search.query('nested', path='registrations', query=nestedQ)[startPos:endPos]
        return nestedSearch.execute()
    
    def query_rennum(self, rennum, page=0, perPage=10):
        startPos, endPos = Elastic.getFromSize(page, perPage)
        search = self.create_search('ccr')
        renewalSearch = search.query('term', rennum=rennum)[startPos:endPos]
        return renewalSearch.execute()
    
    def query_fulltext(self, queryText, page=0, perPage=10):
        startPos, endPos = Elastic.getFromSize(page, perPage)
        search = self.create_search('cce,ccr')
        renewalSearch = search.query('query_string', query=queryText)[startPos:endPos]
        return renewalSearch.execute()

    def query_lccn(self, lccn, page=0, perPage=10):
        startPos, endPos = Elastic.getFromSize(page, perPage)
        search = self.create_search('cce')
        normalLCCN = Elastic.normalizeAndValidateLCCN(lccn)
        renewalSearch = search.query('term', lccns=normalLCCN)[startPos:endPos]
        return renewalSearch.execute()

    @staticmethod
    def getFromSize(page, perPage):
        startPos = page * perPage
        endPos = startPos + perPage
        return startPos, endPos

    @staticmethod
    def normalizeAndValidateLCCN(lccn):
        try:
            normalizedLCCN = normalize(lccn)
            if is_valid(normalizedLCCN):
                return normalizedLCCN
        except InvalidLccnError:
            pass

        raise DataError('Invalid LCCN queried')


elastic = Elastic()
