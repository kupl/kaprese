from kaprese.core.benchmark import Benchmark


def register_benchmarks(overwrite: bool = False) -> None:
    formulas = [
        Benchmark(
            f"formula-{i}",
            "ocaml",
            f"ghcr.io/kupl/starlab-benchmarks/ocaml:formula-{i}",
        )
        for i in range(1, 101)
    ]

    diffs = [
        Benchmark(
            f"diff-{i}", "ocaml", f"ghcr.io/kupl/starlab-benchmarks/ocaml:diff-{i}"
        )
        for i in range(1, 101)
    ]

    lambdas = [
        Benchmark(
            f"lambda-{i}", "ocaml", f"ghcr.io/kupl/starlab-benchmarks/ocaml:lambda-{i}"
        )
        for i in range(1, 101)
    ]

    for bench in [*formulas, *diffs, *lambdas]:
        bench.register(overwrite=overwrite)
