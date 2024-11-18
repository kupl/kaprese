from kaprese.core.benchmark import Benchmark
from kaprese.utils.logging import logger


def register_benchmarks(overwrite: bool = False) -> None:
    flexs = [
        Benchmark(
            f"flex-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:flex-{i}",
            language_command="cat metadata.json | jq -r .language",
            workdir_command="cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 7)
    ]

    flints = [
        Benchmark(
            f"flint-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:flint-{i}",
            language_command="cat metadata.json | jq -r .language",
            workdir_command="cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 2)
    ]

    spearmints = [
        Benchmark(
            f"spearmint-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:spearmint-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 2)
    ]

    for bench in [*flexs, *flints, *spearmints]:
        logger.info(f"Registering c benchmark {bench.name}")
        bench.register(overwrite=overwrite)

def unregister_benchmarks(delete_image: bool = False) -> None:
    flexs = [
        Benchmark(
            f"flex-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:flex-{i}",
            language_command="cat metadata.json | jq -r .language",
            workdir_command="cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 7)
    ]

    flints = [
        Benchmark(
            f"flint-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:flint-{i}",
            language_command="cat metadata.json | jq -r .language",
            workdir_command="cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 2)
    ]

    spearmints = [
        Benchmark(
            f"spearmint-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/c:spearmint-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 2)
    ]

    for bench in [*flexs, *flints, *spearmints]:
        logger.info(f"Unregistering c benchmark {bench.name}")
        bench.unregister(delete_image=delete_image)