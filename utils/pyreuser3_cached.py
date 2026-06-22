from __future__ import annotations

from pathlib import Path
from typing import Any

from pyreuser3.core import RSZ_MAGIC, USR_MAGIC
from pyreuser3.export import User3Exporter
from pyreuser3.pack import User3Packer


class CachedREUser3Converter:
    """Reuse PyREUser3 exporter metadata and schema across all user3 operations."""

    def __init__(
        self,
        schema_path: Path,
        il2cpp_dump_path: Path,
        tree_depth: int | str = "auto",
        user_magic: int = USR_MAGIC,
        rsz_magic: int = RSZ_MAGIC,
    ) -> None:
        self.schema_path = Path(schema_path)
        self.il2cpp_dump_path = Path(il2cpp_dump_path)
        self.user_magic = int(user_magic)
        self.rsz_magic = int(rsz_magic)
        self.exporter = User3Exporter(
            user3_root=Path.cwd(),
            schema_dir=self.schema_path,
            output_root=Path.cwd(),
            tree_depth=tree_depth,
            exclude_regexes=[],
            il2cpp_dump_path=self.il2cpp_dump_path,
            user_magic=self.user_magic,
            rsz_magic=self.rsz_magic,
        )
        self._prepare_exporter_metadata()
        self.packer = self._new_shared_packer()

    def readable(self, user3_path: Path, round_floats: bool = True) -> Any:
        tree = self.exporter._parse_user3(Path(user3_path))
        tree = self.exporter._postprocess_enum_nodes(tree)
        tree = self.exporter._finalize_export_tree(tree)
        if round_floats:
            return self.exporter._round_export_floats(tree)
        return tree

    def repack(self, user3_path: Path) -> Any:
        return self.exporter._parse_user3_pack(Path(user3_path))

    def pack(self, data: Any) -> bytes:
        return self.packer.pack(data)

    def _prepare_exporter_metadata(self) -> None:
        enums_internal, enum_context = self.exporter.export_il2cpp_metadata_from_path(
            self.il2cpp_dump_path
        )
        self.exporter.enum_lookup = self.exporter._build_enum_lookup_from_enums_internal(
            enums_internal
        )
        self.exporter._apply_enum_context(enum_context)
        self.exporter._ensure_enum_lookup()

    def _new_shared_packer(self) -> User3Packer:
        packer = User3Packer.__new__(User3Packer)
        packer.schema_path = self.exporter.schema_path
        packer.typedb = self.exporter.typedb
        packer.il2cpp_dump_path = None
        packer.output_root = Path.cwd()
        packer.user_magic = self.user_magic
        packer.rsz_magic = self.rsz_magic
        packer.enum_underlying_types = dict(self.exporter.enum_underlying_types)
        packer.enum_lookup = self.exporter.enum_lookup
        packer.member_lookup = packer._build_member_lookup()
        packer.instances = []
        return packer
