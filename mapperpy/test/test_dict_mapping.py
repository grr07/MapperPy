import unittest
from assertpy import assert_that

from mapperpy.test.common_test_classes import *

from mapperpy import ObjectMapper, ConfigurationException

__author__ = 'lgrech'


class ObjectMapperDictMappingTest(unittest.TestCase):

    def test_map_empty_to_empty_dict(self):
        assert_that(ObjectMapper.from_class(TestEmptyClass1, dict).map(TestEmptyClass1())).is_instance_of(dict)
        assert_that(ObjectMapper.from_class(TestEmptyClass1, dict).map({})).is_instance_of(TestEmptyClass1)

    def test_map_one_explicit_property(self):
        # given
        mapper = ObjectMapper.from_class(TestClassSomeProperty1, dict).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['mapped_property']).is_equal_to("some_value")

        # when
        mapped_object_rev = mapper.map(dict(mapped_property="other_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")

    def test_map_one_explicit_property_rev(self):
        # given
        mapper = ObjectMapper.from_class(dict, TestClassSomeProperty1).custom_mappings(
            {"mapped_property": "some_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['mapped_property']).is_equal_to("some_value")

        # when
        mapped_object_rev = mapper.map(dict(mapped_property="other_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")

    def test_map_multiple_explicit_properties(self):
        # given
        mapper = ObjectMapper.from_class(dict, TestClassMappedProperty).custom_mappings(
                            {"some_property": "mapped_property",
                             "some_property_02": "mapped_property_02",
                             "some_property_03": "mapped_property_03"})

        # when
        mapped_object = mapper.map(dict(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassMappedProperty)
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")
        assert_that(mapped_object.mapped_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.mapped_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

        # when
        mapped_object_rev = mapper.map(TestClassMappedProperty(
            mapped_property="other_value",
            mapped_property_02="other_value_02",
            mapped_property_03="other_value_03",
            unmapped_property2="unmapped_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(dict)
        assert_that(mapped_object_rev['some_property']).is_equal_to("other_value")
        assert_that(mapped_object_rev['some_property_02']).is_equal_to("other_value_02")
        assert_that(mapped_object_rev['some_property_03']).is_equal_to("other_value_03")
        assert_that(mapped_object_rev).does_not_contain_key('unmapped_property1')

    def test_map_implicit_with_prototype_obj(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomeProperty1(None), TestClassSomeProperty2(None).__dict__)

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02=None,
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['some_property']).is_equal_to("some_value")
        assert_that(mapped_object['some_property_02']).is_none()
        assert_that(mapped_object['some_property_03']).is_equal_to("some_value_03")
        assert_that(mapped_object).does_not_contain_key('unmapped_property2')

        # when
        mapped_object_rev = mapper.map(dict(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property2="unmapped_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("some_value")
        assert_that(mapped_object_rev.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object_rev.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object_rev.unmapped_property1).is_none()

    def test_map_to_dict_with_nested_mapper(self):
        # given
        root_mapper = ObjectMapper.from_prototype(TestClassSomeProperty1(None), TestClassSomeProperty2(None).__dict__)
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(), TestClassSomePropertyEmptyInit2().__dict__))

        # when
        mapped_object = root_mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02=TestClassSomePropertyEmptyInit1(
                some_property="nested_value",
                some_property_02="nested_value_02",
                some_property_03="nested_value_03",
                unmapped_property1="unmapped_nested_value"),
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['some_property']).is_equal_to("some_value")
        assert_that(mapped_object['some_property_03']).is_equal_to("some_value_03")
        assert_that(mapped_object).does_not_contain_key('unmapped_property2')

        assert_that(mapped_object).contains_key('some_property_02')
        nested_mapped_obj = mapped_object['some_property_02']
        assert_that(nested_mapped_obj).is_instance_of(dict)
        assert_that(nested_mapped_obj['some_property']).is_equal_to("nested_value")
        assert_that(nested_mapped_obj['some_property_02']).is_equal_to("nested_value_02")
        assert_that(nested_mapped_obj['some_property_03']).is_equal_to("nested_value_03")
        assert_that(nested_mapped_obj).does_not_contain_key('unmapped_property2')

    def test_map_from_dict_with_nested_mapper(self):
        # given
        root_mapper = ObjectMapper.from_prototype(TestClassSomeProperty1(None).__dict__, TestClassSomeProperty2(None))
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomePropertyEmptyInit2()))

        # when
        mapped_object = root_mapper.map(dict(
            some_property="some_value",
            some_property_02=dict(
                some_property="nested_value",
                some_property_02="nested_value_02",
                some_property_03="nested_value_03",
                unmapped_property1="unmapped_nested_value"),
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

        nested_mapped_obj = mapped_object.some_property_02
        assert_that(nested_mapped_obj).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(nested_mapped_obj.some_property).is_equal_to("nested_value")
        assert_that(nested_mapped_obj.some_property_02).is_equal_to("nested_value_02")
        assert_that(nested_mapped_obj.some_property_03).is_equal_to("nested_value_03")
        assert_that(nested_mapped_obj.unmapped_property2).is_none()

    def test_implicit_mapping_when_dict_does_not_contain_property_from_prototype(self):
        # given
        mapper = ObjectMapper.from_prototype(TestClassSomeProperty1(None).__dict__, TestClassSomeProperty2(None))

        # when
        mapped_object_rev = mapper.map(dict(some_property="some_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object_rev.some_property).is_equal_to("some_value")
        assert_that(mapped_object_rev.some_property_02).is_none()
        assert_that(mapped_object_rev.some_property_03).is_none()
        assert_that(mapped_object_rev.unmapped_property2).is_none()

        # when
        mapped_object = mapper.map(TestClassSomeProperty2(
            some_property="some_value",
            some_property_02=None,
            some_property_03="some_value_03",
            unmapped_property2="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['some_property']).is_equal_to("some_value")
        assert_that(mapped_object['some_property_02']).is_none()
        assert_that(mapped_object['some_property_03']).is_equal_to("some_value_03")
        assert_that(mapped_object).does_not_contain_key('unmapped_property1')

    def test_map_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = ObjectMapper.from_prototype(TestClassSomeProperty1(None).__dict__, TestClassSomeProperty2(None))
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomePropertyEmptyInit2()))
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomeProperty2(None)))

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(dict(some_property=TestClassSomePropertyEmptyInit1().__dict__))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("dict")

    def test_map_explicit_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = ObjectMapper.from_class(dict, TestClassMappedProperty).\
            custom_mappings({"some_property": "mapped_property"})

        root_mapper.nested_mapper(ObjectMapper.from_class(dict, TestClassSomePropertyEmptyInit2))
        root_mapper.nested_mapper(ObjectMapper.from_class(dict, TestClassSomeProperty2))

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(dict(some_property=dict()))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("mapped_property")
        assert_that(context.exception.args[0]).contains("dict")

    def test_map_with_multiple_nested_mappings_when_no_matching_mapper_for_target_type_should_raise_exception(self):
        # given
        root_mapper = ObjectMapper.from_prototype(
            TestClassSomeProperty1(None).__dict__,
            TestClassSomeProperty2(some_property=TestClassMappedPropertyEmptyInit()))

        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomeProperty2(None)))
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomePropertyEmptyInit2()))

        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(dict(some_property=dict(some_property_02="nested_value_02")))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("dict")
        assert_that(context.exception.args[0]).contains("TestClassMappedPropertyEmptyInit")

    def test_map_with_multiple_nested_mappings_for_one_attribute_when_target_type_known(self):
        # given
        root_mapper = ObjectMapper.from_prototype(
            TestClassSomeProperty1(None).__dict__,
            TestClassSomeProperty2(some_property=TestClassSomePropertyEmptyInit2()))

        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomeProperty2(None)))
        root_mapper.nested_mapper(
            ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1().__dict__, TestClassSomePropertyEmptyInit2()))

        # when
        mapped_object = root_mapper.map(dict(some_property=dict(some_property_02="nested_value_02")))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)

        nested_mapped_obj = mapped_object.some_property
        assert_that(nested_mapped_obj).is_not_none()
        assert_that(nested_mapped_obj).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(nested_mapped_obj.some_property_02).is_equal_to("nested_value_02")

    def test_for_dict(self):
        # given
        mapper = ObjectMapper.for_dict(TestClassSomeProperty1(None))

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['some_property']).is_equal_to("some_value")
        assert_that(mapped_object['some_property_02']).is_equal_to("some_value_02")
        assert_that(mapped_object['some_property_03']).is_equal_to("some_value_03")

        # when
        mapped_object_rev = mapper.map(dict(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("some_value")
        assert_that(mapped_object_rev.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object_rev.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object_rev.unmapped_property1).is_none()
