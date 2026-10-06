from typing import Any, Dict, TypeVar, cast, Tuple, Callable
ServiceType = TypeVar('ServiceType')


def service(cls: type[ServiceType]) -> type[ServiceType]:
    instances: Dict[type[ServiceType], ServiceType] = {}

    def get_instance(*args: Any, **kwargs: Any) -> ServiceType:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return cast(type[ServiceType], get_instance)


def secure(exeptions: type[BaseException] | Tuple[type[BaseException], ...],
           errored: bool = True) -> Callable[..., Any]:
    '''Execute a function with expetions,
    if an exeption is raised, None is returned.'''
    def deco_func(func: Callable[..., Any]) -> Callable[..., Any]:
        def execute(*args: Any, **kwargs: Any) -> Any | None:
            try:
                return func(*args, **kwargs)
            except exeptions as error:
                tolist = [f"{v}" for v in list(args) + list(kwargs.values())]
                dkwargs = ", ".join(tolist)
                fname = f'"{func.__name__}({dkwargs})"'
                if not errored:
                    print("\033[38;2;255;255;0mWarning raise by"
                          f" {fname}: {error}\033[0m")
                else:
                    print("\033[38;2;255;0;0m /!\\ Error Raised by"
                          f" {fname}: \n\t \"{error}\"\033[0m")
                return None
        return execute
    return deco_func
