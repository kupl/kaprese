from kaprese.core.engine import Engine


def register_saver(overwrite: bool = False) -> None:
    saver = Engine(
        "saver",
        supported_languages=["c"],
        supported_os=["ubuntu:20.04"],
        image="ghcr.io/kupl/kaprese-engines/saver",
        location="https://github.com/kupl/kaprese-engines.git#main:context/saver/starlab-benchmarks",
    )
    saver.register(overwrite=overwrite)