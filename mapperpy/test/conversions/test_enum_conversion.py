import sys
import unittest
from assertpy import assert_that
from enum import Enum

from mapperpy.test.common_test_classes import *

from mapperpy import ObjectMapper, OneWayMapper

__author__ = 'lgrech'


if sys.version_info > (3, 0):
    unicode = str


class EnumConversionTest(unittest.TestCase):

    def test_enum_to_int_mapping_should_map_to_enum_value(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=1))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=SomeEnum.some_enum_02))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_type_of(int)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_02.value)

    def test_enum_to_unknown_mapping_should_map_to_enum(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(), TestClassSomePropertyEmptyInit2())

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=SomeEnum.some_enum_02))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        self.assertTrue(type(mapped_object.some_property) == SomeEnum)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_02)

    def test_enum_to_string_mapping_should_map_to_enum_name(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=''))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=SomeEnum.some_enum_02))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_type_of(str)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_02.name)

    def test_int_to_enum_mapping_should_map_to_enum(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=SomeEnum.some_enum_02))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=1))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        self.assertTrue(type(mapped_object.some_property) == SomeEnum)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_01)

    def test_int_to_unknown_mapping_should_map_to_int(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(), TestClassSomePropertyEmptyInit2())

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=1))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_type_of(int)
        assert_that(mapped_object.some_property).is_equal_to(1)

    def test_string_to_enum_mapping_should_map_to_enum(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=SomeEnum.some_enum_02))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property='some_enum_01'))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        self.assertTrue(type(mapped_object.some_property) == SomeEnum)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_01)

    def test_other_to_enum_mapping_should_use_default_mapping(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=SomeEnum.some_enum_02))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=TestEmptyClass1()))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_type_of(TestEmptyClass1)

    def test_enum_to_int_explicit_mapping_should_map_to_enum_value(self):
        # given
        mapper = ObjectMapper.\
            from_prototype(TestClassSomePropertyEmptyInit1(), TestClassMappedPropertyEmptyInit(mapped_property=1)). \
            custom_mappings({'some_property': 'mapped_property'})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=SomeEnum.some_enum_02))

        # then
        assert_that(mapped_object).is_type_of(TestClassMappedPropertyEmptyInit)
        assert_that(mapped_object.mapped_property).is_type_of(int)
        assert_that(mapped_object.mapped_property).is_equal_to(SomeEnum.some_enum_02.value)

    def test_int_to_enum_explicit_mapping_should_map_to_enum(self):
        # given
        mapper = ObjectMapper.\
            from_prototype(TestClassSomePropertyEmptyInit1(),
                           TestClassMappedPropertyEmptyInit(mapped_property=SomeEnum.some_enum_02)). \
            custom_mappings({'some_property': 'mapped_property'})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=1))

        # then
        assert_that(mapped_object).is_type_of(TestClassMappedPropertyEmptyInit)
        self.assertTrue(type(mapped_object.mapped_property) == SomeEnum)
        assert_that(mapped_object.mapped_property).is_equal_to(SomeEnum.some_enum_01)

    def test_int_to_enum_explicit_dict_mapping_should_map_to_enum(self):
        # given
        mapper = ObjectMapper.\
            from_prototype(dict(),
                           TestClassMappedPropertyEmptyInit(mapped_property=SomeEnum.some_enum_02)). \
            custom_mappings({'some_property': 'mapped_property'})

        # when
        mapped_object = mapper.map({'some_property': 1})

        # then
        assert_that(mapped_object).is_type_of(TestClassMappedPropertyEmptyInit)
        self.assertTrue(type(mapped_object.mapped_property) == SomeEnum)
        assert_that(mapped_object.mapped_property).is_equal_to(SomeEnum.some_enum_01)

    def test_map_unicode_string_to_enum(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=SomeEnum.some_enum_02))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=unicode('some_enum_01')))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        self.assertTrue(type(mapped_object.some_property) == SomeEnum)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_01)

    def test_enum_to_unicode_string_mapping_should_map_to_enum_name(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property=unicode('')))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=SomeEnum.some_enum_02))

        # then
        assert_that(mapped_object).is_type_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_type_of(str)
        assert_that(mapped_object.some_property).is_equal_to(SomeEnum.some_enum_02.name)

    def test_map_attr_value_with_string_to_enum_conversion(self):
        # given
        mapper = OneWayMapper.for_target_prototype(
            TestClassSomePropertyEmptyInit1(some_property_02=SomeEnum.some_enum_02))

        # then
        assert_that(mapper.map_attr_value("some_property_02", "some_enum_01")).is_equal_to(SomeEnum.some_enum_01)

    def test_map_attr_value_with_enum_to_string_conversion(self):
        # given
        mapper = OneWayMapper.for_target_prototype(
            TestClassSomePropertyEmptyInit1(some_property_02=""))

        # then
        assert_that(mapper.map_attr_value("some_property_02", SomeEnum.some_enum_01)).is_equal_to("some_enum_01")

    def test_map_attr_value_with_int_to_enum_conversion(self):
        # given
        mapper = OneWayMapper.for_target_prototype(
            TestClassSomePropertyEmptyInit1(some_property_02=SomeEnum.some_enum_02))

        # then
        assert_that(mapper.map_attr_value("some_property_02", 1)).is_equal_to(SomeEnum.some_enum_01)

    def test_map_attr_value_with_enum_to_int_conversion(self):
        # given
        mapper = OneWayMapper.for_target_prototype(
            TestClassSomePropertyEmptyInit1(some_property_02=7))

        # then
        assert_that(mapper.map_attr_value("some_property_02", SomeEnum.some_enum_01)).is_equal_to(1)


class SomeEnum(Enum):
    some_enum_01 = 1
    some_enum_02 = 2
