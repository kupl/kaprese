from kaprese.core.benchmark import Benchmark


def register_benchmarks(overwrite: bool = False) -> None:
    flexs = [
        Benchmark(
            f"flex-{i}",
            "c",
            f"ghcr.io/kupl/starlab-benchmarks/c:c-{i}",
        )
        for i in range(1, 2)
    ]

    flints = [
        Benchmark(f"flint-{i}", "c", f"ghcr.io/kupl/starlab-benchmarks/c:flint-{i}")
        for i in range(1, 2)
    ]

    spearmints = [
        Benchmark(
            f"spearmint-{i}", "c", f"ghcr.io/kupl/starlab-benchmarks/c:spearmint-{i}"
        )
        for i in range(1, 2)
    ]

    for bench in [*flexs, *flints, *spearmints]:
        bench.register(overwrite=overwrite)
