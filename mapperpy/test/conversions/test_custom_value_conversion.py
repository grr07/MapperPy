import unittest
from assertpy import assert_that

from mapperpy.test.common_test_classes import *

from mapperpy import OneWayMapper, ObjectMapper


class CustomValueConversionTest(unittest.TestCase):
    def test_target_value_converters_when_converter_not_function_should_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).target_value_converters(
                {"some_property_02": 7}
            )
        assert_that(context.exception.args[0]).contains("some_property_02")

    def test_map_for_single_converter(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).target_value_converters(
            {"some_property_02": lambda val: 7}
        )

        # when
        mapped_object = mapper.map({"some_property_02": "val"})

        # then
        assert_that(mapped_object.some_property_02).is_equal_to(7)

    def test_map_should_not_convert_missing_source_value(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).target_value_converters(
            {"some_property_02": lambda val: 7,
             "some_property_03": lambda val: "some_other_value"}
        )

        # when
        mapped_object = mapper.map({"some_property_02": "val"})

        # then
        assert_that(mapped_object.some_property_02).is_equal_to(7)
        assert_that(mapped_object.some_property_03).is_none()

    def test_map_for_multiple_converters(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).target_value_converters(
            {"some_property_02": lambda val: 7,
             "some_property_03": lambda val: "some_other_value"}
        )

        # when
        mapped_object = mapper.map({"some_property_02": "val", "some_property_03": "some_value"})

        # then
        assert_that(mapped_object.some_property_02).is_equal_to(7)
        assert_that(mapped_object.some_property_03).is_equal_to("some_other_value")

    def test_map_attr_value(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).target_value_converters(
            {"some_property_02": lambda val: 7,
             "some_property_03": lambda val: "some_other_value"}
        )

        # when
        assert_that(mapper.map_attr_value("some_property_02", "val")).is_equal_to(7)
        assert_that(mapper.map_attr_value("some_property_03", "some_value")).is_equal_to("some_other_value")

    def test_object_mapper_value_converters_when_converters_not_in_tuple_should_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            ObjectMapper.from_class(TestClassSomePropertyEmptyInit1, TestClassSomePropertyEmptyInit2).value_converters(
                {"some_property_02": lambda val: 7})

        assert_that(context.exception.args[0]).contains("some_property_02")

    def test_object_mapper_value_converters_when_converter_not_in_2_element_tuple_should_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            ObjectMapper.from_class(TestClassSomePropertyEmptyInit1, TestClassSomePropertyEmptyInit2).value_converters(
                {"some_property_02": (lambda val: 7,)})

        assert_that(context.exception.args[0]).contains("some_property_02")

    def test_object_mapper_value_converters_when_converter_not_callable_should_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            ObjectMapper.from_class(TestClassSomePropertyEmptyInit1, TestClassSomePropertyEmptyInit2).value_converters(
                {"some_property_02": (lambda val: 7, "not_a_function")})

        assert_that(context.exception.args[0]).contains("some_property_02")

    def test_object_mapper_map_with_value_converter_and_default_mapping(self):
        # given
        mapper = ObjectMapper.from_class(
            TestClassSomePropertyEmptyInit1, TestClassSomePropertyEmptyInit2).value_converters(
                {"some_property_02": (lambda val: 7, lambda val: 9)})

        # then
        assert_that(mapper.map(TestClassSomePropertyEmptyInit1(some_property_02="some_val")).some_property_02).\
            is_equal_to(7)

        assert_that(mapper.map(TestClassSomePropertyEmptyInit2(some_property_02="some_other_val")).some_property_02). \
            is_equal_to(9)

    def test_object_mapper_map_with_value_converter_and_custom_mapping(self):
        # given
        mapper = ObjectMapper.from_class(
            TestClassSomePropertyEmptyInit1, TestClassMappedPropertyEmptyInit).custom_mappings(
            {"some_property_02": "mapped_property_02"}
        ).value_converters(
            {"some_property_02": (lambda val: 7, lambda val: 9)})

        # then
        assert_that(mapper.map(TestClassSomePropertyEmptyInit1(
            some_property_02="some_val")).mapped_property_02).is_equal_to(7)

        assert_that(mapper.map(TestClassMappedPropertyEmptyInit(
            mapped_property_02="some_other_val")).some_property_02).is_equal_to(9)

    def test_object_mapper_map_attr_value(self):
        # given
        mapper = ObjectMapper.from_class(
            TestClassSomePropertyEmptyInit1, TestClassMappedPropertyEmptyInit).custom_mappings(
            {"some_property_02": "mapped_property_02"}
        ).value_converters(
            {"some_property_02": (lambda val: 7, lambda val: 9)})

        # when
        assert_that(mapper.map_attr_value(
            "some_property_02", "val", target_class=TestClassMappedPropertyEmptyInit)).is_equal_to(7)
        assert_that(mapper.map_attr_value(
            "mapped_property_02", "some_value", target_class=TestClassSomePropertyEmptyInit1)).is_equal_to(9)
