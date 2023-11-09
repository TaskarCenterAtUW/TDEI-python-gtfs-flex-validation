import os
import json
import unittest
from unittest.mock import MagicMock
from src.serializer.gtfx_flex_serializer import GTFSFlexUpload, GTFSFlexUploadData, Request, Meta, Response

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/test_flex_payload.json')
TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class TestGTFSFlexUpload(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA
        self.upload = GTFSFlexUpload(data)

    def test_message(self):
        self.upload.message = 'New message'
        self.assertEqual(self.upload.message, 'New message')

    def test_message_type(self):
        self.assertEqual(self.upload.message_type, 'gtfs-flex-upload')
        self.upload.message_type = 'New messageType'
        self.assertEqual(self.upload.message_type, 'New messageType')

    def test_message_id(self):
        self.upload.message_id = 'New messageId'
        self.assertEqual(self.upload.message_id, 'New messageId')

    def test_published_date(self):
        self.assertEqual(self.upload.published_date, '2023-02-08T08:33:36.267213Z')
        self.upload.published_date = '2023-05-24'
        self.assertEqual(self.upload.published_date, '2023-05-24')

    def test_data(self):
        self.assertIsInstance(self.upload.data, GTFSFlexUploadData)
        self.assertEqual(self.upload.data.stage, 'Flex-Upload')
        self.upload.data.stage = 'Test stage'
        self.assertEqual(self.upload.data.stage, 'Test stage')

        # Add more assertions for other properties of GTFSFlexUploadData

    def test_to_json(self):
        self.upload.data.to_json = MagicMock(return_value={})
        json_data = self.upload.to_json()
        self.assertIsInstance(json_data, dict)
        self.assertEqual(json_data['message_type'], 'gtfs-flex-upload')
        self.assertEqual(json_data['published_date'], '2023-02-08T08:33:36.267213Z')

    def test_data_from(self):
        message = TEST_DATA
        upload = GTFSFlexUpload.data_from(json.dumps(message))
        self.assertIsInstance(upload, GTFSFlexUpload)
        self.assertEqual(upload.message_type, 'gtfs-flex-upload')
        self.assertEqual(upload.published_date, '2023-02-08T08:33:36.267213Z')


class TestGTFSFlexUploadData(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']
        self.upload_data = GTFSFlexUploadData(data)

    def test_stage(self):
        self.assertEqual(self.upload_data.stage, 'Flex-Upload')
        self.upload_data.stage = 'Test stage'
        self.assertEqual(self.upload_data.stage, 'Test stage')

    def test_tdei_record_id(self):
        self.assertEqual(self.upload_data.tdei_record_id, 'c8c76e89f30944d2b2abd2491bd95337')
        self.upload_data.tdei_record_id = 'Test record ID'
        self.assertEqual(self.upload_data.tdei_record_id, 'Test record ID')

    def test_tdei_project_group_id(self):
        self.assertEqual(self.upload_data.tdei_project_group_id, '0b41ebc5-350c-42d3-90af-3af4ad3628fb')
        self.upload_data.tdei_project_group_id = 'Test org ID'
        self.assertEqual(self.upload_data.tdei_project_group_id, 'Test org ID')

    def test_user_id(self):
        self.assertEqual(self.upload_data.user_id, 'c59d29b6-a063-4249-943f-d320d15ac9ab')
        self.upload_data.user_id = 'Test user ID'
        self.assertEqual(self.upload_data.user_id, 'Test user ID')

    # Add more test cases for other properties of GTFSFlexUploadData


class TestRequest(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']
        self.request = Request(data)

    def test_tdei_project_group_id(self):
        self.assertEqual(self.request.tdei_project_group_id, '0b41ebc5-350c-42d3-90af-3af4ad3628fb')
        self.request.tdei_project_group_id = 'Test org ID'
        self.assertEqual(self.request.tdei_project_group_id, 'Test org ID')

    # Add more test cases for other properties of Request


class TestMeta(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']['meta']
        self.meta = Meta(data)

    def test_file_upload_path(self):
        self.assertEqual(self.meta.file_upload_path,
                         'https://tdeisamplestorage.blob.core.windows.net/gtfsflex/2023%2FFEBRUARY%2F0b41ebc5-350c-42d3-90af-3af4ad3628fb%2Fvalid_c8c76e89f30944d2b2abd2491bd95337.zip')
        self.meta.file_upload_path = 'Test file path'
        self.assertEqual(self.meta.file_upload_path, 'Test file path')

    # Add more test cases for other properties of Meta


class TestResponse(unittest.TestCase):

    def setUp(self):
        data = TEST_DATA['data']['response']
        self.response = Response(data)

    def test_success(self):
        self.assertEqual(self.response.success, True)
        self.response.success = False
        self.assertEqual(self.response.success, False)


if __name__ == '__main__':
    unittest.main()
