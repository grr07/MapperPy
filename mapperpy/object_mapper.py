from enum import Enum
from mapperpy.one_way_mapper import OneWayMapper

__author__ = 'lgrech'


class MappingDirection(Enum):
    left_to_right = 1
    right_to_left = 2


class ObjectMapper(object):

    def __init__(self, from_left_mapper, from_right_mapper):
        """
        :param from_left_mapper:
        :type from_left_mapper: OneWayMapper
        :param from_right_mapper:
        :type from_right_mapper: OneWayMapper
        """
        self.__from_left_mapper = from_left_mapper
        self.__from_right_mapper = from_right_mapper

    @classmethod
    def from_class(cls, left_class, right_class):
        return ObjectMapper(
            OneWayMapper.for_target_class(right_class),
            OneWayMapper.for_target_class(left_class))

    @classmethod
    def from_prototype(cls, left_proto_obj, right_proto_obj):
        return ObjectMapper(
            OneWayMapper.for_target_prototype(right_proto_obj),
            OneWayMapper.for_target_prototype(left_proto_obj))

    @classmethod
    def for_dict(cls, left_proto_obj):
        return ObjectMapper(
            OneWayMapper.for_target_prototype(left_proto_obj.__dict__),
            OneWayMapper.for_target_prototype(left_proto_obj))

    def map(self, obj):
        if isinstance(obj, self.__from_right_mapper.target_class):
            return self.__from_left_mapper.map(obj)
        elif isinstance(obj, self.__from_left_mapper.target_class):
            return self.__from_right_mapper.map(obj)

        raise ValueError("This mapper does not support {} class".format(obj.__class__.__name__))

    def map_attr_name(self, attr_name):
        """
        :type attr_name: basestring
        :rtype: basestring
        """
        mapped_name = self.__get_mapped_name(self.__from_left_mapper, attr_name)
        if mapped_name and self.__get_mapped_name(self.__from_right_mapper, mapped_name) == attr_name:
            return mapped_name

        mapped_name = self.__get_mapped_name(self.__from_right_mapper, attr_name)
        if mapped_name and self.__get_mapped_name(self.__from_left_mapper, mapped_name) == attr_name:
            return mapped_name

        raise ValueError("Can't find mapping for attribute name: {}".format(attr_name))

    def map_attr_value(self, attr_name, attr_value, mapping_direction=None, target_class=None):
        """
        :type attr_name: basestring
        :type attr_value: object
        :type mapping_direction: MappingDirection
        :type target_class: type
        :rtype: object
        """

        if mapping_direction is not None and target_class is not None\
                or mapping_direction is None and target_class is None:
            raise ValueError("Either mapping direction or target class has to be set (not both)")

        if mapping_direction and mapping_direction == MappingDirection.left_to_right \
                or target_class and target_class == self.__from_left_mapper.target_class:
            mapped_name = self.__get_mapped_name(self.__from_left_mapper, attr_name)
            if mapped_name and self.__get_mapped_name(self.__from_right_mapper, mapped_name) == attr_name:
                return self.__from_left_mapper.map_attr_value(attr_name, attr_value)

        elif mapping_direction and mapping_direction == MappingDirection.right_to_left \
                or target_class and target_class == self.__from_right_mapper.target_class:
            mapped_name = self.__get_mapped_name(self.__from_right_mapper, attr_name)
            if mapped_name and self.__get_mapped_name(self.__from_left_mapper, mapped_name) == attr_name:
                return self.__from_right_mapper.map_attr_value(attr_name, attr_value)

        raise ValueError(
            "Can't find mapping for attribute name: {}, direction: {}, target class: {}".format(
                attr_name, mapping_direction, target_class.__name__ if target_class else None))

    def custom_mappings(self, mapping_dict):

        mapping, rev_mapping = self.__get_explicit_mapping(mapping_dict)

        self.__from_left_mapper.custom_mappings(mapping)
        self.__from_right_mapper.custom_mappings(rev_mapping)
        return self

    def nested_mapper(self, mapper):

        if not isinstance(mapper, ObjectMapper):
            raise ValueError("Nested mapper has to be an instance of {}, {} found".format(
                ObjectMapper.__name__, mapper.__class__.__name__))

        left_type = mapper.__from_right_mapper.target_class
        self.__from_left_mapper.nested_mapper(mapper.__from_left_mapper, left_type)

        right_type = mapper.__from_left_mapper.target_class
        self.__from_right_mapper.nested_mapper(mapper.__from_right_mapper, right_type)

        return self

    def left_initializers(self, initializers_dict):
        self.__from_right_mapper.target_initializers(initializers_dict)
        return self

    def right_initializers(self, initializers_dict):
        self.__from_left_mapper.target_initializers(initializers_dict)
        return self

    def value_converters(self, converters_dict):
        to_right_converters, to_left_converters = self.__split_converters(converters_dict)

        self.__from_left_mapper.target_value_converters(to_right_converters)
        self.__from_right_mapper.target_value_converters(to_left_converters)

        return self

    def options(self, option):
        self.__from_left_mapper.options(option)
        self.__from_right_mapper.options(option)
        return self

    def __repr__(self):
        return "{}->{}".format(self.__from_right_mapper.target_class, self.__from_left_mapper.target_class)

    @classmethod
    def __get_mapped_name(cls, one_way_mapper, attr_name):
        try:
            return one_way_mapper.map_attr_name(attr_name)
        except ValueError:
            return None

    @classmethod
    def __get_explicit_mapping(cls, input_mapping):

        mapping = {}
        rev_mapping = {}

        for left, right in list(input_mapping.items()):
            if right is None:
                # user requested to suppress implicit mapping for k
                mapping[left] = rev_mapping[left] = None
            else:
                mapping[left] = right
                rev_mapping[right] = left

        return mapping, rev_mapping

    def __split_converters(self, converters_dict):
        to_right_converters = {}
        to_left_converters = {}

        for left_attr_name, converters_tuple in converters_dict.items():
            if not isinstance(converters_tuple, tuple) or len(converters_tuple) != 2:
                raise ValueError("Converters for {} should be provided in a 2-element tuple".format(left_attr_name))

            to_right_converters[left_attr_name] = converters_tuple[0]
            to_left_converters[self.__from_left_mapper.map_attr_name(left_attr_name)] = converters_tuple[1]

        return to_right_converters, to_left_converters
