import sys
import unittest
from assertpy import assert_that
if sys.version_info > (3, 0):
    from unittest.mock import Mock
else:
    from mock import Mock

from mapperpy.attributes_util import AttributesCache
from mapperpy.test.common_test_classes import *

from mapperpy import OneWayMapper, MapperOptions, ConfigurationException

__author__ = 'lgrech'


class OneWayMapperTest(unittest.TestCase):

    def test_map_empty_to_empty(self):
        assert_that(OneWayMapper.for_target_class(TestEmptyClass2).map(TestEmptyClass1())).\
            is_instance_of(TestEmptyClass2)

    def test_map_one_explicit_property(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassMappedProperty)
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")

    def test_map_unknown_property_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "unknown"})

        # when
        with self.assertRaises(AttributeError) as context:
            mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(context.exception.args[0]).contains("unknown")

    def test_map_multiple_explicit_properties(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
                            {"some_property": "mapped_property",
                             "some_property_02": "mapped_property_02",
                             "some_property_03": "mapped_property_03"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
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

    def test_map_multiple_properties_implicit(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_map_from_none_attribute(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2(some_property_02="3"))

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(some_property_02=None))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property_02).is_none()

    def test_map_implicit_with_prototype_obj(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_map_override_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2).custom_mappings(
                            {"some_property_02": "some_property_03",
                             "some_property_03": "some_property_02"})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_03")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_02")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_nested_mapper_when_wrong_param_type_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassSomeProperty2)

        # when
        with self.assertRaises(ValueError) as context:
            root_mapper.nested_mapper(object(), TestClassSomeProperty1)

        # then
        assert_that(context.exception.args[0]).contains(OneWayMapper.__name__)
        assert_that(context.exception.args[0]).contains("object")

    def test_nested_mapper_when_the_same_mapper_added_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassSomeProperty2)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2),
            TestClassSomePropertyEmptyInit1)

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.nested_mapper(
                OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2),
                TestClassSomePropertyEmptyInit1)

        # then
        assert_that(context.exception.args[0]).contains(TestClassSomePropertyEmptyInit1.__name__)
        assert_that(context.exception.args[0]).contains(TestClassSomePropertyEmptyInit2.__name__)

    def test_map_with_nested_explicit_mapper(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2), TestClassSomePropertyEmptyInit1)

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

    def test_map_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2()), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomeProperty2(None)), TestClassSomePropertyEmptyInit1)

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1()))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("TestClassSomePropertyEmptyInit1")

    def test_map_explicit_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassMappedProperty).\
            custom_mappings({"some_property": "mapped_property"})
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomeProperty2), TestClassSomePropertyEmptyInit1)

        with self.assertRaises(ConfigurationException) as context:
            # when
            root_mapper.map(TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1()))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("mapped_property")
        assert_that(context.exception.args[0]).contains("TestClassSomePropertyEmptyInit1")

    def test_map_with_multiple_nested_mappings_when_no_matching_mapper_for_target_type_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(
            TestClassSomeProperty2(some_property=TestClassMappedPropertyEmptyInit()))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomeProperty2(None)), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2()), TestClassSomePropertyEmptyInit1)

        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(TestClassSomeProperty1(
                some_property=TestClassSomePropertyEmptyInit1(some_property_02="nested_value_02")))

        # then
        assert_that(context.exception.args[0]).contains("some_property")
        assert_that(context.exception.args[0]).contains("TestClassSomePropertyEmptyInit1")
        assert_that(context.exception.args[0]).contains("TestClassMappedPropertyEmptyInit")

    def test_map_with_multiple_nested_mappings_for_one_attribute_when_target_type_known(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(
            TestClassSomeProperty2(some_property=TestClassSomePropertyEmptyInit2()))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomeProperty2(None)), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype( TestClassSomePropertyEmptyInit2()), TestClassSomePropertyEmptyInit1)

        # when
        mapped_object = root_mapper.map(
            TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1(some_property_02="nested_value_02")))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)

        nested_mapped_obj = mapped_object.some_property
        assert_that(nested_mapped_obj).is_not_none()
        assert_that(nested_mapped_obj).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(nested_mapped_obj.some_property_02).is_equal_to("nested_value_02")

    def test_map_with_reversed_nested_mapper_should_not_use_nested_mapper(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(TestClassSomePropertyEmptyInit2()))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit1()), TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = root_mapper.map(TestClassSomeProperty1(
            some_property=TestClassSomePropertyEmptyInit1(some_property="nested_value")))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_instance_of(TestClassSomePropertyEmptyInit1)
        assert_that(mapped_object.some_property.some_property).is_equal_to("nested_value")

    def test_suppress_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2).custom_mappings({"some_property": None})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value", some_property_02="some_value_02"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_none()
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")

    def test_map_with_custom_target_initializers_when_initializer_not_function_should_raise_exception(self):
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit1()).target_initializers(
                {"some_property_02": 7}
            )
        assert_that(context.exception.args[0]).contains("some_property_02")

    def test_map_with_custom_target_initializers(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedPropertyEmptyInit).target_initializers({
                "mapped_property": lambda obj: obj.some_property + obj.some_property_02,
                "unmapped_property2": lambda obj: "prefix_{}".format(obj.unmapped_property1)
            })

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value", some_property_02="some_value_02", unmapped_property1="unmapped_value"))

        assert_that(mapped_object).is_instance_of(TestClassMappedPropertyEmptyInit)
        assert_that(mapped_object.mapped_property).is_equal_to("some_valuesome_value_02")
        assert_that(mapped_object.unmapped_property2).is_equal_to("prefix_unmapped_value")

    def test_map_with_option_fail_on_get_attr(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomeProperty1).custom_mappings(
            {"non_existing_property": "some_property"}).options(MapperOptions.fail_on_get_attr == False)

        # when
        mapped_object = mapper.map(TestEmptyClass1())

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object.some_property).is_none()

        # given
        mapper_strict = OneWayMapper.for_target_class(TestClassSomeProperty1).custom_mappings(
            {"non_existing_property": "some_property"}).options(MapperOptions.fail_on_get_attr == True)

        # when
        with self.assertRaises(AttributeError) as context:
            mapper_strict.map(TestEmptyClass1())

        # then
        assert_that(context.exception.args[0]).contains("non_existing_property")

    def test_map_attr_name_for_empty_classes_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestEmptyClass1)

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property")

        # then
        assert_that(context.exception.args[0]).contains("unmapped_property")

    def test_map_attr_name_for_unmapped_explicit_property_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property")

        # then
        assert_that(context.exception.args[0]).contains("unmapped_property")

    def test_map_attr_name_for_opposite_way_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("mapped_property")

        # then
        assert_that(context.exception.args[0]).contains("mapped_property")

    def test_map_attr_name_for_explicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # then
        assert_that(mapper.map_attr_name("some_property")).is_equal_to("mapped_property")

    def test_map_attr_name_for_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # then
        assert_that(mapper.map_attr_name("some_property")).is_equal_to("some_property")
        assert_that(mapper.map_attr_name("some_property_02")).is_equal_to("some_property_02")
        assert_that(mapper.map_attr_name("some_property_03")).is_equal_to("some_property_03")

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property1")

        # then
        assert_that(context.exception.args[0]).contains("unmapped_property1")

    def test_for_target_class_when_object_passed_should_raise_exception(self):
        # when
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_class(object())

        # then
        assert_that(context.exception.args[0]).contains("object")

    def test_for_target_class(self):
        assert_that(OneWayMapper.for_target_class(object)).is_not_none()

    def test_for_target_prototype_when_class_passed_should_raise_exception(self):
        # when
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_prototype(object)

        # then
        assert_that(context.exception.args[0]).contains("object")

    def test_for_target_prototype(self):
        assert_that(OneWayMapper.for_target_prototype(object())).is_not_none()

    def test_map_attr_value_when_unknown_attr_name_should_raise_exception(self):

        # when
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).map_attr_value("unknown_attr", "some_value")

        # then
        assert_that(context.exception.args[0]).contains("unknown_attr")

    def test_map_attr_value_for_none_attr_name_should_raise_exception(self):

        # when
        with self.assertRaises(ValueError) as context:
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1).map_attr_value(None, "some_value")

        # then
        assert_that(context.exception.args[0]).contains("None")

    def test_map_attr_value_for_none_value(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1)

        # then
        assert_that(mapper.map_attr_value("some_property_02", None)).is_none()

    def test_map_attr_value_with_default_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1)

        # then
        assert_that(mapper.map_attr_value("some_property_02", "some_value")).is_equal_to("some_value")

    def test_map_attr_value_with_custom_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedPropertyEmptyInit).\
            custom_mappings({"some_property_02": "mapped_property_02"})

        # then
        assert_that(mapper.map_attr_value("some_property_02", "some_value")).is_equal_to("some_value")

    def test_map_different_source_dicts_less_attributes(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1)

        # when
        mapped_object = mapper.map(dict(some_property="some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        # when
        mapped_object = mapper.map(dict(some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

    def test_map_different_source_dicts_more_attributes(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit1)

        # when
        mapped_object = mapper.map(dict(some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        # when
        mapped_object = mapper.map(dict(some_property="some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

    def test_map_different_source_objects_less_attributes(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1("some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_02).is_none()
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        # when
        mapped_object = mapper.map(TestClassLessPropertiesEmptyInit1("some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

    def test_map_different_source_objects_more_attributes(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = mapper.map(TestClassLessPropertiesEmptyInit1("some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1("some_val", "some_val_02", "some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_02).is_equal_to("some_val_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

    def test_map_use_cached_source_attributes(self):
        # given
        get_attributes_func_mock = Mock(return_value=["some_property", "some_property_02", "some_property_03"])
        attributes_cache = AttributesCache(get_attributes_func=get_attributes_func_mock)

        mapper = OneWayMapper(TestClassSomePropertyEmptyInit2, attributes_cache_provider=lambda: attributes_cache)

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1("some_val", some_property_03="some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1("some_val", "some_val_02", "some_val_03"))

        # then
        assert_that(mapped_object.some_property).is_equal_to("some_val")
        assert_that(mapped_object.some_property_02).is_equal_to("some_val_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_val_03")

        get_attributes_func_mock.assert_called_once()
