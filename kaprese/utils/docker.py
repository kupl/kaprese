from docker.client import DockerClient  # type: ignore
from docker.errors import APIError  # type: ignore
from docker.errors import ImageNotFound  # type: ignore
from docker.models.images import Image  # type: ignore

from kaprese.core.config import CONFIGURE


def get_docker_client() -> DockerClient:
    return DockerClient(base_url=CONFIGURE.DOCKER_SOCK_PATH)


def find_image(name: str) -> Image | None:
    client = get_docker_client()
    try:
        return client.images.get(name)  # type: ignore
    except (ImageNotFound, APIError):
        return None
