from kaprese.core.benchmark import Benchmark
from kaprese.utils.logging import logger


def register_benchmarks(overwrite: bool = False) -> None:
    formulas = [
        Benchmark(
            f"formula-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:formula-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    diffs = [
        Benchmark(
            f"diff-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:diff-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    lambdas = [
        Benchmark(
            f"lambda-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:lambda-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    for bench in [*formulas, *diffs, *lambdas]:
        logger.info(f"Registering ocaml benchmark {bench.name}")
        bench.register(overwrite=overwrite)

def unregister_benchmarks(delete_image: bool = False) -> None:
    formulas = [
        Benchmark(
            f"formula-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:formula-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    diffs = [
        Benchmark(
            f"diff-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:diff-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    lambdas = [
        Benchmark(
            f"lambda-{i}",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:lambda-{i}",
            language_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cat metadata.json | jq -r .language",
            workdir_command="export DEBIAN_FRONTEND=non-interactive && apt-get update >/dev/null 2>&1 && apt-get install -y --no-install-recommends jq >/dev/null 2>&1 && cd $(cat metadata.json | jq -r .buggyPath) && pwd",
        )
        for i in range(1, 101)
    ]

    for bench in [*formulas, *diffs, *lambdas]:
        logger.info(f"Unregistering ocaml benchmark {bench.name}")
        bench.unregister(delete_image=delete_image)
