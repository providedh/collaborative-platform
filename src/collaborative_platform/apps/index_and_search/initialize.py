def initialize():
    from apps.index_and_search.models import Person, Event, Organization, Place, User
    from elasticsearch_dsl import connections
    from collaborative_platform import settings
    connections.create_connection(hosts=[settings.ES_HOST])
    Person.init()
    Event.init()
    Organization.init()
    Place.init()
    User.init()
