from __future__ import annotations

import copy
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

from pyreuser3.export import User3Exporter
from pyreuser3.native_structs import NATIVE_STRUCT_CODECS
from pyreuser3.pack import User3Packer
from pyreuser3.pack.models import PackError
from pyreuser3.schema import ClassDef, FieldDef, TypeDB

from utils.pyreuser3_cached import CachedREUser3Converter


class CachedConverterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layouts = {
            codec.il2cpp_type: codec.descriptor() for codec in NATIVE_STRUCT_CODECS
        }
        self.metadata = (
            {"test.Flags": {"NONE": 0, "A": 1, "B": 2, "C": 4}},
            {
                "native_struct_layouts": self.layouts,
                "enum_underlying_types": {"test.Flags": "U32"},
                "bitset_rules": {"test.Bitset": "test.Flags"},
                "generic_scalar_rules": {"test.Scalar": "test.Flags"},
                "generic_container_rules": {
                    "test.Container": {
                        "param_type": "test.Param",
                        "enum_type": "test.Flags",
                    }
                },
            },
        )

    def _converter(self, metadata: tuple[dict, dict]) -> CachedREUser3Converter:
        # Replace only the expensive file reads; both constructors remain real.
        source = Path(__file__)
        typedb = TypeDB({})
        with (
            patch.object(User3Exporter, "_resolve_schema_path", return_value=source),
            patch.object(User3Packer, "_resolve_schema_path", return_value=source),
            patch.object(TypeDB, "load", return_value=typedb) as load_schema,
            patch.object(
                User3Exporter,
                "export_il2cpp_metadata_from_path",
                return_value=metadata,
            ) as load_metadata,
        ):
            converter = CachedREUser3Converter(source, source)
        load_schema.assert_called_once()
        load_metadata.assert_called_once_with(source)
        self.assertIs(converter.packer.typedb, converter.exporter.typedb)
        return converter

    def test_native_struct_values_use_validated_layouts(self) -> None:
        converter = self._converter(self.metadata)
        self.assertEqual(converter.packer.native_struct_layouts, self.layouts)
        values = {
            "via.Int2": ({"x": -3, "y": 5}, "<ii", (-3, 5)),
            "via.Uint2": ({"x": 3, "y": 4294967295}, "<II", (3, 4294967295)),
            "via.Range": ({"s": 0.5, "r": 2.0}, "<ff", (0.5, 2.0)),
            "via.RangeI": ({"s": -3, "r": 5}, "<ii", (-3, 5)),
            "via.Sphere": (
                {"pos": [1.0, 2.0, 3.0], "r": 4.0},
                "<ffff",
                (1.0, 2.0, 3.0, 4.0),
            ),
        }
        for type_name, (value, fmt, components) in values.items():
            with self.subTest(type_name=type_name):
                field = FieldDef(
                    "value",
                    type_name.split(".")[-1],
                    type_name,
                    struct.calcsize(fmt),
                    4,
                    False,
                )
                prepared = converter.packer._prepare_field_value(field, value)
                self.assertEqual(prepared.payload, struct.pack(fmt, *components))

    def test_enum_context_preserves_flags_and_generic_rules(self) -> None:
        converter = self._converter(self.metadata)
        packer = converter.packer
        self.assertEqual(packer.enum_lookup, converter.exporter.enum_lookup)
        self.assertEqual(packer.enum_underlying_types, {"test.Flags": "U32"})
        self.assertEqual(packer.bitset_rules, {"test.Bitset": "test.Flags"})
        self.assertEqual(
            packer.class_default_enums,
            {"test.Scalar": "test.Flags", "test.Param": "test.Flags"},
        )
        field = FieldDef("_Value", "U32", "System.UInt32", 4, 4, False)
        for class_name in ("test.Scalar", "test.Param"):
            with self.subTest(class_name=class_name):
                prepared = packer._prepare_fields(
                    ClassDef(class_name, 1, [field]), {"_Value": ["A", "B"]}
                )
                self.assertEqual(prepared, {"_Value": 3})

    def test_missing_or_invalid_layout_still_rejects_structured_value(self) -> None:
        for mode in ("missing", "invalid"):
            with self.subTest(mode=mode):
                metadata = copy.deepcopy(self.metadata)
                layouts = metadata[1]["native_struct_layouts"]
                if mode == "missing":
                    layouts.pop("via.Uint2")
                else:
                    layouts["via.Uint2"]["fields"][1]["offset"] = 8
                converter = self._converter(metadata)
                field = FieldDef("value", "Uint2", "via.Uint2", 8, 4, False)
                with self.assertRaisesRegex(PackError, "did not validate"):
                    converter.packer._prepare_field_value(field, {"x": 1, "y": 2})
                prepared = converter.packer._prepare_field_value(
                    field, {"raw": "0100000002000000"}
                )
                self.assertEqual(prepared.payload, struct.pack("<II", 1, 2))


if __name__ == "__main__":
    unittest.main()
