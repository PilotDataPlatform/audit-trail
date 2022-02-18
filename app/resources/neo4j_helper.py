import requests
from ..config import ConfigClass

def http_query_node(geid):
    '''
    Get file node by geid
    '''

    node_query_url = ConfigClass.NEO4J_SERVICE + "nodes/geid/{}".format(geid)
    response = requests.get(node_query_url)
    return response