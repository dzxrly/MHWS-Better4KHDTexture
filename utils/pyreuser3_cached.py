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
        metadata = self._prepare_exporter_metadata()
        self.packer = self._new_shared_packer(metadata)

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

    def _prepare_exporter_metadata(self) -> tuple[dict, dict]:
        enums_internal, enum_context = self.exporter.export_il2cpp_metadata_from_path(
            self.il2cpp_dump_path
        )
        self.exporter.enum_lookup = (
            self.exporter._build_enum_lookup_from_enums_internal(enums_internal)
        )
        self.exporter._apply_enum_context(enum_context)
        self.exporter._ensure_enum_lookup()
        return enums_internal, enum_context

    def _new_shared_packer(self, metadata: tuple[dict, dict]) -> User3Packer:
        # Let PyREUser3 initialize all packing context from the same cached metadata.
        return User3Packer(
            schema_dir=self.exporter.schema_path,
            il2cpp_dump_path=self.il2cpp_dump_path,
            output_root=Path.cwd(),
            user_magic=self.user_magic,
            rsz_magic=self.rsz_magic,
            preloaded_typedb=self.exporter.typedb,
            preloaded_il2cpp_metadata=metadata,
        )
