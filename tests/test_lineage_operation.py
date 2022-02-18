import unittest
from fastapi.testclient import TestClient
from app.main import create_app    
from app.config import ConfigClass
from .logger import Logger
import requests
import pprint

pp = pprint.PrettyPrinter(indent=4)

app = create_app()


def fetch_geid(id_type):
    ## fetch global entity id
    entity_id_url = ConfigClass.UTILITY_SERVICE + "utility/id?entity_type={}".format(id_type)
    respon_entity_id_fetched = requests.get(entity_id_url)
    if respon_entity_id_fetched.status_code == 200:
        pass
    else:
        raise Exception('Entity id fetch failed: ' + entity_id_url + ": " + str(respon_entity_id_fetched.text))
    trash_geid = respon_entity_id_fetched.json()['result']
    return trash_geid


class TestLineage(unittest.TestCase):
    client = TestClient(app)
    log = Logger(name='test_lineage_operation.log')
    entity_raw = None
    entity_processed = None

    @classmethod
    def createEntity(cls, data_type="raw"):
        payload = {
            "uploader": "gregmccoy",
            "file_name": "testfile.png",
            "path": "/data/test",
            "file_size": 123,
            "description": "A fake file used in unittests",
            "namespace": "greenroom",
            "data_type": data_type,
            "project_code": "123fake",
            "labels": [],
            "global_entity_id": fetch_geid('file_data') 
        }
        if data_type == "processed":
            payload["operator"] = "gregmccoy"
            payload["procesed_pipeline"] = "fake_pipeline"
            payload["path"] = "/data/test/processed"
        response = requests.post(ConfigClass.METADATA_API + "/v2/filedata", json=payload)
        json_payload = response.json()
        if json_payload['result']['mutatedEntities'].get('CREATE'):
            created_entity = json_payload['result']['mutatedEntities']['CREATE'][0]
        elif json_payload['result']['mutatedEntities'].get('UPDATE'):
            created_entity = json_payload['result']['mutatedEntities']['UPDATE'][0]
        return created_entity

    @classmethod
    def setUpClass(cls):
        try:
            cls.entity_raw = cls.createEntity()
            cls.entity_processed = cls.createEntity(data_type="processed")
        except Exception as e:
            print(f"Filed to setup test: {e}")
            cls.log.error(f"Failed to setup test {e}")
            raise unittest.SkipTest(f"Failed to setup test {e}")

    @classmethod
    def tearDownClass(cls):
        guid = cls.entity_raw["guid"]
        requests.delete(ConfigClass.METADATA_API + f"/v1/entity/guid/{guid}")
        guid = cls.entity_processed["guid"]
        requests.delete(ConfigClass.METADATA_API + f"/v1/entity/guid/{guid}")

    def test_01_post_lineage(self):
        self.log.info("\n")
        self.log.info(f"Test test_01_post_lineage".center(80,'-'))
        payload = {
            'input_geid': self.entity_raw["attributes"]["global_entity_id"],
            'output_geid': self.entity_processed["attributes"]["global_entity_id"],
            'project_code': '123fake',
            'pipeline_name': 'fake_pipeline',
            'description': 'A Fake unittest pipeline',
        }

        response = self.client.post("/v1/lineage/", json=payload)
        self.log.info(f"STATUS: {response.status_code}")
        self.log.info(f"Result: {response.json()}")
        result = response.json()['result']['mutatedEntities']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['CREATE'][0]['typeName'], 'Process')

        #update_attr = result['UPDATE'][0]['attributes']
        #self.assertEqual(update_attr['owner'], self.entity_raw['attributes']['owner'])
        #self.assertEqual(update_attr['qualifiedName'], self.entity_raw["attributes"]["qualifiedName"])

    def test_02_get_lineage_raw(self):
        self.log.info("\n")
        self.log.info(f"Test test_02_get_lineage_raw".center(80,'-'))
        geid = self.entity_raw["attributes"]["global_entity_id"]
        params = {
            "geid": geid
        }
        self.log.info(f"GEID: {geid}")
        response = self.client.get("/v1/lineage", params=params)
        self.log.info(f"STATUS: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.entity_raw["guid"], response.json()['result']['baseEntityGuid'])

    def test_03_get_lineage_processed(self):
        self.log.info("\n")
        self.log.info(f"Test test_03_get_lineage_processed".center(80,'-'))
        params = {
            "geid": self.entity_processed["attributes"]["global_entity_id"]
        }
        response = self.client.get("/v1/lineage", params=params)
        self.log.info(f"STATUS: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.entity_processed["guid"], response.json()['result']['baseEntityGuid'])

    def test_04_post_lineage_same_geid(self):
        self.log.info("\n")
        self.log.info(f"Test test_04_post_lineage_same_geid".center(80,'-'))
        payload = {
            'input_geid': self.entity_raw["attributes"]["global_entity_id"],
            'output_geid': self.entity_raw["attributes"]["global_entity_id"],
            'project_code': '123fake',
            'pipeline_name': 'fake_pipeline',
            'description': 'A Fake unittest pipeline',
        }

        response = self.client.post("/v1/lineage/", json=payload)
        self.log.info(f"STATUS: {response.status_code}")
        self.assertEqual(response.status_code, 400)

    def test_05_post_lineage_without_output_geid(self):
        self.log.info("\n")
        self.log.info(f"Test test_05_post_lineage_without_output_geid".center(80,'-'))
        payload = {
            'input_geid': self.entity_raw["attributes"]["global_entity_id"],
            'project_code': '123fake',
            'pipeline_name': 'fake_pipeline',
            'description': 'A Fake unittest pipeline',
        }
        try:
            response = self.client.post("/v1/lineage/", json=payload)
            self.log.info(f"STATUS: {response.status_code}")
            self.assertEqual(response.status_code, 422)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_06_post_lineage_without_project_code(self):
        self.log.info("\n")
        self.log.info(f"Test test_06_post_lineage_without_project_code".center(80,'-'))
        payload = {
            'input_geid': self.entity_raw["attributes"]["global_entity_id"],
            'output_geid': self.entity_processed["attributes"]["global_entity_id"],
            'pipeline_name': 'fake_pipeline',
            'description': 'A Fake unittest pipeline',
        }
        try:
            response = self.client.post("/v1/lineage/", json=payload)
            self.log.info(f"STATUS: {response.status_code}")
            self.assertEqual(response.status_code, 422)
        except Exception as e:
            self.log.error(e)
            raise e


    def test_07_get_lineage_both_direction(self):
        self.log.info("\n")
        self.log.info(f"Test test_07_get_lineage_both_direction".center(80,'-'))
        params = {
            "geid": self.entity_raw["attributes"]["global_entity_id"],
            "direction": "BOTH"
        }
        response = self.client.get("/v1/lineage", params=params)
        self.log.info(f"STATUS: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.entity_raw["guid"], response.json()['result']['baseEntityGuid'])
        self.assertEqual('BOTH', response.json()['result']['lineageDirection'])

    def test_08_get_lineage_output_direction(self):
        self.log.info("\n")
        self.log.info(f"Test test_08_get_lineage_output_direction".center(80,'-'))
        params = {
            "geid": self.entity_raw["attributes"]["global_entity_id"],
            "direction": "OUTPUT"
        }
        response = self.client.get("/v1/lineage", params=params)
        self.log.info(f"STATUS: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.entity_raw["guid"], response.json()['result']['baseEntityGuid'])
        self.assertEqual('OUTPUT', response.json()['result']['lineageDirection'])
