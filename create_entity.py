import configparser
import csv
import sys
import traceback
import time
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON

config = configparser.ConfigParser()
config.read('config/application.config.ini')

wikibase = pywikibot.Site("my", "my")

class CreateEntity:
    def __init__(self, wikibase):
        self.wikibase = wikibase
        self.wikibase_repo = wikibase.data_repository()
        self.sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
        self.class_entities = {}
        self.properties = {}

    def get_class_entity(self):
        labels = [""]
        # add some class labels we need to this particular list later.
        

    