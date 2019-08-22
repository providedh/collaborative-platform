from apps.index_and_search.models import *
from elasticsearch_dsl import connections

connections.create_connection()
Person.init()
Event.init()
Organization.init()
Place.init()
User.init()
