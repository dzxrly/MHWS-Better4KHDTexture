from __future__ import annotations

from typing import Any, Iterable


JsonDict = dict[str, Any]


def instances(data: JsonDict) -> JsonDict:
    value = data.get("_instances")
    if not isinstance(value, dict):
        raise ValueError("pack JSON is missing _instances")
    return value


def ref_id(ref: Any) -> int:
    if isinstance(ref, dict) and isinstance(ref.get("ref_instance_id"), int):
        return int(ref["ref_instance_id"])
    if isinstance(ref, int):
        return ref
    raise ValueError(f"expected ref_instance_id object, got {ref!r}")


def instance(data: JsonDict, ref: Any) -> JsonDict:
    idx = ref_id(ref)
    entry = instances(data).get(str(idx))
    if not isinstance(entry, dict):
        raise KeyError(f"instance {idx} not found")
    return entry


def fields(data: JsonDict, ref: Any) -> JsonDict:
    entry = instance(data, ref)
    value = entry.get("fields")
    if not isinstance(value, dict):
        raise ValueError(f"instance {ref_id(ref)} has no fields")
    return value


def root_instance(data: JsonDict, class_suffix: str) -> JsonDict:
    roots = data.get("_roots")
    if not isinstance(roots, list):
        raise ValueError("pack JSON is missing _roots")
    for root in roots:
        entry = instance(data, root)
        class_name = entry.get("_class")
        if isinstance(class_name, str) and class_name.endswith(class_suffix):
            return entry
    raise KeyError(f"root class not found: {class_suffix}")


def iter_ref_fields(data: JsonDict, refs: Any) -> Iterable[JsonDict]:
    if not isinstance(refs, list):
        raise ValueError(f"expected a list of refs, got {type(refs).__name__}")
    for ref in refs:
        yield fields(data, ref)


def set_field(
    target: JsonDict,
    name: str,
    value: Any,
    changes: list[str],
    context: str,
) -> None:
    old = target.get(name)
    if old != value:
        target[name] = value
        changes.append(f"{context}.{name}: {old!r} -> {value!r}")

