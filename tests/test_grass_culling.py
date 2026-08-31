from __future__ import annotations

import unittest

from utils import (
    GRASS_CULLING_STAGE_DATA_TARGETS,
    GRASS_CULLING_STAGE_ID_FIELD,
    GRASS_CULLING_MODE_FIELD,
    resolve_target_value,
)
from utils.enums import EnumLookup, enum_int, enum_u32
from utils.patches import patch_grass_culling
from utils.repack import iter_ref_fields, root_instance
from utils.verify import verify_grass_culling


class GrassCullingStageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.enums = EnumLookup(
            {
                "app.FieldDef.STAGE_Fixed": {
                    "ST101": 3068809728,
                    "ST102": 3435138240,
                    "ST103": 3043886080,
                }
            }
        )

    def test_patch_matches_stage_and_mode_after_reordering(self) -> None:
        data = self._make_repack_data()
        root_fields = root_instance(data, "GrassCullingSetting")["fields"]
        original_order = self._stage_identities(data, root_fields["_StageData"])

        patch_grass_culling(data, self.enums)

        self.assertEqual(verify_grass_culling(data, self.enums), [])
        self.assertEqual(
            self._stage_identities(data, root_fields["_StageData"]),
            original_order,
        )
        actual = {
            (
                enum_u32(entry[GRASS_CULLING_STAGE_ID_FIELD]),
                enum_int(entry[GRASS_CULLING_MODE_FIELD]),
            ): entry
            for entry in iter_ref_fields(data, root_fields["_StageData"])
        }
        for (stage_target, culling_mode), targets in (
            GRASS_CULLING_STAGE_DATA_TARGETS.items()
        ):
            identity = (
                enum_u32(resolve_target_value(stage_target, self.enums)),
                culling_mode,
            )
            entry = actual[identity]
            for field_name, expected in targets.items():
                self.assertEqual(entry[field_name], expected)

    def test_patch_rejects_duplicate_stage_identity(self) -> None:
        data = self._make_repack_data()
        root_fields = root_instance(data, "GrassCullingSetting")["fields"]
        entries = list(iter_ref_fields(data, root_fields["_StageData"]))
        entries[1][GRASS_CULLING_STAGE_ID_FIELD] = entries[0][
            GRASS_CULLING_STAGE_ID_FIELD
        ]
        entries[1][GRASS_CULLING_MODE_FIELD] = entries[0][GRASS_CULLING_MODE_FIELD]

        with self.assertRaisesRegex(ValueError, "duplicate"):
            patch_grass_culling(data, self.enums)
        self.assertEqual(root_fields["_InstanceNum"], 1)
        self.assertEqual(next(iter_ref_fields(data, root_fields["_Data"])), {})

    def _make_repack_data(self) -> dict:
        instances: dict[str, dict] = {
            "0": {
                "_class": "app.user_data.GrassCullingSetting",
                "fields": {
                    "_EnableDensityCulling": True,
                    "_InstanceNum": 1,
                    "_Data": [],
                    "_StageData": [],
                },
            }
        }
        root_fields = instances["0"]["fields"]
        next_id = 1
        for _ in range(4):
            instances[str(next_id)] = {"_class": "Data", "fields": {}}
            root_fields["_Data"].append({"ref_instance_id": next_id})
            next_id += 1

        stage_rows = list(GRASS_CULLING_STAGE_DATA_TARGETS)
        for stage_target, culling_mode in reversed(stage_rows):
            stage_id = resolve_target_value(stage_target, self.enums)
            instances[str(next_id)] = {
                "_class": "StageData",
                "fields": {
                    GRASS_CULLING_STAGE_ID_FIELD: self._as_signed_32(stage_id),
                    GRASS_CULLING_MODE_FIELD: culling_mode,
                },
            }
            root_fields["_StageData"].append({"ref_instance_id": next_id})
            next_id += 1
        return {
            "_roots": [{"ref_instance_id": 0}],
            "_instances": instances,
        }

    @staticmethod
    def _stage_identities(
        data: dict,
        refs: object,
    ) -> list[tuple[int | None, int | None]]:
        return [
            (
                enum_u32(entry.get(GRASS_CULLING_STAGE_ID_FIELD)),
                enum_int(entry.get(GRASS_CULLING_MODE_FIELD)),
            )
            for entry in iter_ref_fields(data, refs)
        ]

    @staticmethod
    def _as_signed_32(value: object) -> int:
        numeric = enum_int(value)
        if numeric is None:
            raise AssertionError(f"expected enum integer, got {value!r}")
        normalized = numeric & 0xFFFFFFFF
        return normalized - 0x100000000 if normalized >= 0x80000000 else normalized


if __name__ == "__main__":
    unittest.main()
