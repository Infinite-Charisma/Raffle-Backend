import json
from dataclasses import dataclass, field
from typing import Optional
from google.cloud import tasks_v2
from google.oauth2 import service_account


@dataclass
class CloudTaskConfig:
    project_id: str
    location: str
    sa_file: str


class CloudTaskNameCreator:
    def __init__(self, client: tasks_v2.CloudTasksClient, config: CloudTaskConfig) -> None:
        self._client = client
        self._config = config

    def get_parent_name(self):
        return f"projects/{self._config.project_id}/locations/{self._config.location}"

    def get_queue_name(self, queue: str):
        return self._client.queue_path(self._config.project_id, self._config.location, queue)

    def get_task_name(self, queue: str, name: str):
        return self._client.task_path(self._config.project_id, self._config.location, queue, name)


@dataclass
class HttpTask:
    url: str
    method: tasks_v2.HttpMethod = tasks_v2.HttpMethod.POST
    headers: dict = field(default_factory=dict)
    body: Optional[str] = None
    name: Optional[str] = None


class JsonTask(HttpTask):
    def __init__(self,
                 url,
                 method: tasks_v2.HttpMethod = tasks_v2.HttpMethod.POST,
                 headers: dict = {},
                 body: dict = {},
                 name: Optional[str] = None):
        super().__init__(
            url=url,
            method=method,
            headers={
                **headers,
                "Content-Type": "application/json"
            },
            body=json.dumps(body),
            name=name
        )


def cloud_task_client_factory(config: CloudTaskConfig) -> tasks_v2.CloudTasksClient:
    json = config.sa_file
    if json:
        credentials = service_account.Credentials.from_service_account_file(json)
        return tasks_v2.CloudTasksClient(credentials=credentials)

    return tasks_v2.CloudTasksClient()


class CloudTaskQueue:
    def __init__(self, queue_name: str, client: tasks_v2.CloudTasksClient, naming: CloudTaskNameCreator):
        self._queue_name = queue_name
        self._client = client
        self._naming = naming

    def dispatch_http_task(self, task: HttpTask):
        task = {
            "http_request": {
                "http_method": task.method,
                "url": task.url,
                "headers": task.headers,
                **({"body": task.body.encode()} if task.body is not None else {})
            },
            **({"name": self._naming.get_task_name(self._queue_name, task.name)} if task.name is not None else {})
        }

        return self._client.create_task(request={
            "parent": self._naming.get_queue_name(self._queue_name),
            "task": task
        })


class CloudTasks:
    def __init__(self, config: CloudTaskConfig):
        self._config = config
        self._client = cloud_task_client_factory(config)
        self._naming = CloudTaskNameCreator(self._client, self._config)
        self._queue_cache = None

    def _queue_exists(self, queue_name):
        if self._queue_cache is None:
            parent = self._naming.get_parent_name()
            request = tasks_v2.ListQueuesRequest(
                parent=parent
            )
            self._queue_cache = self._client.list_queues(request)

        full_queue_name = self._naming.get_queue_name(queue_name)
        for q in self._queue_cache:
            if q.name == full_queue_name:
                return True
        return False

    def _create_queue(self, queue_name):
        queue = {"name": self._naming.get_queue_name(queue_name)}
        self._client.create_queue(request={"parent": self._naming.get_parent_name(), "queue": queue})
        self._queue_cache = None

    def create_queue(self, queue_name: str):
        if not self._queue_exists(queue_name):
            self._create_queue(queue_name)
        return CloudTaskQueue(queue_name, self._client, self._naming)
