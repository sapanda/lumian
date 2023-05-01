from abc import ABC, abstractmethod
import grpc
from google.api_core import exceptions
from google.cloud.run_v2.services.services.client import ServicesClient
from google.cloud.tasks_v2 import CloudTasksClient
from google.cloud.tasks_v2.services.cloud_tasks.transports \
    import CloudTasksGrpcTransport
from google.cloud.tasks_v2.types import HttpMethod

from app import settings


class GCloudClientInterface(ABC):
    """Interface for OpenAI Client"""
    @abstractmethod
    def create_task(self, path: str, payload: dict):
        """Add a task to the queue"""
        pass


class GCloudClient(GCloudClientInterface):
    def __init__(self,
                 project_id: str,
                 location: str,
                 queue_name: str,
                 service_name: str,
                 ) -> None:
        self.project_id = project_id
        self.location = location
        self.queue_name = queue_name
        self.service_name = service_name
        self.tasks_client = CloudTasksClient()
        self.run_client = ServicesClient()
        self.service_url = self._get_cloud_run_service_url()

    def _get_cloud_run_service_url(self) -> str:
        """Generate the Cloud Run service URL."""
        name = f"projects/{self.project_id}/locations/{self.location}/services/{self.service_name}"
        response = self.run_client.get_service(name=name)
        return response.uri

    def create_task(self, path, payload):
        """Create a Google Cloud Task task for a given service."""
        # Create the task queue path
        parent = self.tasks_client.queue_path(self.project_id,
                                              self.location,
                                              self.queue_name)

        # Get the Cloud Run service URL
        service_url = self._get_cloud_run_service_url()

        # Create the task
        task = {
            "http_request": {
                "http_method": HttpMethod.POST,
                "url": f"{service_url}{path}",
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": payload.encode(),
            }
        }

        try:
            response = self.tasks_client.create_task(
                request={"parent": parent, "task": task}
            )
            print(f"Task created: {response.name}")
            return response.name
        except exceptions.GoogleAPICallError as error:
            print(f"Error creating task: {error}")
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

    def create_task(self, path, payload):
        task = {
            'http_request': {
                'http_method': HttpMethod.POST,
                'url': f"{self.service_url}/{path}",
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": payload.encode(),
            }
        }

        response = self.client.create_task(task=task, parent=self.queue_name)
        print(f"Task created: {response.name}")
        return response.name


if settings.DEPLOY_MODE == settings.ModeEnum.local or \
   settings.DEPLOY_MODE == settings.ModeEnum.github:
    channel = grpc.insecure_channel(settings.GCLOUD_EMULATOR_URL)
    gcloud_client = GCloudEmulatorClient(
        channel=channel,
        service_url=settings.GCLOUD_EMULATOR_SERVICE_URL
    )
else:
    gcloud_client = GCloudClient(
        project_id=settings.GCLOUD_PROJECT_ID,
        location=settings.GCLOUD_LOCATION,
        queue_name=settings.GCLOUD_QUEUE_NAME,
        service_name=settings.GCLOUD_API_SERVICE_NAME
    )
