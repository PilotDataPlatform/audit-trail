import requests
from ..config import ConfigClass

def create_geid(entity_type):
    geid_url = ConfigClass.UTILITY_SERVICE + 'utility/id'
    geid = None
    geid_res = requests.get(geid_url, params={"entity_type": entity_type})
    geid_resutl = geid_res.json()

    if geid_resutl['code'] == 200: 
        geid = geid_resutl['result']

    return geid
