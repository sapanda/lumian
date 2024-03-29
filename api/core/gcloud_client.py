from abc import ABC, abstractmethod
import grpc
from google.api_core import exceptions
from google.cloud.run_v2.services.services.client import ServicesClient
from google.cloud.tasks_v2 import CloudTasksClient
from google.cloud.tasks_v2.services.cloud_tasks.transports \
    import CloudTasksGrpcTransport
from google.cloud.tasks_v2.types import HttpMethod
from google.protobuf.duration_pb2 import Duration
import logging
from typing import Optional

from app import settings


logger = logging.getLogger(__name__)


class GCloudClientInterface(ABC):
    """Interface for OpenAI Client"""
    @abstractmethod
    def create_task(self, path: str, payload: dict, timeout_minutes: int):
        """Add a task to the queue"""
        pass


class GCloudClient(GCloudClientInterface):
    def __init__(self,
                 project_id: str,
                 location: str,
                 queue_name: str,
                 service_name: str,
                 service_url_override: str = None,
                 ) -> None:
        self.project_id = project_id
        self.location = location
        self.queue_name = queue_name
        self.service_name = service_name
        self.tasks_client = CloudTasksClient()

        if service_url_override:
            self.service_url = service_url_override
        else:
            self.run_client = ServicesClient()
            self.service_url = self._get_cloud_run_service_url()

    def _get_cloud_run_service_url(self) -> str:
        """Generate the Cloud Run service URL."""
        name = (f"projects/{self.project_id}/locations/{self.location}/"
                f"services/{self.service_name}")
        response = self.run_client.get_service(name=name)
        return response.uri

    def create_task(self, path: str, payload: dict,
                    timeout_minutes: Optional[int] = -1):
        """Create a Google Cloud Task for a given service."""
        parent = self.tasks_client.queue_path(self.project_id,
                                              self.location,
                                              self.queue_name)
        task = {
            "http_request": {
                "http_method": HttpMethod.POST,
                "url": f"{self.service_url}/{path}",
                "headers": {
                    "Content-Type": "application/json",
                    "X-Task-Caller": "background-task"
                },
                "body": payload.encode(),
            },
        }

        if timeout_minutes > 0:
            duration = Duration()
            duration.FromSeconds(timeout_minutes * 60)
            task["dispatch_deadline"] = duration

        try:
            response = self.tasks_client.create_task(
                request={"parent": parent, "task": task}
            )

            logger.info(f"Task created: {response.name}")
            return response.name
        except exceptions.GoogleAPICallError as error:
            logger.exception("Error creating task", exc_info=error)
            return None


class GCloudEmulatorClient(GCloudClientInterface):
    def __init__(self, channel: grpc.Channel, service_url: str) -> None:
        transport = CloudTasksGrpcTransport(channel=channel)
        self.client = CloudTasksClient(transport=transport)
        self._create_queue()
        self.service_url = service_url

    def _create_queue(self):
        parent = 'projects/dev/locations/here'
        self.queue_name = parent + '/queues/test'

        try:
            self.client.create_queue(queue={'name': self.queue_name},
                                     parent=parent)
        except exceptions.AlreadyExists:
            pass

    def create_task(self, path: str, payload: dict,
                    timeout_minutes: Optional[int] = -1):
        task = {
            "http_request": {
                "http_method": HttpMethod.POST,
                "url": f"{self.service_url}/{path}",
                "headers": {
                    "Content-Type": "application/json",
                    "X-Task-Caller": "background-task"
                },
                "body": payload.encode(),
            }
        }

        response = self.client.create_task(task=task, parent=self.queue_name)
        logger.info(f"Task created: {response.name}")
        return response.name


class GCloudMockClient(GCloudClientInterface):
    def create_task(self, path: str, payload: dict,
                    timeout_minutes: Optional[int] = -1):
        return ""


if settings.TESTING:
    # Use a mock client for testing - technically should be injected
    client = GCloudMockClient()

elif settings.DEPLOY_MODE == settings.ModeEnum.local or \
     settings.DEPLOY_MODE == settings.ModeEnum.github:
    # Use a local emulator for development
    channel = grpc.insecure_channel(settings.GCLOUD_EMULATOR_URL)
    client = GCloudEmulatorClient(
        channel=channel,
        service_url=settings.GCLOUD_EMULATOR_SERVICE_URL
    )

else:
    # Use Google Cloud Tasks for deployment
    client = GCloudClient(
        project_id=settings.GCLOUD_PROJECT_ID,
        location=settings.GCLOUD_LOCATION,
        queue_name=settings.GCLOUD_QUEUE_NAME,
        service_name=settings.GCLOUD_API_SERVICE_NAME,
        service_url_override=settings.GCLOUD_API_SERVICE_URL,
    )
