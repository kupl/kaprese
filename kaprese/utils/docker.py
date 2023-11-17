from docker.client import DockerClient  # type: ignore
from docker.errors import APIError  # type: ignore
from docker.errors import BuildError  # type: ignore
from docker.errors import ContainerError  # type: ignore
from docker.errors import ImageNotFound  # type: ignore

from kaprese.core.config import CONFIGURE
from kaprese.utils.logging import logger


def get_docker_client() -> DockerClient:
    return DockerClient(base_url=CONFIGURE.DOCKER_SOCK_PATH)


def image_exists(name: str) -> bool:
    client = get_docker_client()
    try:
        return client.images.get(name) is not None  # type: ignore
    except (ImageNotFound, APIError):
        return False


def pull_image(name: str) -> bool:
    client = get_docker_client()
    repo, tag = name.split(":") if ":" in name else (name, "latest")
    logger.debug('Pulling image "%s:%s"', repo, tag)
    try:
        return client.images.pull(repo, tag) is not None  # type: ignore
    except APIError:
        return False


def delete_image(name: str) -> None:
    if not image_exists(name):
        logger.error('Image "%s" does not exist', name)
        return
    logger.debug('Deleting image "%s"', name)
    client = get_docker_client()
    client.images.remove(name)  # type: ignore


def build_image(
    name: str, basedir: str, build_args: dict[str, str] | None = None
) -> bool:
    client = get_docker_client()
    if build_args is None:
        build_args = {}
    try:
        logger.debug("Building image %s", name)
        logger.debug("  path: %s", basedir)
        logger.debug("  tag: %s", name)
        logger.debug("  buildargs: %s", build_args)
        image, _ = client.images.build(  # type: ignore
            path=basedir,
            tag=name,
            buildargs=build_args,
            rm=True,
            forcerm=True,
        )
        return image is not None
    except (BuildError, APIError) as e:
        logger.debug(e)
        return False


def run_command(image: str, command: str | None) -> str | None:
    client = get_docker_client()
    try:
        if not image_exists(image):
            logger.error('Image "%s" does not exist', image)
            return None
        out: bytes = client.containers.run(  # type: ignore
            image,
            f'/bin/bash -c "{command}"',
            stdout=True,
            stderr=True,
            remove=True,
        )
        return out.decode()
    except ContainerError as e:
        logger.debug(e)
        logger.error('Failed to run command "%s" in image "%s"', command, image)
    return None


def run_commands(
    image: str, commands: list[str] | None, *, workdir: str | None = None
) -> bool:
    client = get_docker_client()
    try:
        if not image_exists(image):
            logger.error("Image %s does not exist", image)
            return False
        client.containers.run(  # type: ignore
            image,
            commands,
            working_dir=workdir,
            stdout=True,
            stderr=True,
            remove=True,
        )
        return True
    except ContainerError as e:
        logger.debug(e)
        logger.warning("Failed to run commands in image %s", image)
    return False
