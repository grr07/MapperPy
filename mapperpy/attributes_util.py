import inspect


def get_attributes(obj):

    if isinstance(obj, dict):
        return list(obj.keys())

    attributes = inspect.getmembers(obj, lambda a: not(inspect.isroutine(a)))
    return [attr[0] for attr in attributes if not(attr[0].startswith('__') and attr[0].endswith('__'))]


class AttributesCache(object):

    def __init__(self, get_attributes_func=get_attributes):
        self.__cached_class = None
        self.__cached_class_attrs = None
        self.__get_attributes_func = get_attributes_func

    def get_attrs_update_cache(self, obj):
        if isinstance(obj, dict):
            return set(obj.keys())
        elif self.__cached_class_attrs is not None and isinstance(obj, self.__cached_class):
            return self.__cached_class_attrs
        else:
            self.__update_source_class_cache(obj)
            return self.__cached_class_attrs

    def __update_source_class_cache(self, obj):
        self.__cached_class = type(obj)
        self.__cached_class_attrs = set(self.__get_attributes_func(obj))
