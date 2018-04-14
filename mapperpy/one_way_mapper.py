import collections
from datetime import datetime
from enum import Enum

from mapperpy.attributes_util import AttributesCache, get_attributes
from mapperpy.mapper_options import MapperOptions
from mapperpy.exceptions import ConfigurationException

__author__ = 'lgrech'


try:
      basestring
except NameError:
      basestring = str


class OneWayMapper(object):

    def __init__(self, target_class, target_prototype_obj=None, attributes_cache_provider=AttributesCache):
        self.__target_class = target_class
        self.__target_prototype_obj = \
            target_prototype_obj if target_prototype_obj is not None else self.__try_create_prototype(target_class)
        self.__discovered_target_class_attrs = None

        self.__source_attributes_cache = attributes_cache_provider()

        self.__explicit_mapping = {}
        self.__nested_mappers = {}
        self.__target_initializers = {}
        self.__target_value_converters = {}
        self.__general_settings = {}

    @classmethod
    def for_target_class(cls, target_class):
        if not isinstance(target_class, type):
            raise ValueError("Class expected, instead got instance of {}".format(target_class.__class__.__name__))

        return OneWayMapper(target_class)

    @classmethod
    def for_target_prototype(cls, proto_obj):
        if isinstance(proto_obj, type):
            raise ValueError("Object instance expected, instead got class {}".format(proto_obj.__name__))

        return OneWayMapper(proto_obj.__class__, proto_obj)

    def map(self, obj):
        param_dict = self.__get_mapped_params_dict(obj)
        return self.__try_create_target_object(param_dict)

    def map_attr_name(self, attr_name):

        if attr_name in self.__explicit_mapping:
            return self.__explicit_mapping[attr_name]

        if attr_name in self.__get_discovered_target_class_attributes():
            return attr_name

        raise ValueError("Can't find mapping for attribute name: {}".format(attr_name))

    def map_attr_value(self, attr_name, attr_value):
        mapped_attr_name = self.map_attr_name(attr_name)
        return self.__do_apply_mapping(attr_name, mapped_attr_name, attr_value)

    def custom_mappings(self, mapping_dict):
        self.__explicit_mapping.update(mapping_dict)
        return self

    def nested_mapper(self, mapper, for_type):

        if not isinstance(mapper, OneWayMapper):
            raise ValueError("Nested mapper has to be an instance of {}, {} found".format(
                OneWayMapper.__name__, mapper.__class__.__name__))

        if for_type not in self.__nested_mappers:
            self.__nested_mappers[for_type] = set()

        if mapper.target_class in [mpr.target_class for mpr in self.__nested_mappers[for_type]]:
            raise ConfigurationException("Nested mapping {}->{} already defined for this mapper".format(
                for_type.__name__, mapper.target_class.__name__))

        self.__nested_mappers[for_type].add(mapper)

        return self

    def target_initializers(self, initializers_dict):
        self.__verify_if_callable(initializers_dict, "Initializer for {} is not callable")
        self.__target_initializers.update(initializers_dict)
        return self

    def target_value_converters(self, converters_dict):
        self.__verify_if_callable(converters_dict, "Converter for {} is not callable")
        self.__target_value_converters.update(converters_dict)
        return self

    def options(self, settings):
        (setting_name, setting_value) = settings
        self.__general_settings[setting_name] = setting_value
        return self

    @property
    def target_class(self):
        return self.__target_class

    def __try_create_target_object(self, param_dict):
        try:
            return self.__target_class(**param_dict)
        except TypeError as er:
            raise AttributeError("Error when initializing class {} with params: {}\n{}".format(
                self.__target_class.__name__, param_dict, er.args[0]))

    def __get_mapped_params_dict(self, obj_from):

        actual_attr_name_mapping = self.__get_actual_attr_name_mapping(obj_from)

        try:
            mapped_params_dict = self.__apply_mapping(obj_from, actual_attr_name_mapping)
            mapped_params_dict.update(self.__apply_initializers(obj_from))
            return mapped_params_dict
        except AttributeError as er:
            raise AttributeError("Unknown attribute: {}".format(er.args[0]))

    def __apply_initializers(self, source_obj):
        initialized_params_dict = {}

        for attr_name, init_func in list(self.__target_initializers.items()):
            initialized_params_dict[attr_name] = init_func(source_obj)

        return initialized_params_dict

    def __apply_mapping(self, source_obj, attr_name_mapping):

        mapped_params_dict = {}

        for attr_name_from, attr_name_to in list(attr_name_mapping.items()):
            # skip since mapping is suppressed by user (attribute_name = None)
            if not (attr_name_from and attr_name_to):
                continue

            source_attr_value = self.__get_attribute_value(source_obj, attr_name_from)
            mapped_params_dict[attr_name_to] = self.__do_apply_mapping(attr_name_from, attr_name_to, source_attr_value)

        return mapped_params_dict

    def __do_apply_mapping(self, attr_name_from, attr_name_to, source_attr_value):

        target_attr_value = self.__get_target_proto_attribute_value(attr_name_to)

        from_type = self.__try_get_type(source_attr_value)
        to_type = self.__try_get_type(target_attr_value)

        if attr_name_from in self.__target_value_converters:
            return self.__target_value_converters[attr_name_from](source_attr_value)
        elif from_type in self.__nested_mappers:
            return self.__try_apply_nested_mapper(
                source_attr_value, from_type, attr_name_from, to_type, attr_name_to)
        elif from_type is not None and to_type is not None and to_type != from_type:
            return self.__apply_type_conversion(from_type, to_type, source_attr_value)
        else:
            return source_attr_value

    def __try_apply_nested_mapper(self, attr_value, from_type, attr_name_from, to_type, attr_name_to):

        error_message = "Ambiguous nested mapping for attribute {}->{}. Too many mappings defined for type {}". \
            format(attr_name_from, attr_name_to, from_type.__name__)

        if len(self.__nested_mappers[from_type]) == 1:
            return list(self.__nested_mappers[from_type])[0].map(attr_value)
        elif to_type is not None:
            applicable_mappers = [mpr for mpr in self.__nested_mappers[from_type] if mpr.target_class == to_type]
            if len(applicable_mappers) < 1:
                raise ConfigurationException("{}. None of the available mappers ({}) matches target type {}".format(
                    error_message,
                    ", ".join(["{}{}".format(from_type.__name__, mpr) for mpr in self.__nested_mappers[from_type]]),
                    to_type.__name__))
            elif len(applicable_mappers) == 1:
                return applicable_mappers[0].map(attr_value)

        raise ConfigurationException(error_message)

    @classmethod
    def __apply_type_conversion(cls, from_type, to_type, attr_value):
        if issubclass(from_type, Enum):
            return cls.__get_conversion_from_enum(attr_value, to_type)
        elif issubclass(to_type, Enum):
            return cls.__get_conversion_to_enum(attr_value, from_type, to_type)
        elif issubclass(from_type, datetime) and issubclass(to_type, str):
            return cls.__get_conversion_from_datetime(attr_value)
        elif issubclass(from_type, basestring) and issubclass(to_type, datetime):
            return cls.__get_conversion_to_datetime(attr_value)
        return attr_value

    @classmethod
    def __get_conversion_to_datetime(cls, attr_value):
        try:
            return datetime.strptime(attr_value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError as e1:
            try:
                return datetime.strptime(attr_value, "%Y-%m-%dT%H:%M:%S")
            except ValueError as e2:
                raise ValueError("Could not create datetime object from string: {}. {}. {}".format(
                    attr_value, e1.args[0], e2.args[0]))

    @classmethod
    def __get_conversion_from_datetime(cls, attr_value):
        return attr_value.isoformat()

    @classmethod
    def __get_conversion_to_enum(cls, attr_value, from_type, to_enum_type):
        if from_type == int:
            return to_enum_type(attr_value)
        elif issubclass(from_type, basestring):
            # this tries to get enum item from Enum class
            return getattr(to_enum_type, attr_value)
        return attr_value

    @classmethod
    def __get_conversion_from_enum(cls, attr_value, to_type):
        if to_type == int:
            return attr_value.value
        elif issubclass(to_type, basestring):
            return attr_value.name
        return attr_value

    def __get_target_proto_attribute_value(self, attr_name):
        return self.__get_attribute_value(self.__target_prototype_obj, attr_name) \
            if self.__target_prototype_obj else None

    def __get_attribute_value(self, obj, attr_name):
        try:
            attr_value = obj[attr_name] if isinstance(obj, dict) else getattr(obj, attr_name)
        except Exception as ex:
            if self.__get_setting(MapperOptions.fail_on_get_attr, True):
                raise ex
            return None

        return attr_value

    @classmethod
    def __try_get_type(cls, attr_value):
        return type(attr_value) if attr_value is not None else None

    def __get_actual_attr_name_mapping(self, obj):

        common_attributes = self.__get_common_instance_attributes(obj) if self.__target_prototype_obj else []

        actual_attr_name_mapping = {common_attr: common_attr for common_attr in common_attributes}
        actual_attr_name_mapping.update(self.__explicit_mapping)

        return actual_attr_name_mapping

    @classmethod
    def __try_create_prototype(cls, to_class):
        try:
            return to_class()
        except TypeError:
            # if we can't instantiate the class then it's not possible to determine instance attributes - implicit
            # mapping won't work
            return None

    def __get_common_instance_attributes(self, from_obj):
        source_class_attrs = self.__source_attributes_cache.get_attrs_update_cache(from_obj)
        return source_class_attrs.intersection(self.__get_discovered_target_class_attributes())

    def __get_discovered_target_class_attributes(self):
        if self.__discovered_target_class_attrs is None:
            self.__discovered_target_class_attrs = \
                set(get_attributes(self.__target_prototype_obj)) if self.__target_prototype_obj else set()

        return self.__discovered_target_class_attrs

    def __get_setting(self, mapper_option, default_val):
        if mapper_option.get_name() in self.__general_settings:
            return self.__general_settings[mapper_option.get_name()]

        return default_val

    @staticmethod
    def __verify_if_callable(name_callable_map, error_message_template):
        for name, obj in name_callable_map.items():
            if not isinstance(obj, collections.Callable):
                raise ValueError(error_message_template.format(name))

    def __repr__(self):
        return "->{}".format(self.__target_class.__name__)
