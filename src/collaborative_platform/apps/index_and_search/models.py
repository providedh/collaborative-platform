from itertools import permutations

from elasticsearch_dsl import Document, Integer, Text, Keyword, Completion, analyzer, token_filter, GeoPoint, Date

# custom analyzer for names
ascii_fold = analyzer(
    'ascii_fold',
    # we don't want to split O'Brian or Toulouse-Lautrec
    tokenizer='whitespace',
    filter=[
        'lowercase',
        token_filter('ascii_fold', 'asciifolding')
    ]
)


class Entity(Document):
    project_id = Integer()
    file_id = Integer()
    id = Text()
    name = Text(fields={'keywords': Keyword()})
    suggest = Completion(analyzer=ascii_fold)

    def clean(self):
        """
        Automatically construct the suggestion input and weight by taking all
        possible permutation of Person's name as ``input`` and taking their
        popularity as ``weight``.
        """
        self.suggest = {
            'input': [' '.join(p) for p in permutations(self.name.split())],
        }


class Person(Entity):
    forename = Text(fields={'keywords': Keyword()})
    surname = Text(fields={'keywords': Keyword()})

    class Index:
        name = 'person'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class Event(Entity):
    date = Date()

    class Index:
        name = 'event'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class Organization(Entity):
    class Index:
        name = 'organization'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class Place(Entity):
    location = GeoPoint()
    desc = Text()
    region = Text()
    country = Text()

    class Index:
        name = 'place'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class User(Document):
    id = Integer()
    name = Text(fields={'keywords': Keyword()})
    suggest = Completion(analyzer=ascii_fold)

    class Index:
        name = 'user'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    def clean(self):
        """
        Automatically construct the suggestion input and weight by taking all
        possible permutation of Person's name as ``input`` and taking their
        popularity as ``weight``.
        """
        self.suggest = {
            'input': [' '.join(p) for p in permutations(self.name.split())],
        }


class File(Document):
    name = Text(fields={'keywords': Keyword()})
    text = Text()
    id = Integer()
    project_id = Integer()

    class Index:
        name = 'file'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class Ingredient(Entity):
    class Index:
        name = 'ingredient'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class Utensil(Entity):
    class Index:
        name = 'utensil'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


class ProductionMethod(Entity):
    class Index:
        name = 'productionMethod'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
