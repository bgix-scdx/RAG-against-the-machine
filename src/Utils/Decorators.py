from typing import Any, Dict, TypeVar, cast
ServiceType = TypeVar('ServiceType')


def service(cls: type[ServiceType]) -> type[ServiceType]:
    instances: Dict[type[ServiceType], ServiceType] = {}

    def get_instance(*args: Any, **kwargs: Any) -> ServiceType:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return cast(type[ServiceType], get_instance)
