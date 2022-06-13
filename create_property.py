import configparser
import csv
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON

config = configparser.ConfigParser()
config.read('config/application.config.ini')

wikibase = pywikibot.Site('my', 'my')
sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
site = pywikibot.Site()
wikidata = pywikibot.Site('wikidata', 'wikidata')


class CreateProperty:
    def __init__(self, wikibase):
        self.wikibase = wikibase
        self.wikibase_repo = wikibase.data_repository()
        self.sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
        self.class_entities = {}
        self.properties = {}
        self.pywikibot = pywikibot

    def is_not_used(self):
        pass

    def capitaliseFirstLetter(self, word):
        self.is_not_used()
        return word.capitalize()

    def get_item_with_sparql(self, label):
        self.is_not_used()
        query = """
            select ?label ?s where {
                ?s ?p ?o.
                ?s rdfs:label ?label.
                FILTER(LANG(?label) = 'en' || LANG(?label) = 'fr')
                FILTER(?label = '""" + label + """'@en)
            }
        """

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        print(results)
        return results

    def processProperty(self, labelstring, label, description, datatype, aliases, property_map):
        if self.capitaliseFirstLetter(labelstring.rstrip()) in property_map:
            print("Property already exists: " + labelstring)
            return property_map

        property_result = self.get_item_with_sparql(self.capitaliseFirstLetter(labelstring.rstrip()))
        if len(property_result['results']['bindings']) == 0:
            data = {}
            print(f"Creating property: {labelstring}")
            data['labels'] = label
            data['descriptions'] = description
            if len(aliases) > 0:
                data['aliases'] = aliases
            new_property = pywikibot.PropertyPage(self.wikibase_repo, datatype=datatype)
            new_property.editEntity(data)

            print(new_property.type, new_property.id)
            property_map[self.capitaliseFirstLetter(labelstring.rstrip())] = new_property.id
            return property_map

        else:
            data = {}
            print(f"Creating the property: {labelstring}")
            data['labels'] = label
            data['descriptions'] = description
            if len(aliases) > 0:
                data['aliases'] = aliases
            existing_property = pywikibot.PropertyPage(self.wikibase_repo,
                                                       property_result['results']['bindings'][0]['s']['value'].split(
                                                           "/")[-1])
            existing_property.get()
            existing_property.editEntity(data)

            print(existing_property.type, existing_property.id)
            property_map[self.capitaliseFirstLetter(labelstring.rstrip())] = existing_property.id
            return property_map

    def readPropertyCSV(self, file_name):
        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            property_map = {}
            for row in csv_reader:
                print(f'Processing the line number of {line_count}')
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count = line_count + 1
                else:
                    try:
                        description = ""
                        aliases = ""
                        if not row[2]:
                            description = {"en": self.capitaliseFirstLetter(row[0].rstrip() + " : property")}
                        else:
                            description = {"en": self.capitaliseFirstLetter(row[2].rstrip())}
                        if len(row[3]) > 0:
                            aliases = {"en": self.capitaliseFirstLetter(row[3]).rstrip().split(",")}
                        label = {"en": row[0].rstrip().lstrip().lower()}
                        labelstring = row[0].rstrip().lstrip().lower()
                        datatype = row[1]
                        property_map = self.processProperty(labelstring, label, description, datatype, aliases,
                                                            property_map)
                    except Exception as e:
                        print(f'the exception is {e}')
            print(f'Processing is done, {line_count}')


if __name__ == "__main__":
    CreateProperty(wikibase).readPropertyCSV("data/properties.csv")
    quit(code=None)
