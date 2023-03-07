import os

from tdei_gtfs_csv_validator import gcv_test_release
from tdei_gtfs_csv_validator import exceptions as gcvex

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = '/Users/nareshkumardevalapally/Documents/Projects/tdei/repo/TDEI-python-gtfs-flex-validation/src'

DOWNLOAD_FILE_PATH = os.path.join(ROOT_DIR, 'downloads')

DATA_TYPE = 'gtfs_flex'
SCHEMA_VERSION = 'v2.0'
fileName = 'success_1_all_attrs.zip'
downloaded_file_path = f'{DOWNLOAD_FILE_PATH}/{fileName}'

print(downloaded_file_path)

try:
    result = gcv_test_release.test_release(DATA_TYPE, SCHEMA_VERSION, downloaded_file_path)
    print('Result')
    print(result)
    is_valid = True
except Exception as err:
    validation_message = str(err)
    print('Error')
    print(err)