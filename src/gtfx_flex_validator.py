import logging
import uuid
import urllib.parse
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from .config import Settings
from .gtfs_flex_validation import GTFSFlexValidation
from .serializer.gtfx_flex_serializer import GTFSFlexUpload
from .models.file_upload_msg import FileUploadMsg
import threading
import time

logging.basicConfig()
logger = logging.getLogger('FLEX_VALIDATOR')
logger.setLevel(logging.INFO)


class GTFSFlexValidator:
    _settings = Settings()

    def __init__(self):
        self.core = Core()
        self.settings = Settings()
        self._subscription_name = self.settings.request_subscription
        self.request_topic = self.core.get_topic(topic_name=self.settings.request_topic_name,max_concurrent_messages=self.settings.max_concurrent_messages)
        # self.response_topic = self.core.get_topic(topic_name=self.settings.response_topic_name)
        self.logger = self.core.get_logger()
        self.storage_client = self.core.get_storage_client()
        self.listening_thread = threading.Thread(target=self.subscribe)
        self.listening_thread.start()

    def subscribe(self) -> None:
        # Process the incoming message
        def process(message) -> None:
            if message is not None:
                gtfs_upload_message = QueueMessage.to_dict(message)
                upload_msg = FileUploadMsg.from_dict(gtfs_upload_message)
                logger.info(upload_msg)
                self.process_message(upload_msg)
            else:
                logger.info(' No Message')

        self.request_topic.subscribe(subscription=self._subscription_name, callback=process)
    
    def process_message(self, upload_msg: FileUploadMsg) -> None:

        try:
            file_upload_path = urllib.parse.unquote(upload_msg.data.file_upload_path)
            logger.info(f' Received message for Project Group: {upload_msg.data.tdei_project_group_id}')
            logger.info(file_upload_path)
            if file_upload_path:
                # Do the validation in the other class
                validator = GTFSFlexValidation(file_path=file_upload_path, storage_client=self.storage_client)
                validation = validator.validate()
                self.send_status(valid=validation[0], upload_message=upload_msg,
                                        validation_message=validation[1])
            else:
                logger.info(' No file Path found in message!')
        except Exception as e:
            logger.error(f' Error processing message: {e}')
            self.send_status(valid=False, upload_message=upload_msg, validation_message=str(e))

    def send_status(self, valid: bool, upload_message: FileUploadMsg, validation_message: str = '') -> None:
        response_message = {
                "file_upload_path": upload_message.data.file_upload_path,
                "user_id": upload_message.data.user_id ,
                "tdei_project_group_id": upload_message.data.tdei_project_group_id,
                "success": valid,
                "message": validation_message
            }
        logger.info(f' Publishing new message with ID: {upload_message.messageId} with status: {valid} and Message: {validation_message}')
        data = QueueMessage.data_from({
            'messageId': upload_message.messageId,
            'message':  'Validation complete',
            'messageType': upload_message.messageType,
            'data': response_message
        })
        self.send_response(data=data)

    def send_response(self, data: QueueMessage) -> None:
        try:
            response_topic = self.core.get_topic(self.settings.response_topic_name)
            response_topic.publish(data=data)
        except Exception as e:
            logger.error(f'Error sending response: {e}')

    def stop_listening(self):
        self.listening_thread.join(timeout=0)