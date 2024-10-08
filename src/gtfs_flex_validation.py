import os
import shutil
import logging
import traceback
from pathlib import Path
from typing import Union, Any
from .config import Settings

from tcat_gtfs_csv_validator import gcv_test_release
from tcat_gtfs_csv_validator import exceptions as gcvex

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path used for download file generation.
DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'

logging.basicConfig()
logger = logging.getLogger('FLEX_VALIDATION')
logger.setLevel(logging.INFO)

DATA_TYPE = 'gtfs_flex'
SCHEMA_VERSION = 'v2.0'


class GTFSFlexValidation:
    def __init__(self, file_path=None, storage_client=None):
        self.settings = Settings()
        self.container_name = self.settings.storage_container_name
        self.storage_client = storage_client
        self.file_path = file_path
        self.file_relative_path = file_path.split('/')[-1]
        self.client = self.storage_client.get_container(container_name=self.container_name)

    # Facade function to validate the file
    # Focuses on the file name with file name validation
    # Use `is_gtfs_valid` to do more processing
    def validate(self) -> tuple[bool, str]:
        return self.is_gtfs_flex_valid()

    # use this method to do the actual validation
    # when ready to replace, replace the call in the 
    # above function.
    def is_gtfs_flex_valid(self) -> tuple[Union[bool, Any], Union[str, Any]]:
        is_valid = False
        validation_message = ''
        root, ext = os.path.splitext(self.file_relative_path)
        if ext and ext.lower() == '.zip':
            downloaded_file_path = self.download_single_file(self.file_path)
            logger.info(f' Downloaded file path: {downloaded_file_path}')
            try:
                gcv_test_release.test_release(DATA_TYPE, SCHEMA_VERSION, downloaded_file_path)
                is_valid = True
            except Exception as err:
                traceback.print_exc()
                validation_message = str(err)
                logger.error(f' Error While Validating File: {str(err)}')
            GTFSFlexValidation.clean_up(downloaded_file_path)
        else:
            logger.error(f' Failed to validate because unknown file format')

        return is_valid, validation_message

    # Downloads the file to local folder of the server
    # file_upload_path is the fullUrl of where the 
    # file is uploaded.
    def download_single_file(self, file_upload_path=None) -> str:
        is_exists = os.path.exists(DOWNLOAD_FILE_PATH)
        if not is_exists:
            os.makedirs(DOWNLOAD_FILE_PATH)

        unique_folder = self.settings.get_unique_id()
        dl_folder_path = os.path.join(DOWNLOAD_FILE_PATH, unique_folder)

        # Ensure the unique folder path is created
        os.makedirs(dl_folder_path, exist_ok=True)

        file = self.storage_client.get_file_from_url(self.container_name, file_upload_path)
        try:
            if file.file_path:
                file_path = os.path.basename(file.file_path)
                with open(f'{dl_folder_path}/{file_path}', 'wb') as blob:
                    blob.write(file.get_stream())
                logger.info(f' File downloaded to location: {dl_folder_path}/{file_path}')
                return f'{dl_folder_path}/{file_path}'
            else:
                logger.info(' File not found!')
                raise Exception('File not found!')
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            raise e

    @staticmethod
    def clean_up(path):
        if os.path.isfile(path):
            logger.info(f' Removing File: {path}')
            os.remove(path)
        else:
            folder = os.path.join(DOWNLOAD_FILE_PATH, path)
            logger.info(f' Removing Folder: {folder}')
            shutil.rmtree(folder, ignore_errors=False)
