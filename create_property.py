from ast import alias
import configparser
import csv
from distutils.command.config import config
import os
from unicodedata import name

from requests import request
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
from pywikibot import config2

config = configparser.ConfigParser()
config.read('config/application.config.ini')

wikibase = pywikibot.Site("my", "my")
sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
site = pywikibot.Site()

wikidata = pywikibot.Site("wikidata", "wikidata")


class CreateProperty():
    def __init__(self, wikibase):
        self.wikibase = wikibase
        self.wikibase_repo = self.wikibase.data_repository()
        self.sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
        sparql.class_entities = {}
        self.properties = {}
        self.pywikibot = pywikibot

    def capitalizeFirstLetter(self, word):
        return word.capitalize().rstrip()

    def getItemSparql(label):
        query = """
                select ?label ?s where {
                    ?s ?p ?o .
                    ?s rdfs:label ?label .
                    FILTER(lang(?label) = 'en' || lang(?label) = 'fr')
                    FILTER(?label = '""" + label + """')
                }
            """

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        print(results)
        return results

    def searchItem(label):
        if label is None:
            return True

        params = {'action': 'wbsearchentities', 'format': 'json',
                  'language': 'en', 'type': 'item', 'limit': 1, 'search': label}
        request = wikibase._simple_request(**params)
        result = request.submit()
        print(result)

        return True if result['search']['total'] > 0 else False

    def createProperty(self, nameOfLabel, label, description, datatype, aliases, property_map):

        if (self.capitalizeFirstLetter(nameOfLabel.rstrip())):
            return property_map
        propertyResult = self.getItemSparql(
            self.capitalizeFirstLetter(nameOfLabel.rstrip()))
        if (len(propertyResult['result']['bindings']) == 0):
            data = {}
            print(f'creating the property in the wikibase {nameOfLabel}')
            data['labels'] = label
            data['descriptions'] = description
            if (len(aliases) > 0):
                data['aliases'] = aliases
            addedProperty = pywikibot.PropertyPage(
                self.wikibase_repo, datatype=datatype)
            addedProperty.editEntity(data)
            print(f'The type of property is {addedProperty.type}')
            print(f'The ID of property is {addedProperty.type}')
            property_map[self.capitalizeFirstLetter(
                nameOfLabel.rstrip())] = addedProperty.id
            return property_map

        else:
            data = {}
            print(f'creating the property {nameOfLabel}')
            data['labels'] = label
            data['descriptions'] = description
            if (len(aliases) > 0):
                data['aliases'] = aliases
            existingProperty = pywikibot.PropertyPage(
                self.wikibase_repo, propertyResult['result']['bindings'][0]['s']['value'].split('/')[-1])
            existingProperty.get()
            existingProperty.editEntity(data)
            print(f'The type of property is {existingProperty.type}')
            print(f'The ID of property is {existingProperty.type}')
            property_map[self.capitalizeFirstLetter(nameOfLabel.rstrip())] = existingProperty.id
            return property_map

        

