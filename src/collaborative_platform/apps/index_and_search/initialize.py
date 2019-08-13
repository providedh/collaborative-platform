from .models import *
from elasticsearch_dsl import connections

connections.create_connection()
Person.init()
Event.init()
Organization.init()
Place.init()
