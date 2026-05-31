"""Naming and collection helpers for Molder V2 generated objects."""

ROOT_COLLECTION = "MOLDER_V2"
GUIDES_COLLECTION = "MOLDER_V2_GUIDES"
PREVIEW_COLLECTION = "MOLDER_V2_PREVIEW"
DEBUG_COLLECTION = "MOLDER_V2_DEBUG"
VALIDATED_COLLECTION = "MOLDER_V2_VALIDATED_STRATEGY"
CUT_GUIDE_PREFIX = "MOLDER_CUT_GUIDE"
PREVIEW_PREFIX = "MOLDER_PREVIEW"


def guide_name(index: int) -> str:
    return f"{CUT_GUIDE_PREFIX}_{index:02d}"


def is_molder_object(obj) -> bool:
    return bool(obj and obj.get("molder_v2_generated", False))
