from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

from docker.client import DockerClient  # type: ignore
from docker.errors import (  # type: ignore
    APIError,
    BuildError,
    ContainerError,
    ImageNotFound,
)
from docker.models.containers import Container  # type: ignore

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
        logger.debug('Image "%s" does not exist', name)
        return
    logger.debug('Deleting image "%s"', name)
    client = get_docker_client()
    client.images.remove(name)  # type: ignore


def build_image(
    name: str,
    basedir: str,
    build_args: dict[str, str] | None = None,
    *,
    nocache: bool = False,
) -> bool:
    logger.debug('Building image "%s"', name)
    logger.debug("  path: %s", basedir)
    logger.debug("  tag: %s", name)
    logger.debug("  buildargs: %s", build_args)
    client = get_docker_client()
    if build_args is None:
        build_args = {}
    try:
        image, _ = client.images.build(  # type: ignore
            path=basedir,
            tag=name,
            buildargs=build_args,
            nocache=nocache,
            rm=True,
            forcerm=True,
        )
        return image is not None
    except (BuildError, APIError) as e:
        logger.debug('Failed to build image "%s"', name)
        logger.debug(e)
        return False


def run_command(
    image: str,
    command: str | None = None,
    workdir: str | None = None,
) -> str | None:
    client = get_docker_client()
    try:
        if not image_exists(image):
            logger.debug('Image "%s" does not exist', image)
            return None
        kwargs: dict[str, Any] = {}
        if command is not None:
            kwargs["command"] = f'/bin/bash -c "{command}"'
        if workdir is not None:
            kwargs["working_dir"] = workdir
        kwargs.update(
            {
                "stdout": True,
                "stderr": True,
                "remove": True,
            }
        )
        out: bytes = client.containers.run(  # type: ignore
            image,
            **kwargs,
        )
        return out.decode()
    except ContainerError as e:
        logger.debug('Failed to run command "%s" in image "%s"', command, image)
        logger.debug(e)
    return None


def _make_mount_dict(mount: dict[Path | str, Path | str]) -> dict[str, dict[str, str]]:
    return {
        str(Path(src).absolute()): {
            "bind": str(Path(dst).absolute()),
            "mode": "rw",
        }
        for src, dst in mount.items()
    }


class DockerStreamResult:
    def __init__(self) -> None:
        self.stream: Generator[bytes, None, None] | None = None
        self.return_code: int | None = None


@contextmanager
def run_command_stream(
    image: str,
    command: str | None,
    workdir: str | None = None,
    mount: dict[Path | str, Path | str] | None = None,
) -> Generator[DockerStreamResult, None, None]:
    logger.debug("Running commands stream")
    logger.debug("  image: %s", image)
    logger.debug("  command: %s", command)
    logger.debug("  workdir: %s", workdir)
    logger.debug("  mount: %s", mount)
    client = get_docker_client()

    result = DockerStreamResult()
    if not image_exists(image):
        logger.debug('Image "%s" does not exist', image)
        yield result
    else:
        try:
            kwargs: dict[str, Any] = {}
            if command is not None:
                kwargs["command"] = f'/bin/bash -c "{command}"'
            if workdir is not None:
                kwargs["working_dir"] = workdir
            if mount is not None:
                kwargs["volumes"] = _make_mount_dict(mount)
            kwargs.update(
                {
                    "stdout": True,
                    "stderr": True,
                    "remove": False,
                    "detach": True,
                }
            )
            container: Container = client.containers.run(image, **kwargs)  # type: ignore

            result.stream = cast(
                Generator[bytes, None, None],
                container.logs(stream=True),  # type: ignore
            )
            yield result
            container.stop()  # type: ignore
            container_status = cast(dict[str, Any], container.wait())  # type: ignore
            result.return_code = container_status["StatusCode"]
            container.remove()  # type: ignore
        except ContainerError as e:
            logger.debug('Failed to run command "%s" in image "%s"', command, image)
            logger.debug(e)
    return None


@contextmanager
def run_commands_stream(
    image: str,
    commands: list[str] | None,
    workdir: str | None = None,
    mount: dict[Path | str, Path | str] | None = None,
) -> Generator[DockerStreamResult, None, None]:
    command = "; ".join(commands) if commands is not None else None
    with run_command_stream(image, command, workdir, mount) as result:
        yield result
    return None
