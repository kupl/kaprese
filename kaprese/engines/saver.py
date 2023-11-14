from kaprese.core.engine import Engine


def register_saver(overwrite: bool = False) -> None:
    saver = Engine(
        "saver",
        supported_languages=["c"],
        supported_os=["ubuntu:20.04"],
    )
    saver.register(overwrite=overwrite)
