from typing import Any


class Singleton(type):
    __instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]
