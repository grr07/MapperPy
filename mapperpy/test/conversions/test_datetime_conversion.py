import unittest
from datetime import datetime

from assertpy import assert_that

from mapperpy.test.common_test_classes import *
from mapperpy import OneWayMapper, ObjectMapper

__author__ = 'lgrech'


class DateTimeConversionTest(unittest.TestCase):
    def test_map_from_datetime_it_target_type_not_known(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)
        test_datetime = datetime.now()

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02=test_datetime))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to(test_datetime)

    def test_map_from_datetime_to_string(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property_02="string"))
        test_datetime = datetime.now()

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02=test_datetime))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to(test_datetime.isoformat())

    def test_map_from_string_to_datetime_wrong_format_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property_02=datetime.now()))

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map(TestClassSomePropertyEmptyInit1(some_property_02="wrong_date_format"))

        # then
        assert_that(context.exception.message).contains("wrong_date_format")

    def test_map_from_string_to_datetime(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property_02=datetime.now()))
        test_datetime = datetime.now()

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02=test_datetime.isoformat()))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_instance_of(datetime)
        assert_that(mapped_object.some_property_02).is_equal_to(test_datetime)

    def test_map_both_ways(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(some_property_02="str"),
                                             TestClassSomePropertyEmptyInit2(some_property_02=datetime.now()))
        test_datetime = datetime.now()

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02=test_datetime.isoformat()))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_instance_of(datetime)
        assert_that(mapped_object.some_property_02).is_equal_to(test_datetime)

        # when
        mapped_object_rev = mapper.map(TestClassSomePropertyEmptyInit2(
            some_property="some_value",
            some_property_02=test_datetime))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomePropertyEmptyInit1)
        assert_that(mapped_object_rev.some_property).is_equal_to("some_value")
        assert_that(mapped_object_rev.some_property_02).is_instance_of(str)
        assert_that(mapped_object_rev.some_property_02).is_equal_to(test_datetime.isoformat())

    def test_map_from_unicode_string(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(),
                                             TestClassSomePropertyEmptyInit2(some_property_02=datetime.now()))
        test_datetime = datetime.now()

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02=unicode(test_datetime.isoformat())))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_instance_of(datetime)
        assert_that(mapped_object.some_property_02).is_equal_to(test_datetime)

    def test_map_string_without_millis_to_datetime(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property=datetime.now()))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="2015-11-02T18:14:42"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_instance_of(datetime)
        assert_that(mapped_object.some_property).is_equal_to(datetime(2015, 11, 2, 18, 14, 42, 0))

    def test_map_string_with_millis_to_datetime(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property=datetime.now()))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="2015-11-02T18:14:42.000123"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_instance_of(datetime)
        assert_that(mapped_object.some_property).is_equal_to(datetime(2015, 11, 2, 18, 14, 42, 123))

    def test_map_millisecond_timestamp_to_datetime(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property=datetime.now()))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property=1446749497576))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_instance_of(datetime)
        assert_that(mapped_object.some_property).is_equal_to(datetime(2015, 11, 5, 10, 51, 37, 576000))

    def test_map_datetime_to_millisecond_timestamp(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property=7133571))

        # when
        mapped_object = mapper.map(
            TestClassSomePropertyEmptyInit1(some_property=datetime(2015, 11, 5, 10, 51, 37, 576000)))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_instance_of(int)
        assert_that(mapped_object.some_property).is_equal_to(1446749497576)
